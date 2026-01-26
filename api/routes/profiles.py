"""
Profile routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db, get_or_create_profile
from database.models import User, UserProfile, UserHero, Hero
from api.routes.auth import get_current_user

router = APIRouter()


class ProfileResponse(BaseModel):
    id: int
    name: Optional[str]
    state_number: Optional[int]
    server_age_days: int
    furnace_level: int
    furnace_fc_level: Optional[str]
    spending_profile: str
    priority_focus: str
    alliance_role: str
    priority_svs: int
    priority_rally: int
    priority_castle_battle: int
    priority_exploration: int
    priority_gathering: int
    is_farm_account: bool


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    state_number: Optional[int] = None
    server_age_days: Optional[int] = None
    furnace_level: Optional[int] = None
    furnace_fc_level: Optional[str] = None
    spending_profile: Optional[str] = None
    priority_focus: Optional[str] = None
    alliance_role: Optional[str] = None
    priority_svs: Optional[int] = None
    priority_rally: Optional[int] = None
    priority_castle_battle: Optional[int] = None
    priority_exploration: Optional[int] = None
    priority_gathering: Optional[int] = None
    is_farm_account: Optional[bool] = None
    linked_main_profile_id: Optional[int] = None


class ProfileListResponse(BaseModel):
    id: int
    name: Optional[str]
    state_number: Optional[int]
    server_age_days: int
    furnace_level: int
    furnace_fc_level: Optional[str]
    spending_profile: str
    alliance_role: str
    is_farm_account: bool
    linked_main_profile_id: Optional[int]
    hero_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CreateProfileRequest(BaseModel):
    name: Optional[str] = None
    state_number: Optional[int] = None
    is_farm_account: bool = False


class DuplicateProfileRequest(BaseModel):
    name: str


@router.get("/current", response_model=ProfileResponse)
def get_current_profile(current_user: User = Depends(get_current_user)):
    """Get user's current profile."""
    init_db()
    db = get_db()

    profile = get_or_create_profile(db, current_user.id)

    result = {
        "id": profile.id,
        "name": profile.name,
        "state_number": profile.state_number,
        "server_age_days": profile.server_age_days,
        "furnace_level": profile.furnace_level,
        "furnace_fc_level": profile.furnace_fc_level,
        "spending_profile": profile.spending_profile or "f2p",
        "priority_focus": profile.priority_focus or "balanced_growth",
        "alliance_role": profile.alliance_role or "filler",
        "priority_svs": profile.priority_svs,
        "priority_rally": profile.priority_rally,
        "priority_castle_battle": profile.priority_castle_battle,
        "priority_exploration": profile.priority_exploration,
        "priority_gathering": profile.priority_gathering,
        "is_farm_account": profile.is_farm_account or False
    }

    db.close()
    return result


@router.put("/update", response_model=ProfileResponse)
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user's profile."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    result = {
        "id": profile.id,
        "name": profile.name,
        "state_number": profile.state_number,
        "server_age_days": profile.server_age_days,
        "furnace_level": profile.furnace_level,
        "furnace_fc_level": profile.furnace_fc_level,
        "spending_profile": profile.spending_profile or "f2p",
        "priority_focus": profile.priority_focus or "balanced_growth",
        "alliance_role": profile.alliance_role or "filler",
        "priority_svs": profile.priority_svs,
        "priority_rally": profile.priority_rally,
        "priority_castle_battle": profile.priority_castle_battle,
        "priority_exploration": profile.priority_exploration,
        "priority_gathering": profile.priority_gathering,
        "is_farm_account": profile.is_farm_account or False
    }

    db.close()
    return result


def get_profile_with_count(db, profile: UserProfile, active_profile_id: int) -> dict:
    """Helper to convert profile to response dict with hero count."""
    hero_count = db.query(UserHero).filter(UserHero.profile_id == profile.id).count()
    return {
        "id": profile.id,
        "name": profile.name,
        "state_number": profile.state_number,
        "server_age_days": profile.server_age_days,
        "furnace_level": profile.furnace_level,
        "furnace_fc_level": profile.furnace_fc_level,
        "spending_profile": profile.spending_profile or "f2p",
        "alliance_role": profile.alliance_role or "filler",
        "is_farm_account": profile.is_farm_account or False,
        "linked_main_profile_id": profile.linked_main_profile_id,
        "hero_count": hero_count,
        "is_active": profile.id == active_profile_id,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
        "deleted_at": profile.deleted_at,
    }


