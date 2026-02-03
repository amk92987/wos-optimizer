"""Recommendations Lambda handler."""

import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from common.auth import get_effective_user_id
from common.exceptions import AppError, NotFoundError
from common import profile_repo, hero_repo

app = APIGatewayHttpResolver()
logger = Logger()


def _load_user_context():
    """Load profile and heroes for the current user."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)
    return profile, heroes


@app.get("/api/recommendations")
def get_recommendations():
    profile, heroes = _load_user_context()

    from engine.recommendation_engine import get_engine
    engine = get_engine()

    recommendations = engine.get_recommendations(profile=profile, heroes=heroes)
    return {"recommendations": recommendations}


@app.get("/api/recommendations/investments")
def get_investments():
    profile, heroes = _load_user_context()

    from engine.recommendation_engine import get_engine
    engine = get_engine()

    investments = engine.get_hero_investments(profile=profile, heroes=heroes)
    return {"investments": investments}


@app.get("/api/recommendations/phase")
def get_phase_info():
    profile, heroes = _load_user_context()

    from engine.recommendation_engine import get_engine
    engine = get_engine()

    try:
        phase_info = engine.get_phase_info(profile=profile)
        return {"phase": phase_info}
    except Exception as e:
        logger.warning(f"Phase info failed: {e}")
        furnace = profile.get("furnace_level", 1)
        if furnace < 19:
            phase = "early_game"
        elif furnace < 30:
            phase = "mid_game"
        else:
            fc = profile.get("furnace_fc_level", "")
            phase = "endgame" if fc and int(str(fc).replace("FC", "").strip() or "0") >= 5 else "late_game"
        return {"phase": {"name": phase, "furnace_level": furnace}}


@app.get("/api/recommendations/gear-priority")
def get_gear_priority():
    profile, heroes = _load_user_context()

    from engine.recommendation_engine import get_engine
    engine = get_engine()

    try:
        gear_priority = engine.get_gear_priority(spending_profile=profile.get("spending_profile", "f2p"))
        return {"gear_priority": gear_priority}
    except Exception as e:
        logger.warning(f"Gear priority failed: {e}")
        return {"gear_priority": []}


def lambda_handler(event, context):
    return app.resolve(event, context)
