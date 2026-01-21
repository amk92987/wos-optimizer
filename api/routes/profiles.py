"""
Profile routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db, get_or_create_profile
from database.models import User, UserProfile
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
