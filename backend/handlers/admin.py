"""Admin Lambda handler."""

import json
import os
from collections import Counter
from datetime import datetime, timezone

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from common.auth import get_effective_user_id, require_admin, is_admin, get_user_id
from common.error_capture import capture_error
from common.exceptions import AppError, NotFoundError, ValidationError
from common.config import Config
from common import admin_repo, user_repo, ai_repo, profile_repo, hero_repo
from common.db import get_table

cognito = boto3.client("cognito-idp", region_name=Config.REGION)

app = APIGatewayHttpResolver()
logger = Logger()


def _require_admin():
    """Guard: require admin role on every admin route."""
    require_admin(app.current_event.raw_event)


# --- Users ---

@app.get("/api/admin/users")
def list_users():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    test_only = params.get("test_only", "false").lower() == "true"
    limit = int(params.get("limit", "50"))

    users = user_repo.list_users(test_only=test_only, limit=limit)

    # Enrich each user with id, profile_count, states, usage_7d
    for u in users:
        uid = u.get("user_id")
        u["id"] = uid  # Frontend expects both 'id' and 'user_id'
        try:
            profiles = profile_repo.get_profiles(uid) if uid else []
            u["profile_count"] = len(profiles)
            u["states"] = [p["state_number"] for p in profiles if p.get("state_number")]
        except Exception:
            logger.debug("Failed to enrich user %s with profiles", uid, exc_info=True)
            u["profile_count"] = 0
            u["states"] = []
        u.setdefault("usage_7d", 0)

    return {"users": users}


@app.post("/api/admin/users")
def create_user():
    _require_admin()
    body = app.current_event.json_body or {}

    email = body.get("email")
    username = body.get("username", email)
    role = body.get("role", "user")
    is_test = body.get("is_test_account", False)
    # Accept either 'password' (from frontend) or 'password_hash' (direct)
    password_hash = body.get("password_hash") or body.get("password", "")

    if not email:
        raise ValidationError("Email is required")

    import uuid
    user_id = body.get("user_id", str(uuid.uuid4()))

    user = user_repo.create_user(
        user_id=user_id,
        email=email,
        username=username,
        role=role,
        is_test_account=is_test,
        password_hash=password_hash,
    )
    user["id"] = user.get("user_id")

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "create_user", "user", user_id, username)

    return {"user": user}, 201


@app.get("/api/admin/users/<userId>")
def get_user(userId: str):
    _require_admin()
    user = user_repo.get_user(userId)
    if not user:
        raise NotFoundError("User not found")
    user["id"] = user.get("user_id")

    profiles = profile_repo.get_profiles(userId, include_deleted=True)
    return {"user": user, "profiles": profiles}


@app.put("/api/admin/users/<userId>")
def update_user(userId: str):
    _require_admin()
    body = app.current_event.json_body or {}

    user = user_repo.get_user(userId)
    if not user:
        raise NotFoundError("User not found")

    allowed = {"role", "is_active", "is_verified", "is_test_account", "ai_daily_limit", "ai_access_level", "theme", "email"}
    updates = {k: v for k, v in body.items() if k in allowed}

    if not updates:
        raise ValidationError("No valid fields to update")

    updated = user_repo.update_user(userId, updates)
    updated["id"] = updated.get("user_id", userId)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_user", "user", userId, user.get("username"), json.dumps(updates))

    return {"user": updated}


@app.delete("/api/admin/users/<userId>")
def delete_user(userId: str):
    _require_admin()
    user = user_repo.get_user(userId)
    if not user:
        raise NotFoundError("User not found")

    user_repo.delete_user(userId)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "delete_user", "user", userId, user.get("username"))

    return {"status": "deleted"}


@app.post("/api/admin/impersonate/<userId>")
def impersonate_user(userId: str):
    _require_admin()
    user = user_repo.get_user(userId)
    if not user:
        raise NotFoundError("User not found")

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "impersonate", "user", userId, user.get("username"))

    profiles = profile_repo.get_profiles(userId)
    return {
        "user": user,
        "profiles": profiles,
        "impersonating": True,
    }


# --- Seed Test Accounts ---

