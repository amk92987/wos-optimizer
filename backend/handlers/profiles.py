"""Profile management Lambda handler."""

import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from common.auth import get_effective_user_id
from common.exceptions import AppError, NotFoundError, ValidationError
from common import profile_repo, hero_repo

app = APIGatewayHttpResolver()
logger = Logger()


@app.get("/api/profiles")
def get_profiles():
    user_id = get_effective_user_id(app.current_event.raw_event)
    profiles = profile_repo.get_profiles(user_id)
    return {"profiles": profiles}


@app.post("/api/profiles")
def create_profile():
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}

    name = body.get("name", "Chief")
    state_number = body.get("state_number")
    is_farm = body.get("is_farm_account", False)

    profile = profile_repo.create_profile(
        user_id=user_id,
        name=name,
        state_number=state_number,
        is_farm_account=is_farm,
    )
    return {"profile": profile}, 201


# --- Static routes BEFORE parameterized <profileId> routes ---


@app.get("/api/profiles/current")
def get_current_profile():
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    return {"profile": profile}


@app.get("/api/profiles/deleted")
def get_deleted_profiles():
    user_id = get_effective_user_id(app.current_event.raw_event)
    profiles = profile_repo.get_profiles(user_id, include_deleted=True)
    deleted_profiles = [p for p in profiles if p.get("deleted_at") is not None]
    return {"profiles": deleted_profiles}


# --- Parameterized <profileId> routes ---


@app.get("/api/profiles/<profileId>")
def get_profile(profileId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_profile(user_id, profileId)
    if not profile:
        raise NotFoundError("Profile not found")
    return {"profile": profile}


@app.put("/api/profiles/<profileId>")
def update_profile(profileId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}

    profile = profile_repo.get_profile(user_id, profileId)
    if not profile:
        raise NotFoundError("Profile not found")

    # Filter to allowed update fields
    allowed = {
        "name", "state_number", "server_age_days", "furnace_level",
        "furnace_fc_level", "spending_profile", "priority_focus",
        "alliance_role", "priority_svs", "priority_rally",
        "priority_castle_battle", "priority_exploration", "priority_gathering",
        "is_farm_account", "linked_main_profile_id",
    }
    updates = {k: v for k, v in body.items() if k in allowed}

    if not updates:
        raise ValidationError("No valid fields to update")

    updated = profile_repo.update_profile(user_id, profileId, updates)
    return {"profile": updated}


@app.delete("/api/profiles/<profileId>")
def delete_profile(profileId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    hard = app.current_event.query_string_parameters.get("hard", "false").lower() == "true" if app.current_event.query_string_parameters else False

    profile = profile_repo.get_profile(user_id, profileId)
    if not profile:
        raise NotFoundError("Profile not found")

    result = profile_repo.delete_profile(user_id, profileId, hard=hard)
    return result


@app.post("/api/profiles/<profileId>/duplicate")
def duplicate_profile(profileId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}
    name = body.get("name")

    new_profile = profile_repo.duplicate_profile(user_id, profileId, name)
    return {"profile": new_profile}, 201


@app.post("/api/profiles/<profileId>/restore")
def restore_profile(profileId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile_repo.restore_profile(user_id, profileId)
    return {"status": "restored", "profile_id": profileId}


@app.post("/api/profiles/<profileId>/switch")
def switch_profile(profileId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)

    profile = profile_repo.get_profile(user_id, profileId)
    if not profile:
        raise NotFoundError("Profile not found")

    profile_repo.activate_profile(user_id, profileId)
    return {"status": "switched", "profile_id": profileId}


@app.get("/api/profiles/<profileId>/preview")
def preview_profile(profileId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_profile(user_id, profileId)
    if not profile:
        raise NotFoundError("Profile not found")

    heroes = hero_repo.get_heroes(profileId)
    hero_summary = [
        {
            "name": h.get("hero_name"),
            "level": h.get("level", 1),
            "stars": h.get("stars", 0),
            "generation": h.get("generation", 1),
            "hero_class": h.get("hero_class", ""),
        }
        for h in heroes
    ]
    return {"profile": profile, "heroes": hero_summary}


def lambda_handler(event, context):
    return app.resolve(event, context)
