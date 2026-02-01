"""Chief gear and charms Lambda handler."""

import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from backend.common.auth import get_effective_user_id
from backend.common.exceptions import AppError, ValidationError
from backend.common import chief_repo, profile_repo

app = APIGatewayHttpResolver()
logger = Logger()


def _get_profile_id() -> str:
    """Get the active profile ID for the current user."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    return profile["profile_id"]


@app.get("/api/chief/gear")
def get_gear():
    profile_id = _get_profile_id()
    gear = chief_repo.get_chief_gear(profile_id)
    return {"gear": gear}


@app.put("/api/chief/gear")
def update_gear():
    profile_id = _get_profile_id()
    body = app.current_event.json_body or {}

    allowed = {
        "helmet_quality", "helmet_level",
        "armor_quality", "armor_level",
        "gloves_quality", "gloves_level",
        "boots_quality", "boots_level",
        "ring_quality", "ring_level",
        "amulet_quality", "amulet_level",
    }
    updates = {k: v for k, v in body.items() if k in allowed}

    if not updates:
        raise ValidationError("No valid gear fields to update")

    gear = chief_repo.update_chief_gear(profile_id, updates)
    return {"gear": gear}


@app.get("/api/chief/charms")
def get_charms():
    profile_id = _get_profile_id()
    charms = chief_repo.get_chief_charms(profile_id)
    return {"charms": charms}


@app.put("/api/chief/charms")
def update_charms():
    profile_id = _get_profile_id()
    body = app.current_event.json_body or {}

    allowed = {
        "cap_slot_1", "cap_slot_2", "cap_slot_3",
        "watch_slot_1", "watch_slot_2", "watch_slot_3",
        "coat_slot_1", "coat_slot_2", "coat_slot_3",
        "pants_slot_1", "pants_slot_2", "pants_slot_3",
        "belt_slot_1", "belt_slot_2", "belt_slot_3",
        "weapon_slot_1", "weapon_slot_2", "weapon_slot_3",
    }
    updates = {k: v for k, v in body.items() if k in allowed}

    if not updates:
        raise ValidationError("No valid charm fields to update")

    charms = chief_repo.update_chief_charms(profile_id, updates)
    return {"charms": charms}


def lambda_handler(event, context):
    return app.resolve(event, context)