# Hero data for each test account archetype
_TEST_ACCOUNTS = [
    # --- 1. Gen 10 Dolphin (Day 700, FC5) - Main + Farm ---
    {
        "email": "test_gen10_dolphin@test.com",
        "label": "Gen 10 Dolphin (FC5, Day 700)",
        "profiles": [
            {
                "name": "FrostKnight_560",
                "state_number": 456,
                "server_age_days": 700,
                "furnace_level": 30,
                "furnace_fc_level": 5,
                "spending_profile": "dolphin",
                "priority_focus": "svs_combat",
                "alliance_role": "filler",
                "priority_svs": 5,
                "priority_rally": 5,
                "priority_castle_battle": 4,
                "priority_exploration": 2,
                "priority_gathering": 1,
                "heroes": [
                    # Gen 1 - All maxed
                    {"name": "Jeronimo",  "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Natalia",   "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Molly",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Sergey",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Jessie",    "level": 75, "stars": 5, "expl": [4,4,4], "exped": [5,5,5], "gear": 5},
                    {"name": "Bahiti",    "level": 70, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Patrick",   "level": 70, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    # Gen 2-4 - All maxed
                    {"name": "Flint",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Philly",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Alonso",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Logan",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Mia",       "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Ahmose",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Reina",     "level": 75, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Lynn",      "level": 75, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    # Gen 5-6 - Very strong
                    {"name": "Hector",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Norah",     "level": 75, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Gwen",      "level": 75, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Wu Ming",   "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Renee",     "level": 70, "stars": 4, "ascension": 4, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    # Gen 7-8 - Good progress
                    {"name": "Gordon",    "level": 75, "stars": 4, "ascension": 4, "expl": [4,4,4], "exped": [4,4,4], "gear": 5},
                    {"name": "Edith",     "level": 70, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Gatot",     "level": 70, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Hendrik",   "level": 70, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Sonya",     "level": 65, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    # Gen 9-10 - Active investment
                    {"name": "Magnus",    "level": 65, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 4},
                    {"name": "Xura",      "level": 60, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Blanchette","level": 65, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 4},
                ],
            },
            {
                "name": "FrostKnight_Farm",
                "state_number": 456,
                "server_age_days": 700,
                "furnace_level": 25,
                "spending_profile": "f2p",
                "alliance_role": "farmer",
                "priority_svs": 1, "priority_rally": 1, "priority_castle_battle": 1,
                "priority_exploration": 1, "priority_gathering": 5,
                "is_farm_account": True,
                "heroes": [
                    {"name": "Smith",     "level": 50, "stars": 4, "expl": [4,4,1], "exped": [4,4,1], "gear": 0},
                    {"name": "Eugene",    "level": 50, "stars": 4, "expl": [4,4,1], "exped": [4,4,1], "gear": 0},
                    {"name": "Charlie",   "level": 50, "stars": 4, "expl": [4,4,1], "exped": [4,4,1], "gear": 0},
                    {"name": "Cloris",    "level": 50, "stars": 4, "expl": [4,4,1], "exped": [4,4,1], "gear": 0},
                    {"name": "Sergey",    "level": 45, "stars": 3, "expl": [3,3,1], "exped": [3,3,1], "gear": 0},
                    {"name": "Bahiti",    "level": 40, "stars": 2, "expl": [2,2,1], "exped": [2,2,1], "gear": 0},
                    {"name": "Jessie",    "level": 40, "stars": 2, "expl": [2,2,1], "exped": [3,3,1], "gear": 0},
                    {"name": "Natalia",   "level": 40, "stars": 2, "expl": [2,2,1], "exped": [2,2,1], "gear": 0},
                ],
            },
        ],
    },
    # --- 2. Gen 4 F2P (Day 240, F27) ---
    {
        "email": "test_gen4_f2p@test.com",
        "label": "Gen 4 F2P (F27, Day 240)",
        "profiles": [
            {
                "name": "IceWarrior_240",
                "state_number": 789,
                "server_age_days": 240,
                "furnace_level": 27,
                "spending_profile": "f2p",
                "priority_focus": "balanced_growth",
                "alliance_role": "filler",
                "priority_svs": 5,
                "priority_rally": 4,
                "priority_castle_battle": 3,
                "priority_exploration": 3,
                "priority_gathering": 3,
                "heroes": [
                    # Gen 1 core
                    {"name": "Jeronimo",  "level": 60, "stars": 4, "ascension": 3, "expl": [4,4,3], "exped": [4,4,3], "gear": 4},
                    {"name": "Natalia",   "level": 55, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Molly",     "level": 55, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Sergey",    "level": 50, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [4,3,3], "gear": 3},
                    {"name": "Jessie",    "level": 45, "stars": 3, "ascension": 1, "expl": [2,2,2], "exped": [4,3,3], "gear": 3},
                    {"name": "Bahiti",    "level": 45, "stars": 3, "ascension": 1, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Patrick",   "level": 40, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 2},
                    # Gen 2
                    {"name": "Flint",     "level": 50, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Philly",    "level": 50, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Alonso",    "level": 55, "stars": 3, "ascension": 3, "expl": [4,4,3], "exped": [4,4,3], "gear": 4},
                    # Gen 3
                    {"name": "Logan",     "level": 40, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 2},
                    {"name": "Mia",       "level": 40, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 2},
                    # Gen 4 - Just unlocked
                    {"name": "Ahmose",    "level": 35, "stars": 1, "expl": [1,1,1], "exped": [1,1,1], "gear": 0},
                ],
            },
        ],
    },
    # --- 3. Gen 2 Whale (Day 80, F25) - Main + Farm ---
    {
        "email": "test_gen2_whale@test.com",
        "label": "Gen 2 Whale (F25, Day 80)",
        "profiles": [
            {
                "name": "ArcticKing_80",
                "state_number": 999,
                "server_age_days": 80,
                "furnace_level": 25,
                "spending_profile": "whale",
                "priority_focus": "svs_combat",
                "alliance_role": "rally_lead",
                "priority_svs": 5,
                "priority_rally": 5,
                "priority_castle_battle": 5,
                "priority_exploration": 2,
                "priority_gathering": 1,
                "heroes": [
                    # Gen 1 - All maxed (whale)
                    {"name": "Jeronimo",  "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Natalia",   "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Molly",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Sergey",    "level": 75, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 4},
                    {"name": "Jessie",    "level": 70, "stars": 5, "expl": [4,4,4], "exped": [5,5,5], "gear": 3},
                    {"name": "Bahiti",    "level": 70, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 4},
                    {"name": "Gina",      "level": 65, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 3},
                    {"name": "Patrick",   "level": 65, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 3},
                    {"name": "Zinman",    "level": 60, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 3},
                    {"name": "Ling Xue",  "level": 60, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 3},
                    # Gen 2 - High investment
                    {"name": "Flint",     "level": 70, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Philly",    "level": 70, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Alonso",    "level": 75, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    # Gen 3 - Early access from spending
                    {"name": "Logan",     "level": 50, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 0},
                    {"name": "Mia",       "level": 45, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 0},
                ],
            },
            {
                "name": "ArcticKing_Farm",
                "state_number": 999,
                "server_age_days": 80,
                "furnace_level": 18,
                "spending_profile": "f2p",
                "alliance_role": "farmer",
                "priority_svs": 1, "priority_rally": 1, "priority_castle_battle": 1,
                "priority_exploration": 1, "priority_gathering": 5,
                "is_farm_account": True,
                "heroes": [
                    {"name": "Smith",     "level": 40, "stars": 3, "expl": [3,3,1], "exped": [3,3,1], "gear": 0},
                    {"name": "Eugene",    "level": 40, "stars": 3, "expl": [3,3,1], "exped": [3,3,1], "gear": 0},
                    {"name": "Charlie",   "level": 40, "stars": 3, "expl": [3,3,1], "exped": [3,3,1], "gear": 0},
                    {"name": "Cloris",    "level": 40, "stars": 3, "expl": [3,3,1], "exped": [3,3,1], "gear": 0},
                    {"name": "Sergey",    "level": 30, "stars": 2, "expl": [2,2,1], "exped": [2,2,1], "gear": 0},
                    {"name": "Bahiti",    "level": 25, "stars": 1, "expl": [1,1,1], "exped": [1,1,1], "gear": 0},
                    {"name": "Jessie",    "level": 20, "stars": 1, "expl": [1,1,1], "exped": [2,2,1], "gear": 0},
                    {"name": "Natalia",   "level": 20, "stars": 1, "expl": [1,1,1], "exped": [1,1,1], "gear": 0},
                ],
            },
        ],
    },
    # --- 4. Multi-State Player (2 profiles, different states) ---
    {
        "email": "test_multi_state@test.com",
        "label": "Multi-State (2 states)",
        "profiles": [
            {
                "name": "State200_Main",
                "state_number": 200,
                "server_age_days": 500,
                "furnace_level": 30,
                "spending_profile": "minnow",
                "alliance_role": "filler",
                "priority_svs": 4, "priority_rally": 3, "priority_castle_battle": 3,
                "priority_exploration": 3, "priority_gathering": 3,
                "heroes": [
                    {"name": "Jeronimo",  "level": 70, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 4},
                    {"name": "Natalia",   "level": 65, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Molly",     "level": 65, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Jessie",    "level": 50, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [4,3,3], "gear": 3},
                    {"name": "Sergey",    "level": 50, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [4,3,3], "gear": 3},
                    {"name": "Flint",     "level": 60, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 3},
                    {"name": "Alonso",    "level": 55, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Hector",    "level": 50, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 2},
                ],
            },
            {
                "name": "State850_Alt",
                "state_number": 850,
                "server_age_days": 100,
                "furnace_level": 22,
                "spending_profile": "minnow",
                "alliance_role": "filler",
                "priority_svs": 3, "priority_rally": 3, "priority_castle_battle": 3,
                "priority_exploration": 4, "priority_gathering": 4,
                "heroes": [
                    {"name": "Jeronimo",  "level": 45, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 2},
                    {"name": "Natalia",   "level": 40, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 2},
                    {"name": "Molly",     "level": 40, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 2},
                    {"name": "Jessie",    "level": 30, "stars": 1, "expl": [1,1,1], "exped": [2,1,1], "gear": 1},
                    {"name": "Sergey",    "level": 30, "stars": 1, "expl": [1,1,1], "exped": [2,1,1], "gear": 1},
                ],
            },
        ],
    },
    # --- 5. New Player (Day 7, F18) ---
    {
        "email": "test_new_player@test.com",
        "label": "New Player (F18, Day 7)",
        "profiles": [
            {
                "name": "FreshStart",
                "state_number": 900,
                "server_age_days": 7,
                "furnace_level": 18,
                "spending_profile": "f2p",
                "priority_focus": "balanced_growth",
                "alliance_role": "casual",
                "priority_svs": 2, "priority_rally": 2, "priority_castle_battle": 2,
                "priority_exploration": 4, "priority_gathering": 4,
                "heroes": [
                    {"name": "Jeronimo",  "level": 20, "stars": 1, "expl": [1,1,1], "exped": [1,1,1], "gear": 0},
                    {"name": "Molly",     "level": 15, "stars": 0, "expl": [1,1,1], "exped": [1,1,1], "gear": 0},
                    {"name": "Bahiti",    "level": 15, "stars": 0, "expl": [1,1,1], "exped": [1,1,1], "gear": 0},
                ],
            },
        ],
    },
    # --- 6. Rally Leader (Orca, Day 350, F30) ---
    {
        "email": "test_rally_leader@test.com",
        "label": "Rally Leader (Orca, F30, Day 350)",
        "profiles": [
            {
                "name": "StormBringer",
                "state_number": 350,
                "server_age_days": 350,
                "furnace_level": 30,
                "spending_profile": "orca",
                "priority_focus": "svs_combat",
                "alliance_role": "rally_lead",
                "priority_svs": 5, "priority_rally": 5, "priority_castle_battle": 5,
                "priority_exploration": 2, "priority_gathering": 1,
                "heroes": [
                    # Gen 1 - Maxed
                    {"name": "Jeronimo",  "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Natalia",   "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Molly",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Sergey",    "level": 75, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Jessie",    "level": 70, "stars": 5, "expl": [4,4,4], "exped": [5,5,5], "gear": 4},
                    {"name": "Patrick",   "level": 65, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 3},
                    # Gen 2-4
                    {"name": "Flint",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Alonso",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Logan",     "level": 70, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Ahmose",    "level": 70, "stars": 5, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    # Gen 5
                    {"name": "Hector",    "level": 75, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Norah",     "level": 70, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    # Gen 6
                    {"name": "Wu Ming",   "level": 65, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                ],
            },
        ],
    },
    # --- 7. Gen 12 Whale (endgame) ---
    {
        "email": "test_gen12_whale@test.com",
        "label": "Gen 12 Whale (FC8, Day 880)",
        "profiles": [
            {
                "name": "IceTitan",
                "state_number": 100,
                "server_age_days": 880,
                "furnace_level": 30,
                "furnace_fc_level": 8,
                "spending_profile": "whale",
                "priority_focus": "svs_combat",
                "alliance_role": "rally_lead",
                "priority_svs": 5, "priority_rally": 5, "priority_castle_battle": 5,
                "priority_exploration": 3, "priority_gathering": 1,
                "heroes": [
                    # Gen 1 fully maxed
                    {"name": "Jeronimo",  "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Natalia",   "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Molly",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Sergey",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Jessie",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    # Gen 2-6 fully maxed
                    {"name": "Flint",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Alonso",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Hector",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Wu Ming",   "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    # Gen 7-10 strong
                    {"name": "Gatot",     "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Gordon",    "level": 80, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Blanchette","level": 75, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    {"name": "Magnus",    "level": 75, "stars": 5, "expl": [5,5,5], "exped": [5,5,5], "gear": 5},
                    # Gen 11-12 developing
                    {"name": "Eleonora",  "level": 70, "stars": 4, "ascension": 3, "expl": [4,4,4], "exped": [4,4,4], "gear": 4},
                    {"name": "Rufus",     "level": 65, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Hervor",    "level": 65, "stars": 3, "ascension": 2, "expl": [3,3,3], "exped": [3,3,3], "gear": 3},
                    {"name": "Karol",     "level": 60, "stars": 2, "ascension": 1, "expl": [2,2,2], "exped": [2,2,2], "gear": 2},
                ],
            },
        ],
    },
]

_TEST_PASSWORD = "Test1234!"


def _build_hero_data(h: dict) -> dict:
    """Convert shorthand hero definition to full put_hero data dict."""
    # Support both individual skill arrays and uniform "skills" shorthand
    expl = h.get("expl", [h.get("skills", 1)] * 3)
    exped = h.get("exped", [h.get("skills", 1)] * 3)
    gear_quality = h.get("gear", 0)
    gear_level = gear_quality * 20 if gear_quality > 0 else 0
    return {
        "level": h.get("level", 1),
        "stars": h.get("stars", 0),
        "ascension": h.get("ascension", 0),
        "exploration_skill_1": expl[0] if len(expl) > 0 else 1,
        "exploration_skill_2": expl[1] if len(expl) > 1 else 1,
        "exploration_skill_3": expl[2] if len(expl) > 2 else 1,
        "expedition_skill_1": exped[0] if len(exped) > 0 else 1,
        "expedition_skill_2": exped[1] if len(exped) > 1 else 1,
        "expedition_skill_3": exped[2] if len(exped) > 2 else 1,
        "gear_slot1_quality": gear_quality,
        "gear_slot1_level": gear_level,
        "gear_slot2_quality": gear_quality,
        "gear_slot2_level": gear_level,
        "gear_slot3_quality": gear_quality,
        "gear_slot3_level": gear_level,
        "gear_slot4_quality": gear_quality,
        "gear_slot4_level": gear_level,
    }


def _get_or_create_cognito_user(email: str) -> str:
    """Create a Cognito user or get existing sub. Returns cognito sub."""
    try:
        cognito.admin_create_user(
            UserPoolId=Config.USER_POOL_ID,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
            MessageAction="SUPPRESS",
        )
        cognito.admin_set_user_password(
            UserPoolId=Config.USER_POOL_ID,
            Username=email,
            Password=_TEST_PASSWORD,
            Permanent=True,
        )
    except cognito.exceptions.UsernameExistsException:
        pass  # User already exists, that's fine

    # Look up the sub
    resp = cognito.admin_get_user(
        UserPoolId=Config.USER_POOL_ID,
        Username=email,
    )
    sub = None
    for attr in resp.get("UserAttributes", []):
        if attr["Name"] == "sub":
            sub = attr["Value"]
            break
    if not sub:
        raise ValidationError(f"Could not find sub for {email}")
    return sub


@app.post("/api/admin/seed-test-accounts")
def seed_test_accounts():
    """Create test accounts with profiles and heroes for testing."""
    _require_admin()

    admin_id = get_user_id(app.current_event.raw_event)
    results = []

    for acct in _TEST_ACCOUNTS:
        email = acct["email"]
        label = acct["label"]
        status = "created"

        try:
            # 1. Create Cognito user (or get existing)
            cognito_sub = _get_or_create_cognito_user(email)

            # 2. Create or update DynamoDB user record directly
            now = datetime.now(timezone.utc).isoformat()
            existing_user = user_repo.get_user(cognito_sub)
            if existing_user:
                status = "reset"
                if not existing_user.get("is_test_account"):
                    user_repo.update_user(cognito_sub, {"is_test_account": True})
            else:
                table = get_table("main")
                table.put_item(Item={
                    "PK": f"USER#{cognito_sub}",
                    "SK": "METADATA",
                    "entity_type": "USER",
                    "user_id": cognito_sub,
                    "email": email,
                    "username": email,
                    "role": "user",
                    "is_active": True,
                    "is_verified": False,
                    "is_test_account": True,
                    "ai_requests_today": 0,
                    "ai_access_level": "limited",
                    "theme": "dark",
                    "created_at": now,
                    "updated_at": now,
                })

            # 3. Delete existing profiles + heroes to reset data
            existing_profiles = profile_repo.get_profiles(cognito_sub, include_deleted=True)
            for ep in existing_profiles:
                pid = ep.get("profile_id") or ep["SK"].replace("PROFILE#", "")
                profile_repo.delete_profile(cognito_sub, pid, hard=True)

            # 4. Create profiles (supports multiple per account)
            profiles_data = acct.get("profiles", [])
            # Backwards compat: single "profile" + "heroes" format
            if not profiles_data and "profile" in acct:
                profiles_data = [{**acct["profile"], "heroes": acct.get("heroes", [])}]

            total_heroes = 0
            first_profile_id = None
            for idx, prof_data in enumerate(profiles_data):
                profile = profile_repo.create_profile(
                    user_id=cognito_sub,
                    name=prof_data["name"],
                    state_number=prof_data.get("state_number"),
                    is_farm_account=prof_data.get("is_farm_account", False),
                )
                profile_id = profile["profile_id"]
                if idx == 0:
                    first_profile_id = profile_id

                # Update profile settings
                skip_keys = {"name", "state_number", "heroes", "is_farm_account"}
                profile_settings = {k: v for k, v in prof_data.items() if k not in skip_keys}
                if profile_settings:
                    profile_repo.update_profile(cognito_sub, profile_id, profile_settings)

                # Add heroes
                for h in prof_data.get("heroes", []):
                    hero_data = _build_hero_data(h)
                    hero_repo.put_hero(profile_id, h["name"], hero_data)
                    total_heroes += 1

            # Activate first profile as default
            if first_profile_id:
                profile_repo.activate_profile(cognito_sub, first_profile_id)

            results.append({
                "email": email,
                "label": label,
                "status": status,
                "user_id": cognito_sub,
                "profiles": len(profiles_data),
                "heroes": total_heroes,
            })

        except Exception as e:
            logger.error("Failed to create test account", email=email, error=str(e))
            results.append({
                "email": email,
                "label": label,
                "status": "error",
                "error": str(e),
            })

    admin_repo.log_audit(
        admin_id, "admin", "seed_test_accounts",
        details=json.dumps({"accounts": len(results), "password": _TEST_PASSWORD}),
    )

    return {
        "results": results,
        "password": _TEST_PASSWORD,
        "message": f"Processed {len(results)} test accounts",
    }


# --- Feature Flags ---

@app.get("/api/admin/flags")
def list_flags():
    _require_admin()
    flags = admin_repo.get_feature_flags()
    return {"flags": flags}


@app.put("/api/admin/flags/<flagName>")
def update_flag(flagName: str):
    _require_admin()
    body = app.current_event.json_body or {}

    allowed = {"is_enabled", "description"}
    updates = {k: v for k, v in body.items() if k in allowed}

    flag = admin_repo.update_feature_flag(flagName, updates)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_flag", "flag", flagName, details=json.dumps(updates))

    return {"flag": flag}


# --- AI Settings ---

@app.get("/api/admin/ai-settings")
def get_ai_settings():
    _require_admin()
    settings = ai_repo.get_ai_settings()
    return {"settings": settings}


@app.put("/api/admin/ai-settings")
def update_ai_settings():
    _require_admin()
    body = app.current_event.json_body or {}

    # Map frontend field names to backend field names
    field_aliases = {
        "primary_model": "openai_model",
        "fallback_model": "anthropic_model",
    }
    allowed = {"mode", "daily_limit_free", "daily_limit_admin", "cooldown_seconds", "primary_provider", "fallback_provider", "openai_model", "anthropic_model", "primary_model", "fallback_model"}
    updates = {}
    for k, v in body.items():
        if k in allowed:
            mapped_key = field_aliases.get(k, k)
            updates[mapped_key] = v

    settings = ai_repo.update_ai_settings(updates)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_ai_settings", details=json.dumps(updates))

    return {"settings": settings}


# --- Audit Log ---

@app.get("/api/admin/audit-log")
def get_audit_log():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    month = params.get("month")
    limit = int(params.get("limit", "100"))

    logs = admin_repo.get_audit_logs(month=month, limit=limit)
    return {"logs": logs}


# --- Metrics ---

@app.get("/api/admin/metrics")
def get_metrics():
    _require_admin()

    users = user_repo.list_users(limit=1000)
    real_users = [u for u in users if not u.get("is_test_account")]
    test_accounts = len(users) - len(real_users)
    active_users = sum(1 for u in real_users if u.get("is_active"))

    ai_settings = ai_repo.get_ai_settings()
    feedback = admin_repo.get_feedback()

    return {
        "total_users": len(real_users),
        "test_accounts": test_accounts,
        "active_users": active_users,
        "ai_mode": ai_settings.get("mode", "off"),
        "total_ai_requests": ai_settings.get("total_requests", 0),
        "pending_feedback": sum(1 for f in feedback if f.get("status") in ("new", "pending_fix", "pending_update")),
    }


# --- Announcements ---

@app.get("/api/admin/announcements")
def list_announcements():
    _require_admin()
    announcements = admin_repo.get_announcements()
    return {"announcements": announcements}


@app.post("/api/admin/announcements")
def create_announcement():
    _require_admin()
    body = app.current_event.json_body or {}

    title = body.get("title")
    message = body.get("message")
    if not title or not message:
        raise ValidationError("Title and message are required")

    admin_id = get_user_id(app.current_event.raw_event)
    announcement = admin_repo.create_announcement(
        title=title,
        message=message,
        created_by=admin_id,
        announcement_type=body.get("type", "info"),
        display_type=body.get("display_type", "banner"),
        inbox_content=body.get("inbox_content"),
        show_from=body.get("show_from"),
        show_until=body.get("show_until"),
    )
    # Add priority if provided
    if "priority" in body:
        announcement["priority"] = body["priority"]
        admin_repo.update_announcement(announcement["SK"], {"priority": body["priority"]})
    return {"announcement": announcement}, 201


@app.put("/api/admin/announcements/<announcementId>")
def update_announcement(announcementId: str):
    _require_admin()
    body = app.current_event.json_body or {}

    allowed = {"title", "message", "type", "display_type", "inbox_content", "is_active", "show_from", "show_until", "priority"}
    updates = {k: v for k, v in body.items() if k in allowed}

    announcement = admin_repo.update_announcement(announcementId, updates)
    return {"announcement": announcement}


@app.delete("/api/admin/announcements/<announcementId>")
def delete_announcement(announcementId: str):
    _require_admin()
    admin_repo.delete_announcement(announcementId)
    return {"status": "deleted"}


# --- Feedback ---

@app.get("/api/admin/feedback")
def list_feedback():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    status = params.get("status")
    category = params.get("category")

    feedback = admin_repo.get_feedback(status_filter=status, category_filter=category)
    return {"feedback": feedback}


@app.put("/api/admin/feedback/<feedbackId>")
def update_feedback(feedbackId: str):
    _require_admin()
    body = app.current_event.json_body or {}

    allowed = {"status", "admin_notes"}
    updates = {k: v for k, v in body.items() if k in allowed}

    # feedbackId is the SK value
    result = admin_repo.update_feedback(feedbackId, updates)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_feedback", "feedback", feedbackId, details=json.dumps(updates))

    return {"feedback": result}


@app.delete("/api/admin/feedback/<feedbackId>")
def delete_feedback(feedbackId: str):
    _require_admin()
    table = get_table("admin")
    table.delete_item(Key={"PK": "FEEDBACK", "SK": f"FEEDBACK#{feedbackId}"})
    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "delete_feedback", "feedback", feedbackId)
    return {"status": "deleted"}


@app.post("/api/admin/feedback/bulk")
def bulk_feedback_action():
    _require_admin()
    body = app.current_event.json_body or {}
    action = body.get("action")
    admin_id = get_user_id(app.current_event.raw_event)

    if action == "archive_completed":
        feedback = admin_repo.get_feedback(status_filter="completed")
        table = get_table("admin")
        for item in feedback:
            sk = item.get("SK") or f"FEEDBACK#{item.get('feedback_id', '')}"
            table.update_item(
                Key={"PK": "FEEDBACK", "SK": sk},
                UpdateExpression="SET #s = :status",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":status": "archive"},
            )
        admin_repo.log_audit(admin_id, "admin", "bulk_archive_feedback", details=f"Archived {len(feedback)} completed items")
        return {"status": "ok", "count": len(feedback)}

    elif action == "empty_archive":
        feedback = admin_repo.get_feedback(status_filter="archive")
        table = get_table("admin")
        for item in feedback:
            sk = item.get("SK") or f"FEEDBACK#{item.get('feedback_id', '')}"
            table.delete_item(Key={"PK": "FEEDBACK", "SK": sk})
        admin_repo.log_audit(admin_id, "admin", "empty_feedback_archive", details=f"Deleted {len(feedback)} archived items")
        return {"status": "ok", "count": len(feedback)}

    elif action == "delete_all":
        feedback = admin_repo.get_feedback()
        table = get_table("admin")
        for item in feedback:
            sk = item.get("SK") or f"FEEDBACK#{item.get('feedback_id', '')}"
            table.delete_item(Key={"PK": "FEEDBACK", "SK": sk})
        admin_repo.log_audit(admin_id, "admin", "delete_all_feedback", details=f"Deleted {len(feedback)} feedback items")
        return {"status": "ok", "count": len(feedback), "message": f"Deleted {len(feedback)} feedback items"}

    return {"error": "Unknown action"}, 400


# --- Stats (richer than metrics) ---

@app.get("/api/admin/stats")
def get_admin_stats():
    _require_admin()
    users = user_repo.list_users(limit=1000)
    real_users = [u for u in users if not u.get("is_test_account")]
    test_accounts = len(users) - len(real_users)
    active_users = sum(1 for u in real_users if u.get("is_active"))

    ai_settings = ai_repo.get_ai_settings()
    feedback = admin_repo.get_feedback()
    announcements = admin_repo.get_announcements(active_only=True)

    # Count profiles and heroes (exclude test accounts)
    total_profiles = 0
    total_heroes = 0
    ai_requests_today = 0
    for u in real_users:
        ai_requests_today += u.get("ai_requests_today", 0)
        try:
            profiles = profile_repo.get_profiles(u["user_id"])
            total_profiles += len(profiles)
            for p in profiles:
                profile_id = p.get("SK", "").replace("PROFILE#", "") or p.get("profile_id", "")
                if profile_id:
                    try:
                        heroes = hero_repo.get_heroes(profile_id)
                        total_heroes += len(heroes)
                    except Exception:
                        pass
        except Exception:
            pass

    return {
        "total_users": len(real_users),
        "active_users": active_users,
        "test_accounts": test_accounts,
        "total_profiles": total_profiles,
        "total_heroes_tracked": total_heroes,
        "ai_requests_today": ai_requests_today,
        "pending_feedback": sum(1 for f in feedback if f.get("status") in ("new", "pending_fix", "pending_update")),
        "active_announcements": len(announcements),
        "ai_mode": ai_settings.get("mode", "off"),
    }


# --- Usage Reports ---

@app.get("/api/admin/usage/stats")
def get_usage_stats():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    date_range = params.get("range", "7d")

    days = {"7d": 7, "30d": 30, "90d": 90}.get(date_range, 7)

    all_users = user_repo.list_users(limit=1000)
    users = [u for u in all_users if not u.get("is_test_account")]
    total_users = len(users)
    active_users = sum(1 for u in users if u.get("is_active"))
    now = datetime.now(timezone.utc)

    # Classify user activity
    very_active = 0
    active_weekly = 0
    active_monthly = 0
    inactive = 0
    new_users = 0

    for u in users:
        last_login = u.get("last_login")
        created_at = u.get("created_at")

        # Count new users in date range
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if (now - created).days <= days:
                    new_users += 1
            except Exception:
                pass

        if not last_login:
            inactive += 1
            continue

        try:
            last = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
            days_since = (now - last).days
        except Exception:
            inactive += 1
            continue

        if days_since <= 1:
            very_active += 1
        elif days_since <= 7:
            active_weekly += 1
        elif days_since <= 30:
            active_monthly += 1
        else:
            inactive += 1

    # Content stats - profiles, heroes, inventory
    total_profiles = 0
    total_heroes = 0
    total_inventory = 0
    hero_name_counter = Counter()
    hero_class_counter = Counter()
    spending_counter = Counter()
    alliance_role_counter = Counter()
    state_counter = Counter()
    users_with_state = 0
    users_without_state = 0

    # User activity list
    user_activity_list = []

    for u in users:
        uid = u.get("user_id")
        user_heroes_count = 0
        user_items_count = 0
        user_has_state = False

        try:
            profiles = profile_repo.get_profiles(uid) if uid else []
            total_profiles += len(profiles)

            for p in profiles:
                profile_id = p.get("SK", "").replace("PROFILE#", "") or p.get("profile_id", "")
                state_num = p.get("state_number")
                if state_num:
                    state_counter[state_num] += 1
                    user_has_state = True

                spending = p.get("spending_profile")
                if spending:
                    spending_counter[spending] += 1

                alliance_role = p.get("alliance_role")
                if alliance_role:
                    alliance_role_counter[alliance_role] += 1

                if profile_id:
                    try:
                        heroes = hero_repo.get_heroes(profile_id)
                        total_heroes += len(heroes)
                        user_heroes_count += len(heroes)
                        for h in heroes:
                            hname = h.get("SK", "").replace("HERO#", "") or h.get("hero_name", "")
                            if hname:
                                hero_name_counter[hname] += 1
                            hclass = h.get("hero_class")
                            if hclass:
                                hero_class_counter[hclass] += 1
                    except Exception:
                        pass
        except Exception:
            pass

        if user_has_state:
            users_with_state += 1
        else:
            users_without_state += 1

        # Activity score: rough heuristic based on login recency
        activity_score = 0
        last_login = u.get("last_login")
        if last_login:
            try:
                last = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
                days_since_login = (now - last).days
                if days_since_login == 0:
                    activity_score = 7
                elif days_since_login <= 1:
                    activity_score = 6
                elif days_since_login <= 3:
                    activity_score = 5
                elif days_since_login <= 7:
                    activity_score = 3
                elif days_since_login <= 14:
                    activity_score = 2
                elif days_since_login <= 30:
                    activity_score = 1
            except Exception:
                pass

        user_activity_list.append({
            "username": u.get("username", u.get("email", "unknown")),
            "email": u.get("email", ""),
            "heroes": user_heroes_count,
            "items": user_items_count,
            "activity_score": activity_score,
            "last_login": u.get("last_login"),
        })

    # Build top_heroes (sorted by count, top 15)
    top_heroes = [{"name": name, "count": count} for name, count in hero_name_counter.most_common(15)]

    # Build hero_classes
    hero_classes = dict(hero_class_counter)

    # Build spending_distribution
    spending_distribution = dict(spending_counter)

    # Build alliance_roles
    alliance_roles = dict(alliance_role_counter)

    # Build top_states (sorted by count)
    top_states = [{"state": state, "count": count} for state, count in state_counter.most_common()]

    unique_states = len(state_counter)

    # Activity rate
    activity_rate = round((active_users / total_users * 100) if total_users else 0, 1)

    # Build data_points from user created_at / last_login timestamps
    from datetime import timedelta

    created_dates: dict[str, int] = {}  # date -> new users
    login_dates: dict[str, int] = {}    # date -> active users

    for u in users:
        ca = u.get("created_at")
        if ca:
            try:
                d = datetime.fromisoformat(ca.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                created_dates[d] = created_dates.get(d, 0) + 1
            except Exception:
                pass
        ll = u.get("last_login")
        if ll:
            try:
                d = datetime.fromisoformat(ll.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                login_dates[d] = login_dates.get(d, 0) + 1
            except Exception:
                pass

    data_points = []
    cumulative = 0
    # Count users created before the range start
    start_dt = now - timedelta(days=days)
    for u in users:
        ca = u.get("created_at")
        if ca:
            try:
                created = datetime.fromisoformat(ca.replace("Z", "+00:00"))
                if created < start_dt:
                    cumulative += 1
            except Exception:
                pass

    for i in range(days):
        day = (start_dt + timedelta(days=i + 1))
        day_str = day.strftime("%Y-%m-%d")
        new_on_day = created_dates.get(day_str, 0)
        cumulative += new_on_day
        data_points.append({
            "date": day_str,
            "total_users": cumulative,
            "active_users": login_dates.get(day_str, 0),
            "new_users": new_on_day,
        })

    # Extract daily_active_users as simple number array for the DAU chart
    daily_active_users = [dp["active_users"] for dp in data_points]

    # Add heroes_tracked to each data point for the historical view
    historical = [{**dp, "heroes_tracked": 0} for dp in data_points]

    return {
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "new_users": new_users,
            "activity_rate": activity_rate,
        },
        "activity_breakdown": {
            "very_active": very_active,
            "active_weekly": active_weekly,
            "active_monthly": active_monthly,
            "inactive": inactive,
        },
        "content": {
            "profiles": total_profiles,
            "heroes": total_heroes,
            "inventory": total_inventory,
        },
        "top_heroes": top_heroes,
        "hero_classes": hero_classes,
        "spending_distribution": spending_distribution,
        "alliance_roles": alliance_roles,
        "top_states": top_states,
        "states_summary": {
            "unique_states": unique_states,
            "users_with_state": users_with_state,
            "users_without_state": users_without_state,
        },
        "daily_active_users": daily_active_users,
        "historical": historical,
        "ai_usage": [],
        "user_activity": user_activity_list,
    }


# --- Feature Flags (additional routes) ---

@app.post("/api/admin/flags")
def create_flag():
    _require_admin()
    body = app.current_event.json_body or {}
    name = body.get("name")
    if not name:
        raise ValidationError("Flag name is required")

    flag = admin_repo.create_feature_flag(
        name=name,
        description=body.get("description"),
        is_enabled=body.get("is_enabled", False),
    )

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "create_flag", "flag", name)
    return {"flag": flag}, 201


@app.delete("/api/admin/flags/<flagName>")
def delete_flag(flagName: str):
    _require_admin()
    admin_repo.delete_feature_flag(flagName)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "delete_flag", "flag", flagName)
    return {"status": "deleted"}


@app.post("/api/admin/flags/bulk")
def bulk_flag_action():
    _require_admin()
    body = app.current_event.json_body or {}
    action = body.get("action")

    if action not in ("enable_all", "disable_all", "reset_defaults"):
        raise ValidationError("Invalid bulk action")

    admin_repo.bulk_flag_action(action)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "bulk_flag_action", details=action)
    return {"status": "ok", "action": action}


# Feature flag alias routes (frontend uses /api/admin/feature-flags)
@app.get("/api/admin/feature-flags")
def list_flags_alias():
    return list_flags()


@app.put("/api/admin/feature-flags/<flagName>")
def update_flag_alias(flagName: str):
    return update_flag(flagName)


@app.post("/api/admin/feature-flags")
def create_flag_alias():
    return create_flag()


@app.delete("/api/admin/feature-flags/<flagName>")
def delete_flag_alias(flagName: str):
    return delete_flag(flagName)


@app.post("/api/admin/feature-flags/bulk")
def bulk_flag_action_alias():
    return bulk_flag_action()


# --- Errors ---

@app.get("/api/admin/errors")
def get_errors():
    _require_admin()
    errors = admin_repo.get_errors(limit=200)
    return {"errors": errors}


@app.post("/api/admin/errors/<errorId>/resolve")
def resolve_error(errorId: str):
    _require_admin()
    item = admin_repo._find_error_by_id(errorId)
    if not item:
        raise NotFoundError(f"Error {errorId} not found")
    table = get_table("admin")
    table.update_item(
        Key={"PK": "ERRORS", "SK": item["SK"]},
        UpdateExpression="SET #s = :resolved, #r = :true_val",
        ExpressionAttributeNames={"#s": "status", "#r": "resolved"},
        ExpressionAttributeValues={":resolved": "resolved", ":true_val": True},
    )

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "resolve_error", "error", errorId)
    return {"status": "resolved", "resolved": True}


@app.put("/api/admin/errors/<errorId>")
def update_error(errorId: str):
    _require_admin()
    body = app.current_event.json_body or {}
    item = admin_repo._find_error_by_id(errorId)
    if not item:
        raise NotFoundError(f"Error {errorId} not found")
    table = get_table("admin")

    update_parts = []
    names = {}
    values = {}

    if "status" in body:
        update_parts.append("#s = :status")
        names["#s"] = "status"
        values[":status"] = body["status"]
        if body["status"] == "resolved":
            values[":true_val"] = True
            update_parts.append("#r = :true_val")
            names["#r"] = "resolved"

    if "fix_notes" in body:
        update_parts.append("#fn = :fix_notes")
        names["#fn"] = "fix_notes"
        values[":fix_notes"] = body["fix_notes"]

    if update_parts:
        table.update_item(
            Key={"PK": "ERRORS", "SK": item["SK"]},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
        )

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_error", "error", errorId, details=json.dumps(body))
    return {"status": "updated"}


@app.delete("/api/admin/errors/<errorId>")
def delete_error(errorId: str):
    _require_admin()
    item = admin_repo._find_error_by_id(errorId)
    if not item:
        raise NotFoundError(f"Error {errorId} not found")
    table = get_table("admin")
    table.delete_item(Key={"PK": "ERRORS", "SK": item["SK"]})
    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "delete_error", "error", errorId)
    return {"status": "deleted"}


@app.post("/api/admin/errors/<errorId>/diagnose")
def diagnose_error(errorId: str):
    """Use AI to diagnose an error."""
    _require_admin()
    item = admin_repo._find_error_by_id(errorId)
    if not item:
        raise NotFoundError(f"Error {errorId} not found")

    error_type = item.get("error_type", "Unknown")
    error_message = item.get("error_message", "No message")
    stack_trace = item.get("stack_trace", "No stack trace")
    handler = item.get("page", item.get("function", "unknown"))

    prompt = f"""Analyze this application error and provide a diagnosis with suggested fix.

Error Type: {error_type}
Error Message: {error_message}
Handler/Function: {handler}
Environment: {item.get('environment', 'unknown')}

Stack Trace:
{stack_trace}

Provide:
1. Root cause analysis (1-2 sentences)
2. Suggested fix (specific code change if possible)
3. Severity assessment (low/medium/high/critical)
4. Whether this is likely a one-time issue or recurring"""

    diagnosis = None
    try:
        from engine.ai_recommender import AIRecommender
        recommender = AIRecommender(provider="auto")
        if recommender.openai_client:
            response = recommender.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior software engineer diagnosing production errors in a Python/AWS Lambda application using DynamoDB, API Gateway, and Cognito."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=800,
            )
            diagnosis = response.choices[0].message.content.strip()
        elif recommender.anthropic_client:
            response = recommender.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=800,
                system="You are a senior software engineer diagnosing production errors in a Python/AWS Lambda application using DynamoDB, API Gateway, and Cognito.",
                messages=[{"role": "user", "content": prompt}],
            )
            diagnosis = response.content[0].text.strip()
    except Exception as e:
        logger.warning(f"AI diagnosis failed: {e}")
        diagnosis = f"AI diagnosis unavailable: {e}"

    if not diagnosis:
        diagnosis = "No AI provider available. Check API keys in Secrets Manager."

    # Store diagnosis in the error record
    now = datetime.now(timezone.utc).isoformat()
    table = get_table("admin")
    table.update_item(
        Key={"PK": "ERRORS", "SK": item["SK"]},
        UpdateExpression="SET ai_diagnosis = :d, diagnosed_at = :t",
        ExpressionAttributeValues={":d": diagnosis, ":t": now},
    )

    return {"diagnosis": diagnosis, "diagnosed_at": now}


@app.post("/api/admin/errors/bulk")
def bulk_error_action():
    _require_admin()
    body = app.current_event.json_body or {}
    action = body.get("action")
    admin_id = get_user_id(app.current_event.raw_event)

    if action == "delete_ignored":
        table = get_table("admin")
        resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": "ERRORS"},
        )
        count = 0
        for item in resp.get("Items", []):
            if item.get("status") == "ignored":
                table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
                count += 1
        admin_repo.log_audit(admin_id, "admin", "bulk_delete_ignored_errors", details=f"Deleted {count} ignored errors")
        return {"status": "ok", "count": count}

    return {"error": "Unknown action"}, 400


# --- AI Conversations (admin) ---

@app.get("/api/admin/ai-conversations")
def list_ai_conversations():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "50"))

    # Scan all conversations across users via admin table or main table query
    table = get_table("main")
    resp = table.scan(
        FilterExpression="begins_with(SK, :prefix)",
        ExpressionAttributeValues={":prefix": "AICONV#"},
        Limit=limit,
    )
    conversations = resp.get("Items", [])
    conversations.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    # Add routed_to alias for source field (frontend expects routed_to)
    for c in conversations[:limit]:
        c.setdefault("routed_to", c.get("source"))
    return {"conversations": conversations[:limit]}


@app.get("/api/admin/conversations")
def list_conversations_alias():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "50"))
    rating_filter = params.get("rating_filter")
    curation_filter = params.get("curation_filter")
    source_filter = params.get("source_filter")

    table = get_table("main")
    resp = table.scan(
        FilterExpression="begins_with(SK, :prefix)",
        ExpressionAttributeValues={":prefix": "AICONV#"},
        Limit=limit * 3,  # Over-fetch for filtering
    )
    conversations = resp.get("Items", [])

    # Apply filters
    if rating_filter:
        if rating_filter == "rated":
            conversations = [c for c in conversations if c.get("rating") is not None]
        elif rating_filter == "unrated":
            conversations = [c for c in conversations if c.get("rating") is None]
    if curation_filter:
        if curation_filter == "good":
            conversations = [c for c in conversations if c.get("is_good_example")]
        elif curation_filter == "bad":
            conversations = [c for c in conversations if c.get("is_bad_example")]
    if source_filter:
        conversations = [c for c in conversations if c.get("source") == source_filter]

    conversations.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    # Add routed_to alias for source field (frontend expects routed_to)
    for c in conversations[:limit]:
        c.setdefault("routed_to", c.get("source"))
    return {"conversations": conversations[:limit]}


@app.put("/api/admin/conversations/<convId>/curate")
def curate_conversation(convId: str):
    _require_admin()
    body = app.current_event.json_body or {}

    allowed = {"is_good_example", "is_bad_example", "admin_notes"}
    updates = {k: v for k, v in body.items() if k in allowed}

    # Find and update the conversation
    table = get_table("main")
    update_parts = []
    attr_values = {}
    attr_names = {}
    for k, v in updates.items():
        safe_key = f"#{k}"
        val_key = f":{k}"
        update_parts.append(f"{safe_key} = {val_key}")
        attr_names[safe_key] = k
        attr_values[val_key] = v

    if update_parts:
        # convId could be the full SK or just the ID part
        sk = convId if convId.startswith("AICONV#") else f"AICONV#{convId}"

        # We need to find which user owns this - scan for it
        resp = table.scan(
            FilterExpression="SK = :sk",
            ExpressionAttributeValues={":sk": sk},
            Limit=1,
        )
        items = resp.get("Items", [])
        if items:
            table.update_item(
                Key={"PK": items[0]["PK"], "SK": sk},
                UpdateExpression="SET " + ", ".join(update_parts),
                ExpressionAttributeNames=attr_names,
                ExpressionAttributeValues=attr_values,
            )

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "curate_conversation", "conversation", convId, details=json.dumps(updates))
    return {"status": "updated"}


@app.get("/api/admin/conversations/stats")
def get_conversation_stats():
    _require_admin()
    table = get_table("main")
    resp = table.scan(
        FilterExpression="begins_with(SK, :prefix)",
        ExpressionAttributeValues={":prefix": "AICONV#"},
    )
    conversations = resp.get("Items", [])

    total = len(conversations)
    ai_count = sum(1 for c in conversations if c.get("source") == "ai")
    rules_count = sum(1 for c in conversations if c.get("source") == "rules")
    rated = sum(1 for c in conversations if c.get("rating") is not None)
    helpful = sum(1 for c in conversations if c.get("is_helpful") is True)
    good_examples = sum(1 for c in conversations if c.get("is_good_example"))
    bad_examples = sum(1 for c in conversations if c.get("is_bad_example"))

    return {
        "total": total,
        "ai": ai_count,
        "rules": rules_count,
        "ai_routed": ai_count,
        "rules_routed": rules_count,
        "ai_percentage": round((ai_count / total * 100) if total else 0, 1),
        "rated": rated,
        "helpful": helpful,
        "unhelpful": sum(1 for c in conversations if c.get("is_helpful") is False),
        "good_examples": good_examples,
        "bad_examples": bad_examples,
    }


@app.get("/api/admin/conversations/export")
def export_conversations():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    fmt = params.get("format", "jsonl")
    filter_type = params.get("filter")

    table = get_table("main")
    resp = table.scan(
        FilterExpression="begins_with(SK, :prefix)",
        ExpressionAttributeValues={":prefix": "AICONV#"},
    )
    conversations = resp.get("Items", [])

    if filter_type == "good":
        conversations = [c for c in conversations if c.get("is_good_example")]
    elif filter_type == "bad":
        conversations = [c for c in conversations if c.get("is_bad_example")]
    elif filter_type == "rated":
        conversations = [c for c in conversations if c.get("rating") is not None]

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "export_conversations", details=f"format={fmt}, filter={filter_type}")

    if fmt == "csv":
        if not conversations:
            return {"csv": "", "count": 0}
        headers = ["question", "answer", "source", "provider", "model", "rating", "is_helpful", "created_at"]
        lines = [",".join(headers)]
        for c in conversations:
            row = [str(c.get(h, "")).replace(",", ";").replace("\n", " ") for h in headers]
            lines.append(",".join(row))
        return {"csv": "\n".join(lines), "count": len(conversations)}

    # JSONL format
    lines = [json.dumps({"question": c.get("question", ""), "answer": c.get("answer", ""), "source": c.get("source", ""), "rating": c.get("rating")}) for c in conversations]
    return {"data": "\n".join(lines), "count": len(conversations), "format": fmt}


# Alias for frontend path /api/admin/ai/conversations
@app.get("/api/admin/ai/conversations")
def ai_conversations_alias():
    return list_conversations_alias()


@app.put("/api/admin/ai/conversations/<convId>")
def ai_curate_alias(convId: str):
    return curate_conversation(convId)


@app.get("/api/admin/ai/export")
def ai_export_alias():
    return export_conversations()


# --- Data Integrity ---

@app.get("/api/admin/data-integrity/check")
def check_data_integrity():
    _require_admin()
    results = []
    table = get_table("main")

    # 1. Orphaned Profiles - profiles whose user has no METADATA
    try:
        profile_resp = table.scan(
            FilterExpression="begins_with(SK, :prof)",
            ExpressionAttributeValues={":prof": "PROFILE#"},
        )
        orphaned_profiles = []
        for item in profile_resp.get("Items", []):
            user_pk = item["PK"]
            meta = table.get_item(Key={"PK": user_pk, "SK": "METADATA"}).get("Item")
            if not meta:
                orphaned_profiles.append(f"{user_pk}/{item['SK']}")
        count = len(orphaned_profiles)
        results.append({
            "name": "Orphaned Profiles",
            "description": "Profiles without a matching user record",
            "status": "fail" if count > 0 else "pass",
            "details": f"{count} orphaned profile(s) found" if count else "All profiles have valid users",
            "count": count,
            "affected_ids": orphaned_profiles[:20],
            "severity": "high",
            "fix_action": "clean_orphaned_profiles",
        })
    except Exception as e:
        results.append({"name": "Orphaned Profiles", "description": "Profiles without a matching user record",
                        "status": "warn", "details": f"Check failed: {e}", "count": 0, "severity": "high"})

    # 2. Users Without Profiles
    try:
        user_resp = table.scan(
            FilterExpression="SK = :meta AND begins_with(PK, :u)",
            ExpressionAttributeValues={":meta": "METADATA", ":u": "USER#"},
        )
        no_profile = []
        for item in user_resp.get("Items", []):
            user_pk = item["PK"]
            prof = table.query(
                KeyConditionExpression="PK = :pk AND begins_with(SK, :prof)",
                ExpressionAttributeValues={":pk": user_pk, ":prof": "PROFILE#"},
                Limit=1,
            )
            if not prof.get("Items"):
                no_profile.append(item.get("email", user_pk))
        count = len(no_profile)
        results.append({
            "name": "Users Without Profiles",
            "description": "Users who have no profile record",
            "status": "warn" if count > 0 else "pass",
            "details": f"{count} user(s) without profiles" if count else "All users have profiles",
            "count": count,
            "affected_ids": no_profile[:20],
            "severity": "medium",
        })
    except Exception as e:
        results.append({"name": "Users Without Profiles", "description": "Users who have no profile record",
                        "status": "warn", "details": f"Check failed: {e}", "count": 0, "severity": "medium"})

    # 3. Invalid Hero References - heroes with names not in heroes.json
    try:
        valid_heroes = set()
        heroes_data = hero_repo.get_all_heroes_reference()
        for h in heroes_data:
            valid_heroes.add(h.get("name", "").lower())

        hero_resp = table.scan(
            FilterExpression="begins_with(PK, :prof) AND begins_with(SK, :hero)",
            ExpressionAttributeValues={":prof": "PROFILE#", ":hero": "HERO#"},
        )
        invalid_refs = []
        for item in hero_resp.get("Items", []):
            hero_name = item.get("hero_name", item.get("name", ""))
            if hero_name and hero_name.lower() not in valid_heroes:
                invalid_refs.append(f"{hero_name} ({item['PK']})")
        count = len(invalid_refs)
        results.append({
            "name": "Invalid Hero References",
            "description": "User heroes referencing names not in heroes.json",
            "status": "fail" if count > 0 else "pass",
            "details": f"{count} invalid hero reference(s)" if count else "All hero references are valid",
            "count": count,
            "affected_ids": invalid_refs[:20],
            "severity": "high",
        })
    except Exception as e:
        results.append({"name": "Invalid Hero References", "description": "User heroes referencing names not in heroes.json",
                        "status": "warn", "details": f"Check failed: {e}", "count": 0, "severity": "high"})

    # 4. Hero Values Out of Range
    try:
        hero_resp = table.scan(
            FilterExpression="begins_with(PK, :prof) AND begins_with(SK, :hero)",
            ExpressionAttributeValues={":prof": "PROFILE#", ":hero": "HERO#"},
        )
        out_of_range = []
        for item in hero_resp.get("Items", []):
            issues = []
            if item.get("level", 0) > 80:
                issues.append(f"level={item['level']}")
            if item.get("stars", 0) > 5:
                issues.append(f"stars={item['stars']}")
            for sk in ["exploration_skill_1_level", "exploration_skill_2_level", "exploration_skill_3_level",
                        "expedition_skill_1_level", "expedition_skill_2_level", "expedition_skill_3_level"]:
                if item.get(sk, 0) > 5:
                    issues.append(f"{sk}={item[sk]}")
            for gq in ["gear_slot1_quality", "gear_slot2_quality", "gear_slot3_quality", "gear_slot4_quality"]:
                if item.get(gq, 0) > 7:
                    issues.append(f"{gq}={item[gq]}")
            if issues:
                hero_name = item.get("hero_name", item.get("name", "unknown"))
                out_of_range.append(f"{hero_name}: {', '.join(issues)}")
        count = len(out_of_range)
        results.append({
            "name": "Hero Values Out of Range",
            "description": "Heroes with stats exceeding valid maximums",
            "status": "warn" if count > 0 else "pass",
            "details": f"{count} hero(es) with out-of-range values" if count else "All hero values within valid ranges",
            "count": count,
            "affected_ids": out_of_range[:20],
            "severity": "medium",
            "fix_action": "fix_hero_ranges",
        })
    except Exception as e:
        results.append({"name": "Hero Values Out of Range", "description": "Heroes with stats exceeding valid maximums",
                        "status": "warn", "details": f"Check failed: {e}", "count": 0, "severity": "medium"})

    # 5. Game Data Files on Lambda filesystem
    try:
        data_dir = Config.DATA_DIR
        json_count = 0
        missing_core = []
        core_files = ["heroes.json", "events.json", "chief_gear.json", "vip_system.json"]
        for fname in core_files:
            fpath = os.path.join(data_dir, fname)
            if not os.path.exists(fpath):
                missing_core.append(fname)
        for root, dirs, filenames in os.walk(data_dir):
            json_count += sum(1 for f in filenames if f.endswith(".json"))
        if missing_core:
            status = "fail"
            details = f"Missing core files: {', '.join(missing_core)}. {json_count} total JSON files."
        elif json_count < 10:
            status = "warn"
            details = f"Only {json_count} JSON files found (expected 10+)"
        else:
            status = "pass"
            details = f"{json_count} JSON data files present, all core files found"
        results.append({
            "name": "Game Data Files",
            "description": "Core JSON data files on Lambda filesystem",
            "status": status,
            "details": details,
            "count": json_count,
            "affected_ids": missing_core,
            "severity": "low",
        })
    except Exception as e:
        results.append({"name": "Game Data Files", "description": "Core JSON data files on Lambda filesystem",
                        "status": "warn", "details": f"Check failed: {e}", "count": 0, "severity": "low"})

    return {"checks": results, "total": len(results), "passing": sum(1 for r in results if r["status"] == "pass")}


# --- Game Data ---

@app.get("/api/admin/game-data/files")
def list_game_data_files():
    _require_admin()
    data_dir = Config.DATA_DIR
    files = []

    for root, dirs, filenames in os.walk(data_dir):
        for fname in filenames:
            if fname.endswith(".json"):
                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, data_dir)

                # Infer category from subdirectory
                parts = rel_path.replace("\\", "/").split("/")
                category = parts[0] if len(parts) > 1 else "core"

                # Get modified time
                try:
                    mtime = os.path.getmtime(fpath)
                    modified_at = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
                except Exception:
                    modified_at = None

                files.append({
                    "path": rel_path,
                    "name": fname,
                    "size_bytes": os.path.getsize(fpath),
                    "modified_at": modified_at,
                    "category": category,
                })

    files.sort(key=lambda f: f["path"])
    return {"files": files}


