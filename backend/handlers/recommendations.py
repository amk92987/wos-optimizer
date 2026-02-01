"""Recommendations Lambda handler."""

import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from backend.common.auth import get_effective_user_id
from backend.common.exceptions import AppError, NotFoundError
from backend.common import profile_repo, hero_repo

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


def lambda_handler(event, context):
    return app.resolve(event, context)
