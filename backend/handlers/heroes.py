"""Lambda handler for hero routes.

Provides CRUD operations for heroes (user-owned) and read access
to the static hero reference data from heroes.json.
"""

import base64
import json
import os

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response

from backend.common.auth import get_effective_user_id
from backend.common.config import Config
from backend.common.exceptions import AppError, NotFoundError, ValidationError
from backend.common.hero_repo import (
    batch_update_heroes,
    delete_hero,
    get_all_heroes_reference,
    get_hero_reference,
    get_heroes,
    update_hero,
    put_hero,
)
from backend.common.profile_repo import get_or_create_profile

app = APIGatewayHttpResolver()
logger = Logger()

ASSETS_DIR = os.path.normpath(os.path.join(Config.DATA_DIR, "..", "assets", "heroes"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_hero_image_base64(image_filename: str) -> str | None:
    """Load a hero portrait from disk and return a data-URI string."""
    if not image_filename:
        return None
    image_path = os.path.join(ASSETS_DIR, image_filename)
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as f:
        ext = os.path.splitext(image_filename)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def _bool_param(value: str | None, default: bool = False) -> bool:
    """Parse a query-string boolean ('true'/'1'/'yes' -> True)."""
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes")


def _get_profile_id_from_current_event() -> str:
    """Resolve the active profile_id for the authenticated user.

    Uses the raw event from the current Powertools resolver context
    so that the auth module can read JWT claims from requestContext.
    """
    raw_event = app.current_event.raw_event
    user_id = get_effective_user_id(raw_event)
    profile = get_or_create_profile(user_id)
    return profile["profile_id"]


def _merge_reference(user_hero: dict) -> dict:
    """Merge static reference fields into a user-hero record."""
    hero_name = user_hero.get("hero_name", "")
    ref = get_hero_reference(hero_name)
    if not ref:
        return user_hero

    merged = {**user_hero}
    # Copy over useful reference fields that the client needs
    for key in (
        "generation",
        "hero_class",
        "tier_overall",
        "tier_expedition",
        "tier_exploration",
        "rarity",
        "image_filename",
        "exploration_skill_1",
        "exploration_skill_1_desc",
        "exploration_skill_2",
        "exploration_skill_2_desc",
        "exploration_skill_3",
        "exploration_skill_3_desc",
        "expedition_skill_1",
        "expedition_skill_1_desc",
        "expedition_skill_2",
        "expedition_skill_2_desc",
        "expedition_skill_3",
        "expedition_skill_3_desc",
        "mythic_gear_name",
        "mythic_gear_skill",
        "mythic_gear_skill_desc",
    ):
        if key in ref and key not in merged:
            merged[key] = ref[key]

    return merged


def _error_response(exc: AppError) -> Response:
    """Build a JSON error response from an AppError."""
    return Response(
        status_code=exc.status_code,
        content_type="application/json",
        body=json.dumps({"error": exc.message}),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/heroes/all")
def get_all_heroes():
    """Return the full hero reference catalogue from heroes.json.

    Query params:
        include_images (bool, default false) - embed base64 portrait data.
    """
    include_images = _bool_param(
        app.current_event.query_string_parameters.get("include_images")
        if app.current_event.query_string_parameters
        else None,
        default=False,
    )

    heroes = get_all_heroes_reference()

    if include_images:
        for hero in heroes:
            hero["image_base64"] = get_hero_image_base64(hero.get("image_filename"))

    return {"heroes": heroes}


@app.get("/api/heroes/owned")
def get_owned_heroes():
    """Return the current user's owned heroes merged with reference data.

    Query params:
        include_images (bool, default true) - embed base64 portrait data.
    """
    profile_id = _get_profile_id_from_current_event()

    include_images = _bool_param(
        app.current_event.query_string_parameters.get("include_images")
        if app.current_event.query_string_parameters
        else None,
        default=True,
    )

    user_heroes = get_heroes(profile_id)

    results = []
    for uh in user_heroes:
        merged = _merge_reference(uh)
        if include_images:
            merged["image_base64"] = get_hero_image_base64(merged.get("image_filename"))
        results.append(merged)

    return {"heroes": results}


@app.put("/api/heroes/batch")
def batch_update():
    """Batch create/update multiple heroes at once.

    Body: {"heroes": [{"name": "Jessie", "level": 50, ...}, ...]}
    """
    profile_id = _get_profile_id_from_current_event()
    body = app.current_event.json_body or {}
    heroes_list = body.get("heroes")

    if not heroes_list or not isinstance(heroes_list, list):
        raise ValidationError("Request body must contain a 'heroes' list")

    results = batch_update_heroes(profile_id, heroes_list)
    return {"updated": len(results), "heroes": results}


@app.put("/api/heroes/<hero_name>")
def update_single_hero(hero_name: str):
    """Update (or create) a single hero.

    Path param: hero_name (URL-encoded hero name)
    Body: fields to update (level, stars, ascension, skills, gear, etc.)
    """
    profile_id = _get_profile_id_from_current_event()
    body = app.current_event.json_body or {}

    if not body:
        raise ValidationError("Request body must not be empty")

    # Validate hero_name exists in reference data
    ref = get_hero_reference(hero_name)
    if not ref:
        raise NotFoundError(f"Unknown hero: {hero_name}")

    result = update_hero(profile_id, hero_name, body)

    # If update_hero returned empty (no fields to update), fall back to put
    if not result:
        result = put_hero(profile_id, hero_name, body)

    return {"hero": result}


@app.delete("/api/heroes/<hero_name>")
def delete_single_hero(hero_name: str):
    """Remove a hero from the user's roster.

    Path param: hero_name (URL-encoded hero name)
    """
    profile_id = _get_profile_id_from_current_event()

    delete_hero(profile_id, hero_name)
    return {"deleted": hero_name}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

@logger.inject_lambda_context
def lambda_handler(event: dict, context):
    """AWS Lambda entrypoint."""
    try:
        return app.resolve(event, context)
    except AppError as exc:
        logger.warning("Application error", extra={"error": exc.message, "status": exc.status_code})
        return _error_response(exc)
    except Exception:
        logger.exception("Unhandled error in heroes handler")
        return Response(
            status_code=500,
            content_type="application/json",
            body=json.dumps({"error": "Internal server error"}),
        )