@app.get("/api/admin/game-data/file")
def get_game_data_file():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    rel_path = params.get("path")
    if not rel_path:
        raise ValidationError("path parameter is required")

    # Validate path stays within data directory
    data_dir = Config.DATA_DIR
    full_path = os.path.normpath(os.path.join(data_dir, rel_path))
    if not full_path.startswith(os.path.normpath(data_dir)):
        raise ValidationError("Invalid file path")

    if not os.path.exists(full_path):
        raise NotFoundError(f"File not found: {rel_path}")

    with open(full_path, encoding="utf-8") as f:
        content = json.load(f)

    return {"path": rel_path, "content": content}


@app.put("/api/admin/game-data/file")
def save_game_data_file():
    _require_admin()
    body = app.current_event.json_body or {}
    rel_path = body.get("path")
    content = body.get("content")

    if not rel_path:
        raise ValidationError("path is required")
    if content is None:
        raise ValidationError("content is required")

    data_dir = Config.DATA_DIR
    full_path = os.path.normpath(os.path.join(data_dir, rel_path))
    if not full_path.startswith(os.path.normpath(data_dir)):
        raise ValidationError("Invalid file path")

    if not os.path.exists(full_path):
        raise NotFoundError(f"File not found: {rel_path}")

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

    # Clear hero cache if heroes.json was modified
    if "heroes.json" in rel_path:
        hero_repo._heroes_cache = None

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "save_game_data", details=f"path={rel_path}")

    return {"status": "saved", "path": rel_path}


