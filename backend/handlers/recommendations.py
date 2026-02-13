"""Recommendations Lambda handler."""

import json
from dataclasses import asdict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from common.auth import get_effective_user_id
from common.exceptions import AppError, NotFoundError
from common import profile_repo, hero_repo

app = APIGatewayHttpResolver()
logger = Logger()


class DictObj:
    """Wraps a dict so getattr() works for attribute-style access.

    The recommendation engine (and its analyzers) was written for SQLAlchemy
    ORM objects that support attribute access.  DynamoDB returns plain dicts,
    so this thin wrapper bridges the gap.
    """
    def __init__(self, d: dict):
        self.__dict__.update(d)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


def _wrap_profile(profile_dict: dict) -> DictObj:
    """Wrap a profile dict for the engine."""
    return DictObj(profile_dict)


def _wrap_heroes(hero_dicts: list) -> list:
    """Wrap hero dicts for the engine.

    The engine's _heroes_list_to_dict looks for:
      - hasattr(uh, 'hero') and uh.hero  (ORM relationship)
      - getattr(uh, 'name', '')          (fallback)
    DynamoDB items use 'hero_name', so we add 'name' as an alias.
    """
    wrapped = []
    for h in hero_dicts:
        # Ensure 'name' attribute exists (engine looks for it)
        if "name" not in h and "hero_name" in h:
            h["name"] = h["hero_name"]
        wrapped.append(DictObj(h))
    return wrapped


def _load_user_context():
    """Load profile and heroes for the current user."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)
    return profile, heroes


def _serialize_recommendations(recommendations):
    """Convert Recommendation dataclass instances to JSON-safe dicts."""
    results = []
    for rec in recommendations:
        try:
            results.append(asdict(rec))
        except TypeError:
            # Already a dict or non-dataclass
            if hasattr(rec, '__dict__'):
                results.append(rec.__dict__)
            else:
                results.append(rec)
    return results


@app.get("/api/recommendations")
def get_recommendations():
    profile, heroes = _load_user_context()

    from engine.recommendation_engine import get_engine
    engine = get_engine()

    profile_obj = _wrap_profile(profile)
    hero_objs = _wrap_heroes(heroes)

    recommendations = engine.get_recommendations(profile=profile_obj, user_heroes=hero_objs)
    return {"recommendations": _serialize_recommendations(recommendations)}


@app.get("/api/recommendations/investments")
def get_investments():
    profile, heroes = _load_user_context()

    from engine.recommendation_engine import get_engine
    engine = get_engine()

    profile_obj = _wrap_profile(profile)
    hero_objs = _wrap_heroes(heroes)

    # TODO: Implement get_hero_investments in RecommendationEngine
    return {"investments": []}


@app.get("/api/recommendations/phase")
def get_phase_info():
    profile, heroes = _load_user_context()

    from engine.recommendation_engine import get_engine
    engine = get_engine()

    try:
        profile_obj = _wrap_profile(profile)
        phase_info = engine.get_phase_info(profile=profile_obj)
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
    try:
        return app.resolve(event, context)
    except AppError as exc:
        logger.warning("Application error", extra={"error": exc.message, "status": exc.status_code})
        return {"statusCode": exc.status_code, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": exc.message})}
    except Exception as exc:
        logger.exception("Unhandled error in recommendations handler")
        from common.error_capture import capture_error
        capture_error("recommendations", event, exc, logger)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Internal server error"})}
