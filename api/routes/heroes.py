"""
Hero routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import sys
import json
import base64

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import User, UserProfile, UserHero, Hero
from api.routes.auth import get_current_user

router = APIRouter()


class HeroBase(BaseModel):
    id: int
    name: str
    generation: int
    hero_class: str
    tier_overall: Optional[str]
    tier_expedition: Optional[str]
    tier_exploration: Optional[str]
    image_filename: Optional[str]
    image_base64: Optional[str] = None


class UserHeroData(BaseModel):
    hero_id: int
    name: str
    generation: int
    hero_class: str
    tier_overall: Optional[str]
    level: int
    stars: int
    ascension: int
    # Skill levels
    exploration_skill_1: int
    exploration_skill_2: int
    exploration_skill_3: int
    expedition_skill_1: int
    expedition_skill_2: int
    expedition_skill_3: int
    # Skill names (from heroes.json)
    exploration_skill_1_name: Optional[str] = None
    exploration_skill_2_name: Optional[str] = None
    exploration_skill_3_name: Optional[str] = None
    expedition_skill_1_name: Optional[str] = None
    expedition_skill_2_name: Optional[str] = None
    expedition_skill_3_name: Optional[str] = None
    # Skill descriptions
    exploration_skill_1_desc: Optional[str] = None
    exploration_skill_2_desc: Optional[str] = None
    exploration_skill_3_desc: Optional[str] = None
    expedition_skill_1_desc: Optional[str] = None
    expedition_skill_2_desc: Optional[str] = None
    expedition_skill_3_desc: Optional[str] = None
    # Gear slots (4 slots)
    gear_slot1_quality: int = 0
    gear_slot1_level: int = 0
    gear_slot1_mastery: int = 0
    gear_slot2_quality: int = 0
    gear_slot2_level: int = 0
    gear_slot2_mastery: int = 0
    gear_slot3_quality: int = 0
    gear_slot3_level: int = 0
    gear_slot3_mastery: int = 0
    gear_slot4_quality: int = 0
    gear_slot4_level: int = 0
    gear_slot4_mastery: int = 0
    # Mythic/Exclusive gear
    mythic_gear_name: Optional[str] = None
    mythic_gear_unlocked: bool = False
    mythic_gear_quality: int = 0
    mythic_gear_level: int = 0
    mythic_gear_mastery: int = 0
    # Image
    image_base64: Optional[str] = None


class UpdateHeroRequest(BaseModel):
    level: Optional[int] = None
    stars: Optional[int] = None
    ascension: Optional[int] = None
    exploration_skill_1: Optional[int] = None
    exploration_skill_2: Optional[int] = None
    exploration_skill_3: Optional[int] = None
    expedition_skill_1: Optional[int] = None
    expedition_skill_2: Optional[int] = None
    expedition_skill_3: Optional[int] = None
    # Gear
    gear_slot1_quality: Optional[int] = None
    gear_slot1_level: Optional[int] = None
    gear_slot1_mastery: Optional[int] = None
    gear_slot2_quality: Optional[int] = None
    gear_slot2_level: Optional[int] = None
    gear_slot2_mastery: Optional[int] = None
    gear_slot3_quality: Optional[int] = None
    gear_slot3_level: Optional[int] = None
    gear_slot3_mastery: Optional[int] = None
    gear_slot4_quality: Optional[int] = None
    gear_slot4_level: Optional[int] = None
    gear_slot4_mastery: Optional[int] = None
    # Mythic
    mythic_gear_unlocked: Optional[bool] = None
    mythic_gear_quality: Optional[int] = None
    mythic_gear_level: Optional[int] = None
    mythic_gear_mastery: Optional[int] = None


def get_hero_image_base64(image_filename: str) -> Optional[str]:
    """Load hero image and convert to base64."""
    if not image_filename:
        return None

    image_path = PROJECT_ROOT / "assets" / "heroes" / image_filename
    if not image_path.exists():
        return None

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
            ext = image_path.suffix.lower()
            mime = "image/png" if ext == ".png" else "image/jpeg"
            return f"data:{mime};base64,{base64.b64encode(image_data).decode()}"
    except Exception:
        return None


@router.get("/all", response_model=List[HeroBase])
def get_all_heroes(include_images: bool = False):
    """Get all heroes from the game data."""
    heroes_path = PROJECT_ROOT / "data" / "heroes.json"

    if not heroes_path.exists():
        raise HTTPException(status_code=500, detail="Heroes data not found")

    with open(heroes_path, encoding="utf-8") as f:
        data = json.load(f)

    heroes = []
    for h in data.get("heroes", []):
        hero = {
            "id": h.get("id"),
            "name": h.get("name"),
            "generation": h.get("generation"),
            "hero_class": h.get("hero_class"),
            "tier_overall": h.get("tier_overall"),
            "tier_expedition": h.get("tier_expedition"),
            "tier_exploration": h.get("tier_exploration"),
            "image_filename": h.get("image_filename"),
            "image_base64": None
        }

        if include_images:
            hero["image_base64"] = get_hero_image_base64(h.get("image_filename"))

        heroes.append(hero)

    return heroes


def load_heroes_json():
    """Load heroes.json data for skill names and mythic gear info."""
    heroes_path = PROJECT_ROOT / "data" / "heroes.json"
    if heroes_path.exists():
        with open(heroes_path, encoding="utf-8") as f:
            data = json.load(f)
        return {h["name"]: h for h in data.get("heroes", [])}
    return {}


@router.get("/owned", response_model=List[UserHeroData])
def get_owned_heroes(
    include_images: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Get user's owned heroes."""
    init_db()
    db = get_db()

    # Get user's active profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        return []

    # Load heroes.json for skill names
    heroes_json = load_heroes_json()

    # Get owned heroes with hero details
    user_heroes = db.query(UserHero, Hero).join(
        Hero, UserHero.hero_id == Hero.id
    ).filter(
        UserHero.profile_id == profile.id
    ).all()

    result = []
    for uh, hero in user_heroes:
        # Get skill names and descriptions from heroes.json
        hero_data = heroes_json.get(hero.name, {})

        data = {
            "hero_id": hero.id,
            "name": hero.name,
            "generation": hero.generation,
            "hero_class": hero.hero_class,
            "tier_overall": hero.tier_overall,
            "level": uh.level,
            "stars": uh.stars,
            "ascension": getattr(uh, 'ascension_tier', uh.ascension) if hasattr(uh, 'ascension_tier') else uh.ascension,
            # Skill levels
            "exploration_skill_1": getattr(uh, 'exploration_skill_1_level', uh.exploration_skill_1) if hasattr(uh, 'exploration_skill_1_level') else uh.exploration_skill_1,
            "exploration_skill_2": getattr(uh, 'exploration_skill_2_level', uh.exploration_skill_2) if hasattr(uh, 'exploration_skill_2_level') else uh.exploration_skill_2,
            "exploration_skill_3": getattr(uh, 'exploration_skill_3_level', uh.exploration_skill_3) if hasattr(uh, 'exploration_skill_3_level') else uh.exploration_skill_3,
            "expedition_skill_1": getattr(uh, 'expedition_skill_1_level', uh.expedition_skill_1) if hasattr(uh, 'expedition_skill_1_level') else uh.expedition_skill_1,
            "expedition_skill_2": getattr(uh, 'expedition_skill_2_level', uh.expedition_skill_2) if hasattr(uh, 'expedition_skill_2_level') else uh.expedition_skill_2,
            "expedition_skill_3": getattr(uh, 'expedition_skill_3_level', uh.expedition_skill_3) if hasattr(uh, 'expedition_skill_3_level') else uh.expedition_skill_3,
            # Skill names from heroes.json
            "exploration_skill_1_name": hero_data.get("exploration_skill_1"),
            "exploration_skill_2_name": hero_data.get("exploration_skill_2"),
            "exploration_skill_3_name": hero_data.get("exploration_skill_3"),
            "expedition_skill_1_name": hero_data.get("expedition_skill_1"),
            "expedition_skill_2_name": hero_data.get("expedition_skill_2"),
            "expedition_skill_3_name": hero_data.get("expedition_skill_3"),
            # Skill descriptions
            "exploration_skill_1_desc": hero_data.get("exploration_skill_1_desc"),
            "exploration_skill_2_desc": hero_data.get("exploration_skill_2_desc"),
            "exploration_skill_3_desc": hero_data.get("exploration_skill_3_desc"),
            "expedition_skill_1_desc": hero_data.get("expedition_skill_1_desc"),
            "expedition_skill_2_desc": hero_data.get("expedition_skill_2_desc"),
            "expedition_skill_3_desc": hero_data.get("expedition_skill_3_desc"),
            # Gear slots
            "gear_slot1_quality": getattr(uh, 'gear_slot1_quality', 0) or 0,
            "gear_slot1_level": getattr(uh, 'gear_slot1_level', 0) or 0,
            "gear_slot1_mastery": getattr(uh, 'gear_slot1_mastery', 0) or 0,
            "gear_slot2_quality": getattr(uh, 'gear_slot2_quality', 0) or 0,
            "gear_slot2_level": getattr(uh, 'gear_slot2_level', 0) or 0,
            "gear_slot2_mastery": getattr(uh, 'gear_slot2_mastery', 0) or 0,
            "gear_slot3_quality": getattr(uh, 'gear_slot3_quality', 0) or 0,
            "gear_slot3_level": getattr(uh, 'gear_slot3_level', 0) or 0,
            "gear_slot3_mastery": getattr(uh, 'gear_slot3_mastery', 0) or 0,
            "gear_slot4_quality": getattr(uh, 'gear_slot4_quality', 0) or 0,
            "gear_slot4_level": getattr(uh, 'gear_slot4_level', 0) or 0,
            "gear_slot4_mastery": getattr(uh, 'gear_slot4_mastery', 0) or 0,
            # Mythic gear
            "mythic_gear_name": hero_data.get("mythic_gear"),
            "mythic_gear_unlocked": getattr(uh, 'mythic_gear_unlocked', False) or False,
            "mythic_gear_quality": getattr(uh, 'mythic_gear_quality', 0) or 0,
            "mythic_gear_level": getattr(uh, 'mythic_gear_level', 0) or 0,
            "mythic_gear_mastery": getattr(uh, 'mythic_gear_mastery', 0) or 0,
            "image_base64": None
        }

        if include_images:
            data["image_base64"] = get_hero_image_base64(hero.image_filename)

        result.append(data)

    db.close()
    return result


