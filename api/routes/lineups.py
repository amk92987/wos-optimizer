"""
Lineup routes for the API.
Handles lineup recommendations and saved lineups.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import User, UserProfile, UserHero
from api.routes.auth import get_current_user
from engine.recommendation_engine import get_engine
from engine.analyzers.lineup_builder import LINEUP_TEMPLATES

router = APIRouter()


class LineupHero(BaseModel):
    hero: str
    hero_class: str
    slot: str
    role: str
    is_lead: bool = False
    status: str = ""
    power: int = 0


class LineupResponse(BaseModel):
    game_mode: str
    heroes: List[LineupHero]
    troop_ratio: Dict[str, int]
    notes: str
    confidence: str
    recommended_to_get: List[dict] = []


class SavedLineup(BaseModel):
    id: int
    name: str
    game_mode: str
    heroes: List[LineupHero]
    troop_ratio: Dict[str, int]
    notes: Optional[str]
    created_at: datetime


class CreateLineupRequest(BaseModel):
    name: str
    game_mode: str
    heroes: List[dict]
    troop_ratio: Dict[str, int]
    notes: Optional[str] = None


class JoinerRecommendation(BaseModel):
    hero: Optional[str]
    status: str
    skill_level: Optional[int] = None
    max_skill: int = 5
    recommendation: str
    action: str
    critical_note: str


@router.get("/templates")
def get_lineup_templates():
    """Get all available lineup templates."""
    templates = {}
    for key, template in LINEUP_TEMPLATES.items():
        templates[key] = {
            "name": template.get("name", key),
            "troop_ratio": template.get("troop_ratio", {}),
            "notes": template.get("notes", ""),
            "key_heroes": template.get("key_heroes", []),
            "ratio_explanation": template.get("ratio_explanation", "")
        }
    return templates


@router.get("/build/{game_mode}", response_model=LineupResponse)
def build_lineup(
    game_mode: str,
    current_user: User = Depends(get_current_user)
):
    """Build a personalized lineup for a specific game mode."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Get user's heroes
        user_heroes = db.query(UserHero).filter(
            UserHero.profile_id == profile.id
        ).all()

        # Convert to dict format for engine
        heroes_dict = {}
        for uh in user_heroes:
            if uh.hero:
                heroes_dict[uh.hero.name] = {
                    'level': uh.level or 1,
                    'stars': uh.stars or 1,
                    'ascension_tier': getattr(uh, 'ascension_tier', 0) or 0,
                    'expedition_skill_1_level': getattr(uh, 'expedition_skill_1_level', 1) or 1,
                    'expedition_skill_2_level': getattr(uh, 'expedition_skill_2_level', 1) or 1,
                    'expedition_skill_3_level': getattr(uh, 'expedition_skill_3_level', 1) or 1,
                    'gear_slot1_quality': getattr(uh, 'gear_slot1_quality', 0) or 0,
                    'gear_slot1_level': getattr(uh, 'gear_slot1_level', 0) or 0,
                }

        # Get recommendation
        engine = get_engine()
        lineup = engine.lineup_builder.build_personalized_lineup(
            event_type=game_mode,
            user_heroes=heroes_dict,
            max_generation=99
        )

        return {
            "game_mode": lineup.game_mode,
            "heroes": lineup.heroes,
            "troop_ratio": lineup.troop_ratio,
            "notes": lineup.notes,
            "confidence": lineup.confidence,
            "recommended_to_get": lineup.recommended_to_get
        }

    finally:
        db.close()


@router.get("/build-all")
def build_all_lineups(current_user: User = Depends(get_current_user)):
    """Build personalized lineups for all game modes."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        user_heroes = db.query(UserHero).filter(
            UserHero.profile_id == profile.id
        ).all()

        heroes_dict = {}
        for uh in user_heroes:
            if uh.hero:
                heroes_dict[uh.hero.name] = {
                    'level': uh.level or 1,
                    'stars': uh.stars or 1,
                    'expedition_skill_1_level': getattr(uh, 'expedition_skill_1_level', 1) or 1,
                }

        engine = get_engine()
        lineups = engine.get_all_lineups(heroes_dict, profile)

        return lineups

    finally:
        db.close()


@router.get("/general/{game_mode}", response_model=LineupResponse)
def get_general_lineup(
    game_mode: str,
    max_generation: int = Query(8, ge=1, le=14)
):
    """Get general lineup recommendation (no login required)."""
    engine = get_engine()
    lineup = engine.lineup_builder.build_general_lineup(
        event_type=game_mode,
        max_generation=max_generation
    )

    return {
        "game_mode": lineup.game_mode,
        "heroes": lineup.heroes,
        "troop_ratio": lineup.troop_ratio,
        "notes": lineup.notes,
        "confidence": lineup.confidence,
        "recommended_to_get": lineup.recommended_to_get
    }


@router.get("/joiner/{attack_type}", response_model=JoinerRecommendation)
def get_joiner_recommendation(
    attack_type: str,
    current_user: User = Depends(get_current_user)
):
    """Get rally joiner recommendation (attack or defense)."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        user_heroes = db.query(UserHero).filter(
            UserHero.profile_id == profile.id
        ).all()

        heroes_dict = {}
        for uh in user_heroes:
            if uh.hero:
                heroes_dict[uh.hero.name] = {
                    'level': uh.level or 1,
                    'stars': uh.stars or 1,
                    'expedition_skill': getattr(uh, 'expedition_skill_1_level', 1) or 1,
                    'expedition_skill_1': getattr(uh, 'expedition_skill_1_level', 1) or 1,
                }

        engine = get_engine()
        is_attack = attack_type.lower() in ["attack", "offense", "true", "1"]
        recommendation = engine.get_joiner_recommendation(heroes_dict, is_attack)

        return recommendation

    finally:
        db.close()


@router.get("/template/{game_mode}")
def get_template_details(game_mode: str):
    """Get detailed template info including hero explanations."""
    template = LINEUP_TEMPLATES.get(game_mode)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template not found: {game_mode}")

    return {
        "name": template.get("name", game_mode),
        "slots": template.get("slots", []),
        "troop_ratio": template.get("troop_ratio", {}),
        "notes": template.get("notes", ""),
        "key_heroes": template.get("key_heroes", []),
        "hero_explanations": template.get("hero_explanations", {}),
        "ratio_explanation": template.get("ratio_explanation", ""),
        "sustain_heroes": template.get("sustain_heroes", {}),
        "joiner_warning": template.get("joiner_warning")
    }