@app.post("/api/admin/data-integrity/fix/<action>")
def fix_integrity_issue(action: str):
    _require_admin()

    valid_actions = ("rebuild_hero_cache", "clean_orphaned_profiles", "clean_orphaned_heroes", "fix_hero_ranges")
    if action not in valid_actions:
        raise ValidationError(f"Invalid action. Must be one of: {', '.join(valid_actions)}")

    fixed = 0
    table = get_table("main")

    if action == "rebuild_hero_cache":
        hero_repo._heroes_cache = None
        fixed = 1

    elif action == "clean_orphaned_profiles":
        # Find profiles whose user doesn't exist
        resp = table.scan(
            FilterExpression="begins_with(SK, :prof)",
            ExpressionAttributeValues={":prof": "PROFILE#"},
        )
        for item in resp.get("Items", []):
            user_pk = item["PK"]  # USER#xxx
            meta = table.get_item(Key={"PK": user_pk, "SK": "METADATA"}).get("Item")
            if not meta:
                table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
                fixed += 1

    elif action == "clean_orphaned_heroes":
        # Find heroes whose profile doesn't exist
        resp = table.scan(
            FilterExpression="begins_with(PK, :prof) AND begins_with(SK, :hero)",
            ExpressionAttributeValues={":prof": "PROFILE#", ":hero": "HERO#"},
        )
        for item in resp.get("Items", []):
            profile_pk = item["PK"]  # PROFILE#xxx
            profile_id = profile_pk.replace("PROFILE#", "")
            # Check if any user has this profile
            user_resp = table.scan(
                FilterExpression="begins_with(SK, :prefix) AND profile_id = :pid",
                ExpressionAttributeValues={":prefix": "PROFILE#", ":pid": profile_id},
                Limit=1,
            )
            if not user_resp.get("Items"):
                table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
                fixed += 1

    elif action == "fix_hero_ranges":
        # Clamp out-of-range hero values
        resp = table.scan(
            FilterExpression="begins_with(PK, :prof) AND begins_with(SK, :hero)",
            ExpressionAttributeValues={":prof": "PROFILE#", ":hero": "HERO#"},
        )
        for item in resp.get("Items", []):
            updates = {}
            if item.get("level", 0) > 80:
                updates["level"] = 80
            if item.get("stars", 0) > 5:
                updates["stars"] = 5
            for skill_key in ["exploration_skill_1_level", "exploration_skill_2_level", "exploration_skill_3_level",
                              "expedition_skill_1_level", "expedition_skill_2_level", "expedition_skill_3_level"]:
                if item.get(skill_key, 0) > 5:
                    updates[skill_key] = 5
            for gq_key in ["gear_slot1_quality", "gear_slot2_quality", "gear_slot3_quality", "gear_slot4_quality"]:
                if item.get(gq_key, 0) > 7:
                    updates[gq_key] = 7
            if updates:
                expr_parts = [f"#{k} = :{k}" for k in updates]
                table.update_item(
                    Key={"PK": item["PK"], "SK": item["SK"]},
                    UpdateExpression="SET " + ", ".join(expr_parts),
                    ExpressionAttributeNames={f"#{k}": k for k in updates},
                    ExpressionAttributeValues={f":{k}": v for k, v in updates.items()},
                )
                fixed += 1

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", f"integrity_fix_{action}", details=f"fixed={fixed}")

    return {"message": f"Action '{action}' completed", "fixed": fixed}


