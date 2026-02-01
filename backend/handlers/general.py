"""General routes Lambda handler (dashboard, events, inbox, feedback, lineups)."""

import json
import os

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from backend.common.auth import get_effective_user_id
from backend.common.exceptions import AppError, ValidationError, NotFoundError
from backend.common.config import Config
from backend.common import profile_repo, hero_repo, admin_repo, user_repo, ai_repo
from backend.common.db import get_table

app = APIGatewayHttpResolver()
logger = Logger()


# --- Dashboard ---

@app.get("/api/dashboard")
def get_dashboard():
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]

    heroes = hero_repo.get_heroes(profile_id)
    profiles = profile_repo.get_profiles(user_id)

    # Active announcements
    announcements = admin_repo.get_announcements(active_only=True)

    return {
        "profile": profile,
        "hero_count": len(heroes),
        "profile_count": len(profiles),
        "furnace_level": profile.get("furnace_level", 1),
        "spending_profile": profile.get("spending_profile", "f2p"),
        "announcements": announcements,
    }


# --- Events ---

@app.get("/api/events")
def get_events():
    events_path = os.path.join(Config.DATA_DIR, "events.json")
    if not os.path.exists(events_path):
        return {"events": []}

    with open(events_path, encoding="utf-8") as f:
        data = json.load(f)

    return {"events": data.get("events", data) if isinstance(data, dict) else data}


# --- Inbox / Notifications ---

@app.get("/api/inbox")
def get_inbox():
    user_id = get_effective_user_id(app.current_event.raw_event)
    table = get_table("main")

    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":prefix": "NOTIF#",
        },
        ScanIndexForward=False,
    )
    notifications = resp.get("Items", [])

    # Also include active announcements as inbox items
    announcements = admin_repo.get_announcements(active_only=True)
    inbox_items = [
        a for a in announcements
        if a.get("display_type") in ("inbox", "both", "banner")
    ]

    return {
        "notifications": notifications,
        "announcements": inbox_items,
    }


@app.post("/api/inbox/<notificationId>/dismiss")
def dismiss_notification(notificationId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    table = get_table("main")

    table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": f"NOTIF#{notificationId}"},
        UpdateExpression="SET dismissed = :t",
        ExpressionAttributeValues={":t": True},
    )
    return {"status": "dismissed"}


# --- Feedback ---

@app.post("/api/feedback")
def submit_feedback():
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}

    category = body.get("category", "general")
    description = body.get("description", "").strip()
    page = body.get("page")

    if not description:
        raise ValidationError("Description is required")

    if category not in ("bug", "feature", "bad_recommendation", "general", "other"):
        raise ValidationError("Invalid feedback category")

    feedback = admin_repo.create_feedback(
        user_id=user_id,
        category=category,
        description=description,
        page=page,
    )
    return {"feedback": feedback}, 201


# --- Lineups ---

@app.get("/api/lineups")
def get_lineups():
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)
    hero_ref = hero_repo.get_all_heroes_reference()

    # Load lineup templates from data
    lineup_path = os.path.join(Config.DATA_DIR, "guides", "hero_lineup_reasoning.json")
    lineups = {}
    if os.path.exists(lineup_path):
        with open(lineup_path, encoding="utf-8") as f:
            lineups = json.load(f)

    return {
        "lineups": lineups,
        "owned_heroes": len(heroes),
        "hero_count": len(hero_ref),
    }


@app.get("/api/lineups/<eventType>")
def get_lineup_for_event(eventType: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)

    # Load lineup data
    lineup_path = os.path.join(Config.DATA_DIR, "guides", "hero_lineup_reasoning.json")
    if not os.path.exists(lineup_path):
        raise NotFoundError("Lineup data not found")

    with open(lineup_path, encoding="utf-8") as f:
        lineups = json.load(f)

    # Find the matching event type lineup
    event_lineup = None
    if isinstance(lineups, dict):
        event_lineup = lineups.get(eventType)
    elif isinstance(lineups, list):
        for entry in lineups:
            if entry.get("event_type") == eventType:
                event_lineup = entry
                break

    if not event_lineup:
        raise NotFoundError(f"No lineup found for event type: {eventType}")

    return {
        "event_type": eventType,
        "lineup": event_lineup,
        "owned_heroes": [h.get("hero_name") for h in heroes],
    }


# --- Cleanup (scheduled Lambda) ---

def cleanup_handler(event, context):
    """Daily cleanup Lambda triggered by EventBridge schedule.

    Resets AI request counters, cleans up expired data, and saves metrics.
    """
    logger.info("Running daily cleanup")

    # Reset AI request counters for all users
    users = user_repo.list_users(limit=10000)
    reset_count = 0
    for user in users:
        if user.get("ai_requests_today", 0) > 0:
            user_repo.reset_ai_request_counter(user["user_id"])
            reset_count += 1

    # Save daily metrics
    total_users = len(users)
    test_accounts = sum(1 for u in users if u.get("is_test_account"))
    active_users = sum(1 for u in users if u.get("is_active"))

    ai_settings = ai_repo.get_ai_settings()
    feedback = admin_repo.get_feedback()

    admin_repo.save_daily_metrics({
        "total_users": total_users,
        "test_accounts": test_accounts,
        "active_users": active_users,
        "ai_mode": ai_settings.get("mode", "off"),
        "total_ai_requests": ai_settings.get("total_requests", 0),
        "pending_feedback": sum(1 for f in feedback if f.get("status") in ("new", "pending_fix", "pending_update")),
    })

    logger.info(f"Cleanup complete: reset {reset_count} AI counters, saved metrics")
    return {"status": "ok", "reset_count": reset_count}


def lambda_handler(event, context):
    return app.resolve(event, context)
