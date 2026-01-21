"""
Dashboard routes for the API.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import User, UserProfile, UserHero
from api.routes.auth import get_current_user

router = APIRouter()


class DashboardStats(BaseModel):
    total_heroes: int
    owned_heroes: int
    furnace_level: int
    furnace_display: str
    server_age_days: int
    generation: int
    state_number: Optional[int]
    spending_profile: str
    alliance_role: str
    priority_focus: str


def get_generation(server_age_days: int) -> int:
    """Calculate generation based on server age."""
    if server_age_days < 40:
        return 1
    elif server_age_days < 120:
        return 2
    elif server_age_days < 200:
        return 3
    elif server_age_days < 280:
        return 4
    elif server_age_days < 360:
        return 5
    elif server_age_days < 440:
        return 6
    elif server_age_days < 520:
        return 7
    elif server_age_days < 600:
        return 8
    elif server_age_days < 680:
        return 9
    elif server_age_days < 760:
        return 10
    elif server_age_days < 840:
        return 11
    elif server_age_days < 920:
        return 12
    elif server_age_days < 1000:
        return 13
    else:
        return 14


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Get dashboard statistics for current user."""
    init_db()
    db = get_db()

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        db.close()
        return {
            "total_heroes": 56,
            "owned_heroes": 0,
            "furnace_level": 1,
            "furnace_display": "Lv.1",
            "server_age_days": 0,
            "generation": 1,
            "state_number": None,
            "spending_profile": "f2p",
            "alliance_role": "filler",
            "priority_focus": "balanced_growth"
        }

    # Count owned heroes
    owned_count = db.query(UserHero).filter(
        UserHero.profile_id == profile.id
    ).count()

    # Determine furnace display
    if profile.furnace_fc_level:
        furnace_display = profile.furnace_fc_level.replace("-0", "")
    else:
        furnace_display = f"Lv.{profile.furnace_level}"

    generation = get_generation(profile.server_age_days)

    result = {
        "total_heroes": 56,
        "owned_heroes": owned_count,
        "furnace_level": profile.furnace_level,
        "furnace_display": furnace_display,
        "server_age_days": profile.server_age_days,
        "generation": generation,
        "state_number": profile.state_number,
        "spending_profile": profile.spending_profile or "f2p",
        "alliance_role": profile.alliance_role or "filler",
        "priority_focus": profile.priority_focus or "balanced_growth"
    }

    db.close()
    return result