# --- Data Browser ---

# Entity type definitions: maps entity name -> (table_alias, pk_pattern, sk_pattern, display_columns)
ENTITY_TYPES = {
    "users": {
        "table": "main", "pk_prefix": "USER#", "sk_value": "METADATA",
        "columns": ["email", "role", "is_active", "created_at", "last_login", "ai_requests_today"],
        "label": "Users",
    },
    "profiles": {
        "table": "main", "pk_prefix": "USER#", "sk_prefix": "PROFILE#",
        "columns": ["profile_id", "name", "state_number", "furnace_level", "spending_profile", "alliance_role"],
        "label": "Profiles",
    },
    "heroes": {
        "table": "main", "pk_prefix": "PROFILE#", "sk_prefix": "HERO#",
        "columns": ["hero_name", "level", "stars", "ascension", "gear_slot_1_quality", "gear_slot_2_quality"],
        "label": "Heroes",
    },
    "ai_conversations": {
        "table": "main", "pk_prefix": "USER#", "sk_prefix": "AICONV#",
        "columns": ["question", "source", "provider", "model", "created_at"],
        "label": "AI Conversations",
    },
    "feedback": {
        "table": "admin", "pk_value": "FEEDBACK", "sk_prefix": "",
        "columns": ["category", "description", "status", "user_email", "created_at"],
        "label": "Feedback",
    },
    "errors": {
        "table": "admin", "pk_value": "ERRORS", "sk_prefix": "",
        "columns": ["error_type", "error_message", "status", "page", "created_at"],
        "label": "Errors",
    },
    "feature_flags": {
        "table": "admin", "pk_value": "FLAG", "sk_prefix": "",
        "columns": ["name", "is_enabled", "description", "updated_at"],
        "label": "Feature Flags",
    },
    "audit_log": {
        "table": "admin", "pk_prefix": "AUDIT#", "sk_prefix": "",
        "columns": ["action", "admin_username", "target", "details", "created_at"],
        "label": "Audit Log",
    },
}