@router.get("/all", response_model=List[ProfileListResponse])
def get_all_profiles(current_user: User = Depends(get_current_user)):
    """Get all profiles for the current user (excluding soft-deleted)."""
    init_db()
    db = get_db()

    try:
        # Get active profile ID
        active_profile = get_or_create_profile(db, current_user.id)
        active_id = active_profile.id

        # Get all non-deleted profiles
        profiles = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id,
            UserProfile.deleted_at.is_(None)
        ).order_by(UserProfile.is_farm_account, UserProfile.name).all()

        return [get_profile_with_count(db, p, active_id) for p in profiles]
    finally:
        db.close()


@router.get("/deleted", response_model=List[ProfileListResponse])
def get_deleted_profiles(current_user: User = Depends(get_current_user)):
    """Get soft-deleted profiles for the current user."""
    init_db()
    db = get_db()

    try:
        profiles = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id,
            UserProfile.deleted_at.isnot(None)
        ).order_by(UserProfile.deleted_at.desc()).all()

        return [get_profile_with_count(db, p, -1) for p in profiles]
    finally:
        db.close()


@router.post("", response_model=ProfileListResponse)
def create_profile(
    request: CreateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new profile."""
    init_db()
    db = get_db()

    try:
        new_profile = UserProfile(
            user_id=current_user.id,
            name=request.name,
            state_number=request.state_number,
            is_farm_account=request.is_farm_account,
            furnace_level=1,
            server_age_days=0,
            spending_profile="f2p",
            alliance_role="filler"
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        return get_profile_with_count(db, new_profile, new_profile.id)
    finally:
        db.close()


@router.get("/{profile_id}", response_model=ProfileListResponse)
def get_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific profile."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        active_profile = get_or_create_profile(db, current_user.id)
        return get_profile_with_count(db, profile, active_profile.id)
    finally:
        db.close()


@router.put("/{profile_id}", response_model=ProfileListResponse)
def update_profile_by_id(
    profile_id: int,
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a specific profile."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Update fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(profile, field, value)

        db.commit()
        db.refresh(profile)

        active_profile = get_or_create_profile(db, current_user.id)
        return get_profile_with_count(db, profile, active_profile.id)
    finally:
        db.close()


@router.delete("/{profile_id}")
def delete_profile(
    profile_id: int,
    hard: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Delete a profile (soft delete by default, hard delete if specified)."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Check if this is the active profile
        active_profile = get_or_create_profile(db, current_user.id)
        if profile.id == active_profile.id:
            raise HTTPException(status_code=400, detail="Cannot delete active profile. Switch to another profile first.")

        # Check if test account - always hard delete
        is_test = current_user.is_test_account

        if hard or is_test:
            # Hard delete
            db.query(UserHero).filter(UserHero.profile_id == profile_id).delete()
            db.delete(profile)
            db.commit()
            return {"status": "deleted", "permanent": True}
        else:
            # Soft delete
            profile.deleted_at = datetime.utcnow()
            db.commit()
            return {"status": "deleted", "permanent": False}
    finally:
        db.close()


@router.post("/{profile_id}/activate")
def activate_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user)
):
    """Set a profile as the active profile."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id,
            UserProfile.deleted_at.is_(None)
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Mark this as the default profile (for session tracking)
        # Unmark all other profiles first
        db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).update({"is_default": False})

        profile.is_default = True
        db.commit()

        return {"status": "activated", "profile_id": profile_id}
    finally:
        db.close()