@router.post("/own/{hero_id}")
def add_owned_hero(
    hero_id: int,
    current_user: User = Depends(get_current_user)
):
    """Add a hero to user's owned list."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=400, detail="No profile found")

    # Check if already owned
    existing = db.query(UserHero).filter(
        UserHero.profile_id == profile.id,
        UserHero.hero_id == hero_id
    ).first()

    if existing:
        db.close()
        return {"message": "Hero already owned", "hero_id": hero_id}

    # Add hero
    user_hero = UserHero(
        profile_id=profile.id,
        hero_id=hero_id,
        level=1,
        stars=0,
        ascension=0
    )

    db.add(user_hero)
    db.commit()
    db.close()

    return {"message": "Hero added", "hero_id": hero_id}


@router.put("/update/{hero_id}")
def update_hero(
    hero_id: int,
    request: UpdateHeroRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a user's hero stats."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=400, detail="No profile found")

    user_hero = db.query(UserHero).filter(
        UserHero.profile_id == profile.id,
        UserHero.hero_id == hero_id
    ).first()

    if not user_hero:
        db.close()
        raise HTTPException(status_code=404, detail="Hero not owned")

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user_hero, field, value)

    db.commit()
    db.close()

    return {"message": "Hero updated", "hero_id": hero_id}


@router.delete("/remove/{hero_id}")
def remove_hero(
    hero_id: int,
    current_user: User = Depends(get_current_user)
):
    """Remove a hero from user's owned list."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        raise HTTPException(status_code=400, detail="No profile found")

    user_hero = db.query(UserHero).filter(
        UserHero.profile_id == profile.id,
        UserHero.hero_id == hero_id
    ).first()

    if not user_hero:
        db.close()
        raise HTTPException(status_code=404, detail="Hero not owned")

    db.delete(user_hero)
    db.commit()
    db.close()

    return {"message": "Hero removed", "hero_id": hero_id}
