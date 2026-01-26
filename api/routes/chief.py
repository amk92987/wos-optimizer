"""
Chief Gear and Charms routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import User, UserProfile, UserChiefGear, UserChiefCharm
from api.routes.auth import get_current_user

router = APIRouter()


class ChiefGearResponse(BaseModel):
    id: int
    profile_id: int
    helmet_quality: int
    helmet_level: int
    armor_quality: int
    armor_level: int
    gloves_quality: int
    gloves_level: int
    boots_quality: int
    boots_level: int
    ring_quality: int
    ring_level: int
    amulet_quality: int
    amulet_level: int


class UpdateChiefGearRequest(BaseModel):
    helmet_quality: Optional[int] = None
    helmet_level: Optional[int] = None
    armor_quality: Optional[int] = None
    armor_level: Optional[int] = None
    gloves_quality: Optional[int] = None
    gloves_level: Optional[int] = None
    boots_quality: Optional[int] = None
    boots_level: Optional[int] = None
    ring_quality: Optional[int] = None
    ring_level: Optional[int] = None
    amulet_quality: Optional[int] = None
    amulet_level: Optional[int] = None


class ChiefCharmResponse(BaseModel):
    id: int
    profile_id: int
    # Cap slots (Keenness - Lancer)
    cap_slot_1: str
    cap_slot_2: str
    cap_slot_3: str
    # Watch slots (Keenness - Lancer)
    watch_slot_1: str
    watch_slot_2: str
    watch_slot_3: str
    # Coat slots (Protection - Infantry)
    coat_slot_1: str
    coat_slot_2: str
    coat_slot_3: str
    # Pants slots (Protection - Infantry)
    pants_slot_1: str
    pants_slot_2: str
    pants_slot_3: str
    # Belt slots (Vision - Marksman)
    belt_slot_1: str
    belt_slot_2: str
    belt_slot_3: str
    # Weapon slots (Vision - Marksman)
    weapon_slot_1: str
    weapon_slot_2: str
    weapon_slot_3: str


class UpdateChiefCharmRequest(BaseModel):
    cap_slot_1: Optional[str] = None
    cap_slot_2: Optional[str] = None
    cap_slot_3: Optional[str] = None
    watch_slot_1: Optional[str] = None
    watch_slot_2: Optional[str] = None
    watch_slot_3: Optional[str] = None
    coat_slot_1: Optional[str] = None
    coat_slot_2: Optional[str] = None
    coat_slot_3: Optional[str] = None
    pants_slot_1: Optional[str] = None
    pants_slot_2: Optional[str] = None
    pants_slot_3: Optional[str] = None
    belt_slot_1: Optional[str] = None
    belt_slot_2: Optional[str] = None
    belt_slot_3: Optional[str] = None
    weapon_slot_1: Optional[str] = None
    weapon_slot_2: Optional[str] = None
    weapon_slot_3: Optional[str] = None


def get_or_create_chief_gear(db, profile_id: int) -> UserChiefGear:
    """Get or create chief gear for a profile."""
    gear = db.query(UserChiefGear).filter(
        UserChiefGear.profile_id == profile_id
    ).first()

    if not gear:
        gear = UserChiefGear(profile_id=profile_id)
        db.add(gear)
        db.commit()
        db.refresh(gear)

    return gear


def get_or_create_chief_charms(db, profile_id: int) -> UserChiefCharm:
    """Get or create chief charms for a profile."""
    charms = db.query(UserChiefCharm).filter(
        UserChiefCharm.profile_id == profile_id
    ).first()

    if not charms:
        charms = UserChiefCharm(profile_id=profile_id)
        db.add(charms)
        db.commit()
        db.refresh(charms)

    return charms


@router.get("/gear", response_model=ChiefGearResponse)
def get_chief_gear(current_user: User = Depends(get_current_user)):
    """Get user's chief gear."""
    init_db()
    db = get_db()

    # Get user's current profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Profile not found")

    gear = get_or_create_chief_gear(db, profile.id)

    result = {
        "id": gear.id,
        "profile_id": gear.profile_id,
        "helmet_quality": gear.helmet_quality or 1,
        "helmet_level": gear.helmet_level or 1,
        "armor_quality": gear.armor_quality or 1,
        "armor_level": gear.armor_level or 1,
        "gloves_quality": gear.gloves_quality or 1,
        "gloves_level": gear.gloves_level or 1,
        "boots_quality": gear.boots_quality or 1,
        "boots_level": gear.boots_level or 1,
        "ring_quality": gear.ring_quality or 1,
        "ring_level": gear.ring_level or 1,
        "amulet_quality": gear.amulet_quality or 1,
        "amulet_level": gear.amulet_level or 1,
    }

    db.close()
    return result