@app.get("/api/admin/database/entities")
def list_entities():
    """List all entity types with row counts."""
    _require_admin()
    entities = []
    for key, cfg in ENTITY_TYPES.items():
        try:
            count = _count_entity(cfg)
        except Exception:
            count = -1
        entities.append({
            "id": key,
            "label": cfg["label"],
            "table": cfg["table"],
            "row_count": count,
            "columns": cfg["columns"],
        })
    return {"entities": entities}


def _count_entity(cfg: dict) -> int:
    """Count items matching an entity type's PK/SK pattern."""
    table = get_table(cfg["table"])
    if "pk_value" in cfg:
        resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": cfg["pk_value"]},
            Select="COUNT",
        )
        return resp.get("Count", 0)
    # For prefix-based patterns, use scan with filter
    filter_parts = []
    expr_vals = {}
    if "pk_prefix" in cfg:
        filter_parts.append("begins_with(PK, :pkp)")
        expr_vals[":pkp"] = cfg["pk_prefix"]
    if cfg.get("sk_value"):
        filter_parts.append("SK = :skv")
        expr_vals[":skv"] = cfg["sk_value"]
    elif cfg.get("sk_prefix"):
        filter_parts.append("begins_with(SK, :skp)")
        expr_vals[":skp"] = cfg["sk_prefix"]
    resp = table.scan(
        FilterExpression=" AND ".join(filter_parts),
        ExpressionAttributeValues=expr_vals,
        Select="COUNT",
    )
    return resp.get("Count", 0)


@app.get("/api/admin/database/entities/<entityId>")
def browse_entity(entityId: str):
    """Browse items of a specific entity type with human-readable columns."""
    _require_admin()
    if entityId not in ENTITY_TYPES:
        raise ValidationError(f"Unknown entity: {entityId}")

    cfg = ENTITY_TYPES[entityId]
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "100"))

    table = get_table(cfg["table"])
    items = _query_entity(table, cfg, limit)

    # Project to display columns only (plus PK/SK for identification)
    display_cols = cfg["columns"]
    rows = []
    for item in items:
        row = {"_pk": item.get("PK", ""), "_sk": item.get("SK", "")}
        for col in display_cols:
            val = item.get(col)
            if col == "question" and isinstance(val, str) and len(val) > 120:
                val = val[:120] + "..."
            if col == "error_message" and isinstance(val, str) and len(val) > 200:
                val = val[:200] + "..."
            row[col] = val
        rows.append(row)

    return {"entity": entityId, "label": cfg["label"], "columns": display_cols, "items": rows, "count": len(rows)}


def _query_entity(table, cfg: dict, limit: int) -> list:
    """Query items matching an entity type's PK/SK pattern."""
    if "pk_value" in cfg:
        resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": cfg["pk_value"]},
            ScanIndexForward=False,
            Limit=limit,
        )
        return resp.get("Items", [])
    filter_parts = []
    expr_vals = {}
    if "pk_prefix" in cfg:
        filter_parts.append("begins_with(PK, :pkp)")
        expr_vals[":pkp"] = cfg["pk_prefix"]
    if cfg.get("sk_value"):
        filter_parts.append("SK = :skv")
        expr_vals[":skv"] = cfg["sk_value"]
    elif cfg.get("sk_prefix"):
        filter_parts.append("begins_with(SK, :skp)")
        expr_vals[":skp"] = cfg["sk_prefix"]
    resp = table.scan(
        FilterExpression=" AND ".join(filter_parts),
        ExpressionAttributeValues=expr_vals,
        Limit=limit,
    )
    return resp.get("Items", [])


# Keep legacy endpoints for backwards compat during transition
@app.get("/api/admin/database/tables")
def list_tables():
    _require_admin()
    return {
        "tables": [
            {"name": Config.MAIN_TABLE, "alias": "main"},
            {"name": Config.ADMIN_TABLE, "alias": "admin"},
            {"name": Config.REFERENCE_TABLE, "alias": "reference"},
        ]
    }


@app.get("/api/admin/database/tables/<tableName>")
def scan_table(tableName: str):
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "25"))

    alias_map = {"main": Config.MAIN_TABLE, "admin": Config.ADMIN_TABLE, "reference": Config.REFERENCE_TABLE}
    actual_name = alias_map.get(tableName, tableName)
    valid_tables = {Config.MAIN_TABLE, Config.ADMIN_TABLE, Config.REFERENCE_TABLE}
    if actual_name not in valid_tables:
        raise ValidationError(f"Unknown table: {tableName}")

    table = get_table(actual_name)
    resp = table.scan(Limit=limit)
    items = resp.get("Items", [])
    return {"table": actual_name, "items": items, "count": len(items)}