@router.post("/{profile_id}/duplicate", response_model=ProfileListResponse)
def duplicate_profile(
    profile_id: int,
    request: DuplicateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """Duplicate a profile with all its heroes."""
    init_db()
    db = get_db()

    try:
        original = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id
        ).first()

        if not original:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Create new profile with same settings
        new_profile = UserProfile(
            user_id=original.user_id,
            name=request.name,
            state_number=original.state_number,
            server_age_days=original.server_age_days,
            furnace_level=original.furnace_level,
            furnace_fc_level=original.furnace_fc_level,
            spending_profile=original.spending_profile,
            priority_focus=original.priority_focus,
            alliance_role=original.alliance_role,
            is_farm_account=False,  # Don't copy farm status
            priority_svs=original.priority_svs,
            priority_rally=original.priority_rally,
            priority_castle_battle=original.priority_castle_battle,
            priority_exploration=original.priority_exploration,
            priority_gathering=original.priority_gathering,
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        # Copy all heroes
        original_heroes = db.query(UserHero).filter(UserHero.profile_id == profile_id).all()
        for hero in original_heroes:
            new_hero = UserHero(
                profile_id=new_profile.id,
                hero_id=hero.hero_id,
                level=hero.level,
                stars=hero.stars,
                ascension_tier=hero.ascension_tier,
                exploration_skill_1_level=hero.exploration_skill_1_level,
                exploration_skill_2_level=hero.exploration_skill_2_level,
                exploration_skill_3_level=hero.exploration_skill_3_level,
                expedition_skill_1_level=hero.expedition_skill_1_level,
                expedition_skill_2_level=hero.expedition_skill_2_level,
                expedition_skill_3_level=hero.expedition_skill_3_level,
                gear_slot1_quality=hero.gear_slot1_quality,
                gear_slot1_level=hero.gear_slot1_level,
                gear_slot1_mastery=hero.gear_slot1_mastery,
                gear_slot2_quality=hero.gear_slot2_quality,
                gear_slot2_level=hero.gear_slot2_level,
                gear_slot2_mastery=hero.gear_slot2_mastery,
                gear_slot3_quality=hero.gear_slot3_quality,
                gear_slot3_level=hero.gear_slot3_level,
                gear_slot3_mastery=hero.gear_slot3_mastery,
                gear_slot4_quality=hero.gear_slot4_quality,
                gear_slot4_level=hero.gear_slot4_level,
                gear_slot4_mastery=hero.gear_slot4_mastery,
                mythic_gear_unlocked=hero.mythic_gear_unlocked,
                mythic_gear_quality=hero.mythic_gear_quality,
                mythic_gear_level=hero.mythic_gear_level,
                mythic_gear_mastery=hero.mythic_gear_mastery,
            )
            db.add(new_hero)

        db.commit()

        return get_profile_with_count(db, new_profile, new_profile.id)
    finally:
        db.close()


@router.post("/{profile_id}/restore")
def restore_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user)
):
    """Restore a soft-deleted profile."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id,
            UserProfile.deleted_at.isnot(None)
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Deleted profile not found")

        profile.deleted_at = None
        db.commit()

        return {"status": "restored", "profile_id": profile_id}
    finally:
        db.close()


@router.get("/{profile_id}/preview")
def preview_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get profile preview with hero list."""
    init_db()
    db = get_db()

    try:
        profile = db.query(UserProfile).filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Get heroes with hero names
        heroes = db.query(UserHero, Hero).join(Hero).filter(
            UserHero.profile_id == profile_id
        ).order_by(Hero.generation, Hero.name).all()

        hero_list = [
            {
                "name": hero.name,
                "level": uh.level,
                "stars": uh.stars,
                "generation": hero.generation,
                "hero_class": hero.hero_class,
            }
            for uh, hero in heroes
        ]

        return {
            "id": profile.id,
            "name": profile.name,
            "state_number": profile.state_number,
            "server_age_days": profile.server_age_days,
            "furnace_level": profile.furnace_level,
            "furnace_fc_level": profile.furnace_fc_level,
            "spending_profile": profile.spending_profile or "f2p",
            "alliance_role": profile.alliance_role or "filler",
            "is_farm_account": profile.is_farm_account or False,
            "linked_main_profile_id": profile.linked_main_profile_id,
            "heroes": hero_list,
        }
    finally:
        db.close()