@router.put("/gear", response_model=ChiefGearResponse)
def update_chief_gear(
    request: UpdateChiefGearRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user's chief gear."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Profile not found")

    gear = get_or_create_chief_gear(db, profile.id)

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(gear, field, value)

    db.commit()
    db.refresh(gear)

    result = {
        "id": gear.id,
        "profile_id": gear.profile_id,
        "helmet_quality": gear.helmet_quality or 1,
        "helmet_level": gear.helmet_level or 1,
        "armor_quality": gear.armor_quality or 1,
        "armor_level": gear.armor_level or 1,
        "gloves_quality": gear.gloves_quality or 1,
        "gloves_level": gear.gloves_level or 1,
        "boots_quality": gear.boots_quality or 1,
        "boots_level": gear.boots_level or 1,
        "ring_quality": gear.ring_quality or 1,
        "ring_level": gear.ring_level or 1,
        "amulet_quality": gear.amulet_quality or 1,
        "amulet_level": gear.amulet_level or 1,
    }

    db.close()
    return result


@router.get("/charms", response_model=ChiefCharmResponse)
def get_chief_charms(current_user: User = Depends(get_current_user)):
    """Get user's chief charms."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Profile not found")

    charms = get_or_create_chief_charms(db, profile.id)

    result = {
        "id": charms.id,
        "profile_id": charms.profile_id,
        "cap_slot_1": charms.cap_slot_1 or "1",
        "cap_slot_2": charms.cap_slot_2 or "1",
        "cap_slot_3": charms.cap_slot_3 or "1",
        "watch_slot_1": charms.watch_slot_1 or "1",
        "watch_slot_2": charms.watch_slot_2 or "1",
        "watch_slot_3": charms.watch_slot_3 or "1",
        "coat_slot_1": charms.coat_slot_1 or "1",
        "coat_slot_2": charms.coat_slot_2 or "1",
        "coat_slot_3": charms.coat_slot_3 or "1",
        "pants_slot_1": charms.pants_slot_1 or "1",
        "pants_slot_2": charms.pants_slot_2 or "1",
        "pants_slot_3": charms.pants_slot_3 or "1",
        "belt_slot_1": charms.belt_slot_1 or "1",
        "belt_slot_2": charms.belt_slot_2 or "1",
        "belt_slot_3": charms.belt_slot_3 or "1",
        "weapon_slot_1": charms.weapon_slot_1 or "1",
        "weapon_slot_2": charms.weapon_slot_2 or "1",
        "weapon_slot_3": charms.weapon_slot_3 or "1",
    }

    db.close()
    return result


@router.put("/charms", response_model=ChiefCharmResponse)
def update_chief_charms(
    request: UpdateChiefCharmRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user's chief charms."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Profile not found")

    charms = get_or_create_chief_charms(db, profile.id)

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(charms, field, value)

    db.commit()
    db.refresh(charms)

    result = {
        "id": charms.id,
        "profile_id": charms.profile_id,
        "cap_slot_1": charms.cap_slot_1 or "1",
        "cap_slot_2": charms.cap_slot_2 or "1",
        "cap_slot_3": charms.cap_slot_3 or "1",
        "watch_slot_1": charms.watch_slot_1 or "1",
        "watch_slot_2": charms.watch_slot_2 or "1",
        "watch_slot_3": charms.watch_slot_3 or "1",
        "coat_slot_1": charms.coat_slot_1 or "1",
        "coat_slot_2": charms.coat_slot_2 or "1",
        "coat_slot_3": charms.coat_slot_3 or "1",
        "pants_slot_1": charms.pants_slot_1 or "1",
        "pants_slot_2": charms.pants_slot_2 or "1",
        "pants_slot_3": charms.pants_slot_3 or "1",
        "belt_slot_1": charms.belt_slot_1 or "1",
        "belt_slot_2": charms.belt_slot_2 or "1",
        "belt_slot_3": charms.belt_slot_3 or "1",
        "weapon_slot_1": charms.weapon_slot_1 or "1",
        "weapon_slot_2": charms.weapon_slot_2 or "1",
        "weapon_slot_3": charms.weapon_slot_3 or "1",
    }

    db.close()
    return result
