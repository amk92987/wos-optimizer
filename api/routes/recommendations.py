"""
Recommendations routes for the API.
Uses the recommendation engine to provide personalized upgrade suggestions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import User, UserProfile, UserHero, UserChiefGear, UserChiefCharm
from api.routes.auth import get_current_user
from engine.recommendation_engine import RecommendationEngine, get_engine

router = APIRouter()


class RecommendationResponse(BaseModel):
    priority: int
    action: str
    category: str
    hero: Optional[str]
    reason: str
    resources: str
    relevance_tags: List[str]
    source: str


class InvestmentRecommendation(BaseModel):
    hero: str
    hero_class: str
    tier: str
    generation: int
    current_level: int
    target_level: int
    current_stars: int
    target_stars: int
    reason: str
    priority: int


class PhaseInfo(BaseModel):
    phase_id: str
    phase_name: str
    focus_areas: List[str]
    common_mistakes: List[str]
    bottlenecks: List[str]
    next_milestone: Optional[dict]


@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    include_power: bool = Query(True),
    current_user: User = Depends(get_current_user)
):
    """Get personalized upgrade recommendations."""
    init_db()
    db = get_db()

    try:
        # Get user's profile
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Get user's heroes
        user_heroes = db.query(UserHero).filter(
            UserHero.profile_id == profile.id
        ).all()

        # Get user's gear and charms
        user_gear = db.query(UserChiefGear).filter(
            UserChiefGear.profile_id == profile.id
        ).all()

        user_charms = db.query(UserChiefCharm).filter(
            UserChiefCharm.profile_id == profile.id
        ).all()

        # Get recommendations from engine
        engine = get_engine()
        recommendations = engine.get_recommendations(
            profile=profile,
            user_heroes=user_heroes,
            user_gear=user_gear,
            user_charms=user_charms,
            limit=limit,
            include_power=include_power
        )

        # Convert to response format
        result = []
        for rec in recommendations:
            result.append({
                "priority": rec.priority,
                "action": rec.action,
                "category": rec.category,
                "hero": rec.hero,
                "reason": rec.reason,
                "resources": rec.resources,
                "relevance_tags": rec.relevance_tags,
                "source": rec.source
            })

        return result

    finally:
        db.close()


@router.get("/investments", response_model=List[InvestmentRecommendation])
def get_investment_recommendations(
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """Get hero investment recommendations based on spending profile."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Get user's heroes with their static data
        user_heroes = db.query(UserHero).filter(
            UserHero.profile_id == profile.id
        ).all()

        engine = get_engine()
        hero_analyzer = engine.hero_analyzer

        # Get spending profile to determine investment strategy
        spending = profile.spending_profile or "f2p"

        # Investment targets based on spending
        investment_limits = {
            "f2p": 3,
            "minnow": 4,
            "dolphin": 6,
            "orca": 8,
            "whale": 10
        }
        max_heroes = investment_limits.get(spending, 5)

        # Analyze heroes and build investment list
        investments = []
        for uh in user_heroes:
            if not uh.hero:
                continue

            hero = uh.hero
            tier = hero.tier_overall or "C"
            gen = hero.generation or 1

            # Skip low-tier heroes for investment
            if tier in ["C", "D"] and spending in ["f2p", "minnow"]:
                continue

            # Calculate target levels based on spending
            current_level = uh.level or 1
            current_stars = uh.stars or 0

            # Target based on tier and spending
            if tier in ["S+", "S"]:
                target_level = 80 if spending in ["whale", "orca"] else 60
                target_stars = 5 if spending in ["whale", "orca"] else 4
            elif tier == "A":
                target_level = 60 if spending in ["whale", "orca", "dolphin"] else 50
                target_stars = 4 if spending in ["whale", "orca"] else 3
            else:
                target_level = 50
                target_stars = 3

            # Skip if already at target
            if current_level >= target_level and current_stars >= target_stars:
                continue

            # Calculate priority (lower = higher priority)
            tier_priority = {"S+": 1, "S": 2, "A": 3, "B": 4, "C": 5, "D": 6}
            priority = tier_priority.get(tier, 5) + (gen // 3)

            reason = f"{tier} tier hero"
            if gen <= 3:
                reason += " (easily obtainable)"
            elif gen >= 10:
                reason += " (latest generation)"

            investments.append({
                "hero": hero.name,
                "hero_class": hero.hero_class or "Unknown",
                "tier": tier,
                "generation": gen,
                "current_level": current_level,
                "target_level": target_level,
                "current_stars": current_stars,
                "target_stars": target_stars,
                "reason": reason,
                "priority": priority
            })

        # Sort by priority and limit
        investments.sort(key=lambda x: x["priority"])
        return investments[:limit]

    finally:
        db.close()


@router.get("/phase", response_model=PhaseInfo)
def get_phase_info(current_user: User = Depends(get_current_user)):
    """Get current game phase and progression info."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        engine = get_engine()
        phase_info = engine.get_phase_info(profile)

        return phase_info

    finally:
        db.close()


@router.get("/gear-priority")
def get_gear_priority(current_user: User = Depends(get_current_user)):
    """Get gear upgrade priority order."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        spending = profile.spending_profile if profile else "f2p"

        engine = get_engine()
        priority = engine.get_gear_priority(spending)

        return {"spending_profile": spending, "priority": priority}

    finally:
        db.close()