# --- Export ---

@app.get("/api/admin/export/<format>")
def export_data(format: str):
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    table_name = params.get("table", "main")

    # Normalize format: excel -> csv, jsonl -> json
    format_lower = format.lower()
    if format_lower == "excel":
        format_lower = "csv"
    if format_lower not in ("json", "csv", "jsonl"):
        raise ValidationError("Format must be json, csv, excel, or jsonl")

    # Map human-readable table names to actual table aliases
    table_alias_map = {
        "users": "main",
        "heroes": "main",
        "ai_conversations": "main",
        "feedback": "admin",
        "audit_log": "admin",
        "game_data": "reference",
    }
    resolved_alias = table_alias_map.get(table_name, table_name)

    alias_map = {
        "main": Config.MAIN_TABLE,
        "admin": Config.ADMIN_TABLE,
        "reference": Config.REFERENCE_TABLE,
    }
    actual_name = alias_map.get(resolved_alias, resolved_alias)

    valid_tables = {Config.MAIN_TABLE, Config.ADMIN_TABLE, Config.REFERENCE_TABLE}
    if actual_name not in valid_tables:
        raise ValidationError(f"Unknown table: {table_name}")

    table = get_table(actual_name)

    # Apply prefix filter for specific table names
    prefix_map = {
        "users": "USER#",
        "heroes": "PROFILE#",
        "ai_conversations": "AICONV#",
        "feedback": "FEEDBACK",
        "audit_log": "AUDIT#",
    }
    prefix = prefix_map.get(table_name)

    if prefix and prefix.endswith("#"):
        # SK-based prefix filter
        resp = table.scan(
            FilterExpression="begins_with(SK, :prefix)",
            ExpressionAttributeValues={":prefix": prefix},
        )
    elif prefix:
        # PK-based prefix filter
        resp = table.scan(
            FilterExpression="begins_with(PK, :prefix)",
            ExpressionAttributeValues={":prefix": prefix},
        )
    else:
        resp = table.scan()

    items = resp.get("Items", [])

    if format_lower == "json":
        return {"table": actual_name, "items": items, "count": len(items)}

    if format_lower == "jsonl":
        # JSONL: one JSON object per line
        lines = [json.dumps(item, default=str) for item in items]
        admin_id = get_user_id(app.current_event.raw_event)
        admin_repo.log_audit(admin_id, "admin", "export_data", "table", actual_name, details=f"format={format}")
        return {"data": "\n".join(lines), "count": len(items), "format": "jsonl"}

    # CSV format
    if not items:
        return {"csv": "", "count": 0}

    all_keys = set()
    for item in items:
        all_keys.update(item.keys())
    headers = sorted(all_keys)

    lines = [",".join(headers)]
    for item in items:
        row = [str(item.get(h, "")).replace(",", ";").replace("\n", " ") for h in headers]
        lines.append(",".join(row))

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "export_data", "table", actual_name, details=f"format={format}")

    return {"csv": "\n".join(lines), "count": len(items)}


# --- Admin Message Threads ---

@app.get("/api/admin/threads")
def list_admin_threads():
    """List all message threads (admin sees all users' threads)."""
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "50"))

    table = get_table("admin")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": "THREADS",
            ":prefix": "THREAD#",
        },
        ScanIndexForward=False,
    )
    threads = resp.get("Items", [])

    # Enrich threads with username
    for t in threads:
        uid = t.get("user_id")
        if uid:
            u = user_repo.get_user(uid)
            t["username"] = u.get("username") or u.get("email", "Unknown") if u else "Unknown"
        else:
            t["username"] = "Unknown"
        # Extract thread_id from SK
        sk = t.get("SK", "")
        t["thread_id"] = sk.replace("THREAD#", "") if sk.startswith("THREAD#") else sk

    # Sort by updated_at descending
    threads.sort(key=lambda t: t.get("updated_at", t.get("created_at", "")), reverse=True)

    return {"threads": threads[:limit]}


@app.post("/api/admin/threads")
def create_admin_thread():
    """Create a new message thread from admin to a user."""
    _require_admin()
    body = app.current_event.json_body or {}

    user_id = body.get("user_id")
    subject = body.get("subject", "").strip()
    message = body.get("message", "").strip()

    if not user_id:
        raise ValidationError("user_id is required")
    if not subject:
        raise ValidationError("subject is required")
    if not message:
        raise ValidationError("message is required")

    # Verify user exists
    user = user_repo.get_user(user_id)
    if not user:
        raise NotFoundError("User not found")

    import uuid
    now = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    admin_id = get_user_id(app.current_event.raw_event)

    table = get_table("admin")

    # Create thread record
    thread_item = {
        "PK": "THREADS",
        "SK": f"THREAD#{thread_id}",
        "thread_id": thread_id,
        "user_id": user_id,
        "subject": subject,
        "status": "open",
        "is_read_by_admin": True,
        "is_read_by_user": False,
        "message_count": 1,
        "last_message": message[:200],
        "last_sender": "admin",
        "created_at": now,
        "updated_at": now,
        "created_by": admin_id,
    }
    table.put_item(Item=thread_item)

    # Create first message
    msg_item = {
        "PK": f"THREAD#{thread_id}",
        "SK": f"MSG#{now}#{message_id}",
        "message_id": message_id,
        "thread_id": thread_id,
        "sender_id": admin_id,
        "is_from_admin": True,
        "content": message,
        "created_at": now,
    }
    table.put_item(Item=msg_item)

    # Create a notification for the user in the main table
    main_table = get_table("main")
    notif_id = str(uuid.uuid4())
    main_table.put_item(Item={
        "PK": f"USER#{user_id}",
        "SK": f"NOTIF#{notif_id}",
        "title": f"New message: {subject}",
        "message": message[:200],
        "type": "message",
        "is_read": False,
        "dismissed": False,
        "thread_id": thread_id,
        "created_at": now,
    })

    admin_repo.log_audit(admin_id, "admin", "create_thread", "thread", thread_id, user.get("username", ""), f"Subject: {subject}")

    thread_item["username"] = user.get("username") or user.get("email", "Unknown")
    return {"thread": thread_item}, 201


@app.get("/api/admin/threads/<threadId>/messages")
def get_admin_thread_messages(threadId: str):
    """Get all messages in a thread (admin view)."""
    _require_admin()
    table = get_table("admin")

    # Get the thread metadata
    thread_resp = table.get_item(Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"})
    thread = thread_resp.get("Item")
    if not thread:
        raise NotFoundError("Thread not found")

    # Get messages
    msg_resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"THREAD#{threadId}",
            ":prefix": "MSG#",
        },
        ScanIndexForward=True,
    )
    messages = msg_resp.get("Items", [])

    # Mark thread as read by admin
    if not thread.get("is_read_by_admin"):
        table.update_item(
            Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"},
            UpdateExpression="SET is_read_by_admin = :t",
            ExpressionAttributeValues={":t": True},
        )

    # Transform messages
    result_messages = []
    for msg in messages:
        result_messages.append({
            "id": msg.get("message_id", ""),
            "thread_id": threadId,
            "sender_id": msg.get("sender_id", ""),
            "is_from_admin": msg.get("is_from_admin", False),
            "content": msg.get("content", ""),
            "created_at": msg.get("created_at", ""),
        })

    return {
        "thread": {
            "thread_id": threadId,
            "subject": thread.get("subject", ""),
            "status": thread.get("status", "open"),
            "user_id": thread.get("user_id", ""),
        },
        "messages": result_messages,
    }


@app.post("/api/admin/threads/<threadId>/reply")
def admin_reply_to_thread(threadId: str):
    """Admin sends a reply to an existing thread."""
    _require_admin()
    body = app.current_event.json_body or {}
    content = body.get("content", "").strip()

    if not content:
        raise ValidationError("content is required")

    table = get_table("admin")

    # Verify thread exists
    thread_resp = table.get_item(Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"})
    thread = thread_resp.get("Item")
    if not thread:
        raise NotFoundError("Thread not found")

    import uuid
    now = datetime.now(timezone.utc).isoformat()
    message_id = str(uuid.uuid4())
    admin_id = get_user_id(app.current_event.raw_event)

    # Create message
    msg_item = {
        "PK": f"THREAD#{threadId}",
        "SK": f"MSG#{now}#{message_id}",
        "message_id": message_id,
        "thread_id": threadId,
        "sender_id": admin_id,
        "is_from_admin": True,
        "content": content,
        "created_at": now,
    }
    table.put_item(Item=msg_item)

    # Update thread metadata
    current_count = thread.get("message_count", 0)
    table.update_item(
        Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"},
        UpdateExpression="SET updated_at = :now, last_message = :msg, last_sender = :sender, message_count = :count, is_read_by_admin = :t, is_read_by_user = :f",
        ExpressionAttributeValues={
            ":now": now,
            ":msg": content[:200],
            ":sender": "admin",
            ":count": current_count + 1,
            ":t": True,
            ":f": False,
        },
    )

    # Create notification for user
    user_id = thread.get("user_id")
    if user_id:
        main_table = get_table("main")
        notif_id = str(uuid.uuid4())
        main_table.put_item(Item={
            "PK": f"USER#{user_id}",
            "SK": f"NOTIF#{notif_id}",
            "title": f"Reply: {thread.get('subject', 'Message')}",
            "message": content[:200],
            "type": "message",
            "is_read": False,
            "dismissed": False,
            "thread_id": threadId,
            "created_at": now,
        })

    return {"status": "sent", "message_id": message_id}


@app.put("/api/admin/threads/<threadId>")
def update_admin_thread(threadId: str):
    """Update thread status (close/reopen, mark read/unread)."""
    _require_admin()
    body = app.current_event.json_body or {}

    table = get_table("admin")

    # Verify thread exists
    thread_resp = table.get_item(Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"})
    thread = thread_resp.get("Item")
    if not thread:
        raise NotFoundError("Thread not found")

    update_parts = []
    attr_names = {}
    attr_values = {}

    if "status" in body:
        status = body["status"]
        if status not in ("open", "closed"):
            raise ValidationError("Status must be 'open' or 'closed'")
        update_parts.append("#s = :status")
        attr_names["#s"] = "status"
        attr_values[":status"] = status

    if "is_read_by_admin" in body:
        update_parts.append("is_read_by_admin = :read")
        attr_values[":read"] = bool(body["is_read_by_admin"])

    now = datetime.now(timezone.utc).isoformat()
    update_parts.append("updated_at = :now")
    attr_values[":now"] = now

    if update_parts:
        expr = "SET " + ", ".join(update_parts)
        kwargs = {
            "Key": {"PK": "THREADS", "SK": f"THREAD#{threadId}"},
            "UpdateExpression": expr,
            "ExpressionAttributeValues": attr_values,
        }
        if attr_names:
            kwargs["ExpressionAttributeNames"] = attr_names
        table.update_item(**kwargs)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_thread", "thread", threadId, details=json.dumps(body))

    return {"status": "updated"}


# --- Custom Reports ---

@app.get("/api/admin/export/report")
def generate_report():
    """Generate a custom report with aggregated data."""
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    report_type = params.get("type")
    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if not report_type:
        raise ValidationError("Report type is required")

    valid_types = ("user_summary", "activity", "content_stats", "hero_usage", "growth")
    if report_type not in valid_types:
        raise ValidationError(f"Invalid report type. Must be one of: {', '.join(valid_types)}")

    rows = _build_report(report_type, start_date, end_date)

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "generate_report", details=f"type={report_type}")

    return {"rows": rows, "type": report_type, "count": len(rows)}


@app.get("/api/admin/export/report/download")
def download_report():
    """Download a custom report as CSV."""
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    report_type = params.get("type")
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    fmt = params.get("format", "csv")

    if not report_type:
        raise ValidationError("Report type is required")

    valid_types = ("user_summary", "activity", "content_stats", "hero_usage", "growth")
    if report_type not in valid_types:
        raise ValidationError(f"Invalid report type. Must be one of: {', '.join(valid_types)}")

    rows = _build_report(report_type, start_date, end_date)

    if not rows:
        return {"csv": "", "count": 0}

    headers = list(rows[0].keys()) if rows else []
    lines = [",".join(headers)]
    for row in rows:
        line = [str(row.get(h, "")).replace(",", ";").replace("\n", " ").replace("\r", "") for h in headers]
        lines.append(",".join(line))

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "download_report", details=f"type={report_type}, format={fmt}")

    return {"csv": "\n".join(lines), "count": len(rows), "filename": f"{report_type}_report.csv"}


def _build_report(report_type: str, start_date: str = None, end_date: str = None) -> list:
    """Build report rows based on type."""
    if report_type == "user_summary":
        return _report_user_summary()
    elif report_type == "activity":
        return _report_activity()
    elif report_type == "content_stats":
        return _report_content_stats()
    elif report_type == "hero_usage":
        return _report_hero_usage()
    elif report_type == "growth":
        return _report_growth(start_date, end_date)
    return []


def _report_user_summary() -> list:
    """User Summary report."""
    users = user_repo.list_users(limit=1000)
    rows = []

    for u in users:
        uid = u.get("user_id")
        profiles = []
        try:
            profiles = profile_repo.get_profiles(uid) if uid else []
        except Exception:
            pass

        if not profiles:
            rows.append({
                "Username": u.get("username", ""),
                "Email": u.get("email", ""),
                "Role": u.get("role", "user"),
                "State": "",
                "Is Active": str(u.get("is_active", True)),
                "Created": u.get("created_at", "")[:10],
                "Last Login": (u.get("last_login") or "")[:10],
                "Profile Name": "",
                "Heroes Tracked": 0,
            })
        else:
            for p in profiles:
                profile_id = p.get("SK", "").replace("PROFILE#", "") or p.get("profile_id", "")
                hero_count = 0
                if profile_id:
                    try:
                        hero_count = len(hero_repo.get_heroes(profile_id))
                    except Exception:
                        pass
                rows.append({
                    "Username": u.get("username", ""),
                    "Email": u.get("email", ""),
                    "Role": u.get("role", "user"),
                    "State": str(p.get("state_number", "")),
                    "Is Active": str(u.get("is_active", True)),
                    "Created": u.get("created_at", "")[:10],
                    "Last Login": (u.get("last_login") or "")[:10],
                    "Profile Name": p.get("name", ""),
                    "Heroes Tracked": hero_count,
                })

    return rows


def _report_activity() -> list:
    """Activity Report."""
    users = user_repo.list_users(limit=1000)
    now = datetime.now(timezone.utc)
    rows = []

    for u in users:
        last_login = u.get("last_login")
        days_since = None
        status = "Never"

        if last_login:
            try:
                last = datetime.fromisoformat(last_login.replace("Z", "+00:00"))
                days_since = (now - last).days
                if days_since == 0:
                    status = "Active Today"
                elif days_since <= 7:
                    status = "Active This Week"
                elif days_since <= 30:
                    status = "Active This Month"
                else:
                    status = "Inactive"
            except Exception:
                status = "Never"

        rows.append({
            "Username": u.get("username", ""),
            "Status": status,
            "Last Login": (last_login or "")[:10],
            "Days Since Login": days_since if days_since is not None else "",
            "Account Created": u.get("created_at", "")[:10],
        })

    return rows


def _report_content_stats() -> list:
    """Content Statistics report."""
    users = user_repo.list_users(limit=1000)
    rows = []

    for u in users:
        uid = u.get("user_id")
        try:
            profiles = profile_repo.get_profiles(uid) if uid else []
        except Exception:
            profiles = []

        for p in profiles:
            profile_id = p.get("SK", "").replace("PROFILE#", "") or p.get("profile_id", "")
            hero_count = 0
            if profile_id:
                try:
                    hero_count = len(hero_repo.get_heroes(profile_id))
                except Exception:
                    pass

            rows.append({
                "Profile Name": p.get("name", ""),
                "Username": u.get("username", ""),
                "State": str(p.get("state_number", "")),
                "Server Age": p.get("server_age_days", ""),
                "Furnace Level": p.get("furnace_level", ""),
                "Spending Profile": p.get("spending_profile", ""),
                "Alliance Role": p.get("alliance_role", ""),
                "Heroes Tracked": hero_count,
                "Inventory Items": 0,
            })

    return rows


def _report_hero_usage() -> list:
    """Hero Usage report."""
    users = user_repo.list_users(limit=1000)
    hero_counter = Counter()

    hero_ref = {}
    try:
        ref_heroes = hero_repo.get_all_heroes_reference()
        for h in ref_heroes:
            hero_ref[h.get("name", "")] = h
    except Exception:
        pass

    for u in users:
        uid = u.get("user_id")
        try:
            profiles = profile_repo.get_profiles(uid) if uid else []
        except Exception:
            continue

        for p in profiles:
            profile_id = p.get("SK", "").replace("PROFILE#", "") or p.get("profile_id", "")
            if profile_id:
                try:
                    heroes = hero_repo.get_heroes(profile_id)
                    for h in heroes:
                        hname = h.get("hero_name") or h.get("SK", "").replace("HERO#", "")
                        if hname:
                            hero_counter[hname] += 1
                except Exception:
                    pass

    rows = []
    for hero_name, count in hero_counter.most_common():
        ref = hero_ref.get(hero_name, {})
        rows.append({
            "Hero": hero_name,
            "Class": ref.get("hero_class", ""),
            "Rarity": ref.get("rarity", ""),
            "Generation": ref.get("generation", ""),
            "Users Tracking": count,
        })

    return rows


def _report_growth(start_date: str = None, end_date: str = None) -> list:
    """Growth Metrics report."""
    from datetime import timedelta

    if not start_date:
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    metrics = admin_repo.get_metrics_history(days=90)

    rows = []
    for m in metrics:
        date = m.get("date", "")
        if date < start_date or date > end_date:
            continue
        rows.append({
            "Date": date,
            "Total Users": m.get("total_users", 0),
            "New Users": m.get("new_users", 0),
            "Active Users": m.get("active_users", 0),
            "Total Profiles": m.get("total_profiles", 0),
            "Heroes Tracked": m.get("total_heroes", 0),
            "Inventory Items": m.get("total_inventory", 0),
        })

    return rows


# --- Admin Hero CRUD ---

@app.get("/api/admin/heroes")
def admin_list_heroes():
    _require_admin()
    heroes = hero_repo.get_all_heroes_reference()
    return {"heroes": heroes}


@app.post("/api/admin/heroes")
def admin_create_hero():
    _require_admin()
    body = app.current_event.json_body or {}

    name = body.get("name")
    if not name:
        raise ValidationError("Hero name is required")

    hero_class = body.get("hero_class", "Infantry")
    rarity = body.get("rarity", "Epic")
    generation = body.get("generation", 1)
    tier_overall = body.get("tier_overall")

    # Check if hero already exists
    existing = hero_repo.get_hero_reference(name)
    if existing:
        raise ValidationError(f"Hero '{name}' already exists")

    # Add to heroes.json
    heroes_path = os.path.join(Config.DATA_DIR, "heroes.json")
    with open(heroes_path, encoding="utf-8") as f:
        data = json.load(f)

    new_hero = {
        "name": name,
        "hero_class": hero_class,
        "rarity": rarity,
        "generation": generation,
        "tier_overall": tier_overall,
    }
    data["heroes"].append(new_hero)

    with open(heroes_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Clear the in-memory cache
    hero_repo._heroes_cache = None

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "create_hero", "hero", name)

    return {"hero": new_hero}, 201


@app.put("/api/admin/heroes/<heroName>")
def admin_update_hero(heroName: str):
    _require_admin()
    body = app.current_event.json_body or {}

    heroes_path = os.path.join(Config.DATA_DIR, "heroes.json")
    with open(heroes_path, encoding="utf-8") as f:
        data = json.load(f)

    hero_idx = None
    for i, h in enumerate(data["heroes"]):
        if h["name"] == heroName:
            hero_idx = i
            break

    if hero_idx is None:
        raise NotFoundError(f"Hero '{heroName}' not found")

    allowed = {"name", "hero_class", "rarity", "generation", "tier_overall", "tier_expedition", "tier_exploration"}
    for k, v in body.items():
        if k in allowed:
            data["heroes"][hero_idx][k] = v

    with open(heroes_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    hero_repo._heroes_cache = None

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_hero", "hero", heroName, details=json.dumps(body))

    return {"hero": data["heroes"][hero_idx]}


@app.delete("/api/admin/heroes/<heroName>")
def admin_delete_hero(heroName: str):
    _require_admin()

    heroes_path = os.path.join(Config.DATA_DIR, "heroes.json")
    with open(heroes_path, encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data["heroes"])
    data["heroes"] = [h for h in data["heroes"] if h["name"] != heroName]

    if len(data["heroes"]) == original_count:
        raise NotFoundError(f"Hero '{heroName}' not found")

    with open(heroes_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    hero_repo._heroes_cache = None

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "delete_hero", "hero", heroName)

    return {"status": "deleted"}


# --- Admin Item CRUD ---

def _load_items() -> list:
    """Load items from ReferenceTable."""
    table = get_table("reference")
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": "ITEM"},
    )
    return resp.get("Items", [])


@app.get("/api/admin/items")
def admin_list_items():
    _require_admin()
    items = _load_items()
    return {"items": items}


@app.post("/api/admin/items")
def admin_create_item():
    _require_admin()
    body = app.current_event.json_body or {}

    name = body.get("name")
    if not name:
        raise ValidationError("Item name is required")

    category = body.get("category", "")
    subcategory = body.get("subcategory")
    rarity = body.get("rarity")

    # Check if item already exists
    table = get_table("reference")
    resp = table.get_item(Key={"PK": "ITEM", "SK": name})
    if resp.get("Item"):
        raise ValidationError(f"Item '{name}' already exists")

    item = {
        "PK": "ITEM",
        "SK": name,
        "entity_type": "Item",
        "name": name,
        "category": category,
        "rarity": rarity,
    }
    if subcategory:
        item["subcategory"] = subcategory

    table.put_item(Item={k: v for k, v in item.items() if v is not None})

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "create_item", "item", name)

    return {"item": item}, 201


@app.put("/api/admin/items/<itemName>")
def admin_update_item(itemName: str):
    _require_admin()
    body = app.current_event.json_body or {}

    table = get_table("reference")
    resp = table.get_item(Key={"PK": "ITEM", "SK": itemName})
    if not resp.get("Item"):
        raise NotFoundError(f"Item '{itemName}' not found")

    allowed = {"name", "category", "subcategory", "rarity"}
    update_parts = []
    attr_names = {}
    attr_values = {}

    for i, (k, v) in enumerate(body.items()):
        if k in allowed:
            update_parts.append(f"#k{i} = :v{i}")
            attr_names[f"#k{i}"] = k
            attr_values[f":v{i}"] = v

    if update_parts:
        table.update_item(
            Key={"PK": "ITEM", "SK": itemName},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
        )

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "update_item", "item", itemName, details=json.dumps(body))

    updated = table.get_item(Key={"PK": "ITEM", "SK": itemName})
    return {"item": updated.get("Item", {})}


@app.delete("/api/admin/items/<itemName>")
def admin_delete_item(itemName: str):
    _require_admin()

    table = get_table("reference")
    resp = table.get_item(Key={"PK": "ITEM", "SK": itemName})
    if not resp.get("Item"):
        raise NotFoundError(f"Item '{itemName}' not found")

    table.delete_item(Key={"PK": "ITEM", "SK": itemName})

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "delete_item", "item", itemName)

    return {"status": "deleted"}


def lambda_handler(event, context):
    try:
        return app.resolve(event, context)
    except AppError as exc:
        logger.warning("Application error", extra={"error": exc.message, "status": exc.status_code})
        return {"statusCode": exc.status_code, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": exc.message})}
    except Exception as exc:
        logger.exception("Unhandled error in admin handler")
        capture_error("admin", event, exc, logger)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Internal server error"})}
