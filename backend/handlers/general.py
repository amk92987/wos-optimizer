"""General routes Lambda handler (dashboard, events, inbox, feedback, lineups)."""

import json
import os

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from common.auth import get_effective_user_id
from common.exceptions import AppError, ValidationError, NotFoundError
from common.config import Config
from common import profile_repo, hero_repo, admin_repo, user_repo, ai_repo
from common.db import get_table

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

    # Compute generation from server_age_days
    server_age_days = profile.get("server_age_days", 0)
    generation = 1
    gen_thresholds = [40, 120, 200, 280, 360, 440, 520, 600, 680, 760, 840, 920, 1000]
    for i, threshold in enumerate(gen_thresholds):
        if server_age_days >= threshold:
            generation = i + 2
        else:
            break

    # Build furnace display string
    furnace_level = profile.get("furnace_level", 1)
    furnace_fc_level = profile.get("furnace_fc_level")
    if furnace_fc_level:
        furnace_display = furnace_fc_level
    elif furnace_level:
        furnace_display = f"Lv.{furnace_level}"
    else:
        furnace_display = "Lv.1"

    # Load total hero count from reference data
    heroes_path = os.path.join(Config.DATA_DIR, "heroes.json")
    total_heroes = 0
    try:
        with open(heroes_path, encoding="utf-8") as f:
            heroes_data = json.load(f)
        total_heroes = len(heroes_data.get("heroes", []))
    except Exception:
        pass

    # Get user info
    user = user_repo.get_user(user_id)

    return {
        "profile": profile,
        "hero_count": len(heroes),
        "owned_heroes": len(heroes),
        "total_heroes": total_heroes,
        "profile_count": len(profiles),
        "furnace_level": furnace_level,
        "furnace_display": furnace_display,
        "spending_profile": profile.get("spending_profile", "f2p"),
        "generation": generation,
        "server_age_days": server_age_days,
        "username": user.get("username", "") if user else "",
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


@app.get("/api/events/guide")
def get_events_guide():
    """Return full events guide data for the frontend events page."""
    # Use the dedicated guide file which matches the frontend's expected format
    guide_path = os.path.join(Config.DATA_DIR, "events_guide.json")
    if os.path.exists(guide_path):
        with open(guide_path, encoding="utf-8") as f:
            return json.load(f)

    # Fallback to events.json (old format, may not work with frontend)
    events_path = os.path.join(Config.DATA_DIR, "events.json")
    if not os.path.exists(events_path):
        return {"events": {}, "cost_categories": {}, "priority_tiers": {}}

    with open(events_path, encoding="utf-8") as f:
        data = json.load(f)

    return data


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
    raw_notifications = resp.get("Items", [])

    # Transform DynamoDB items into the shape the frontend expects
    notifications = []
    for item in raw_notifications:
        sk = item.get("SK", "")
        notif_id = sk.replace("NOTIF#", "") if sk.startswith("NOTIF#") else sk
        notifications.append({
            "id": notif_id,
            "title": item.get("title", ""),
            "message": item.get("message", ""),
            "type": item.get("type", "info"),
            "is_read": bool(item.get("is_read") or item.get("dismissed")),
            "created_at": item.get("created_at", ""),
        })

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

    if category not in ("bug", "feature", "bad_recommendation", "data_error", "general", "other"):
        raise ValidationError("Invalid feedback category")

    feedback = admin_repo.create_feedback(
        user_id=user_id,
        category=category,
        description=description,
        page=page,
    )
    return {"feedback": feedback}, 201


# --- Inbox / Notifications (additional routes) ---

@app.get("/api/inbox/notifications")
def get_notifications():
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
    raw_notifications = resp.get("Items", [])

    # Transform DynamoDB items into the shape the frontend expects
    notifications = []
    for item in raw_notifications:
        sk = item.get("SK", "")
        notif_id = sk.replace("NOTIF#", "") if sk.startswith("NOTIF#") else sk
        notifications.append({
            "id": notif_id,
            "title": item.get("title", ""),
            "message": item.get("message", ""),
            "type": item.get("type", "info"),
            "is_read": bool(item.get("is_read") or item.get("dismissed")),
            "created_at": item.get("created_at", ""),
        })

    # Include active announcements that should appear in inbox
    announcements = admin_repo.get_announcements(active_only=True)
    for a in announcements:
        if a.get("display_type") in ("inbox", "both"):
            sk = a.get("SK", "")
            ann_id = sk.replace("ANNOUNCE#", "ann-") if sk.startswith("ANNOUNCE#") else f"ann-{sk}"
            notifications.append({
                "id": ann_id,
                "title": a.get("title", ""),
                "message": a.get("inbox_content") or a.get("message", ""),
                "type": a.get("announcement_type", "info"),
                "is_read": False,
                "created_at": a.get("created_at", ""),
            })

    return {"notifications": notifications}


@app.post("/api/inbox/notifications/<notificationId>/read")
def mark_notification_read(notificationId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)
    table = get_table("main")

    table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": f"NOTIF#{notificationId}"},
        UpdateExpression="SET dismissed = :t, is_read = :t",
        ExpressionAttributeValues={":t": True},
    )
    return {"status": "read"}


@app.get("/api/inbox/unread-count")
def get_unread_count():
    user_id = get_effective_user_id(app.current_event.raw_event)
    table = get_table("main")

    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":prefix": "NOTIF#",
        },
    )
    notifications = resp.get("Items", [])
    unread = sum(1 for n in notifications if not n.get("dismissed") and not n.get("is_read"))

    # For admins, include unresolved error count
    error_count = 0
    try:
        from common.auth import is_admin
        if is_admin(app.current_event.raw_event):
            admin_table = get_table("admin")
            error_resp = admin_table.query(
                KeyConditionExpression="PK = :pk",
                FilterExpression="attribute_not_exists(#s) OR #s = :new",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":pk": "ERRORS", ":new": "new"},
                Select="COUNT",
            )
            error_count = error_resp.get("Count", 0)
    except Exception:
        pass  # Don't break unread count if error query fails

    return {"unread_notifications": unread, "error_count": error_count, "total_unread": unread + error_count}


@app.get("/api/inbox/threads")
def get_inbox_threads():
    """Get message threads for the current user."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    admin_table = get_table("admin")

    # Query all threads - filter by user_id
    resp = admin_table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": "THREADS",
            ":prefix": "THREAD#",
        },
        ScanIndexForward=False,
    )
    all_threads = resp.get("Items", [])

    # Filter to only this user's threads
    user_threads = [t for t in all_threads if t.get("user_id") == user_id]

    # Transform for frontend
    threads = []
    for t in user_threads:
        sk = t.get("SK", "")
        thread_id = sk.replace("THREAD#", "") if sk.startswith("THREAD#") else sk
        threads.append({
            "id": thread_id,
            "subject": t.get("subject", ""),
            "last_message": t.get("last_message", ""),
            "has_unread": not t.get("is_read_by_user", True),
            "message_count": t.get("message_count", 0),
            "status": t.get("status", "open"),
            "updated_at": t.get("updated_at", t.get("created_at", "")),
        })

    threads.sort(key=lambda t: t.get("updated_at", ""), reverse=True)
    return {"threads": threads}


@app.get("/api/inbox/threads/<threadId>/messages")
def get_thread_messages(threadId: str):
    """Get messages in a thread for the current user."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    admin_table = get_table("admin")

    # Verify the thread belongs to this user
    thread_resp = admin_table.get_item(Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"})
    thread = thread_resp.get("Item")
    if not thread or thread.get("user_id") != user_id:
        return {"messages": []}

    # Get messages
    msg_resp = admin_table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"THREAD#{threadId}",
            ":prefix": "MSG#",
        },
        ScanIndexForward=True,
    )
    messages = msg_resp.get("Items", [])

    # Mark thread as read by user
    if not thread.get("is_read_by_user"):
        admin_table.update_item(
            Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"},
            UpdateExpression="SET is_read_by_user = :t",
            ExpressionAttributeValues={":t": True},
        )

    result = []
    for msg in messages:
        result.append({
            "id": msg.get("message_id", ""),
            "is_from_admin": msg.get("is_from_admin", False),
            "content": msg.get("content", ""),
            "created_at": msg.get("created_at", ""),
        })

    return {"messages": result}


@app.post("/api/inbox/threads/<threadId>/reply")
def reply_to_thread(threadId: str):
    """User replies to a thread."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}
    content = body.get("content", "").strip()

    if not content:
        return {"error": "content is required"}, 400

    admin_table = get_table("admin")

    # Verify the thread belongs to this user and is open
    thread_resp = admin_table.get_item(Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"})
    thread = thread_resp.get("Item")
    if not thread or thread.get("user_id") != user_id:
        return {"error": "Thread not found"}, 404

    if thread.get("status") == "closed":
        return {"error": "Thread is closed"}, 400

    import uuid
    from datetime import datetime as dt, timezone as tz
    now = dt.now(tz.utc).isoformat()
    message_id = str(uuid.uuid4())

    # Create message
    msg_item = {
        "PK": f"THREAD#{threadId}",
        "SK": f"MSG#{now}#{message_id}",
        "message_id": message_id,
        "thread_id": threadId,
        "sender_id": user_id,
        "is_from_admin": False,
        "content": content,
        "created_at": now,
    }
    admin_table.put_item(Item=msg_item)

    # Update thread metadata
    current_count = thread.get("message_count", 0)
    admin_table.update_item(
        Key={"PK": "THREADS", "SK": f"THREAD#{threadId}"},
        UpdateExpression="SET updated_at = :now, last_message = :msg, last_sender = :sender, message_count = :count, is_read_by_user = :t, is_read_by_admin = :f",
        ExpressionAttributeValues={
            ":now": now,
            ":msg": content[:200],
            ":sender": "user",
            ":count": current_count + 1,
            ":t": True,
            ":f": False,
        },
    )

    return {"status": "sent", "message_id": message_id}


# --- Lineups ---

@app.get("/api/lineups/templates")
def get_lineup_templates():
    """Return lineup template metadata (no auth required)."""
    lineup_path = os.path.join(Config.DATA_DIR, "guides", "hero_lineup_reasoning.json")
    if not os.path.exists(lineup_path):
        return {}

    with open(lineup_path, encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/lineups/template/<gameMode>")
def get_lineup_template(gameMode: str):
    """Return specific lineup template details (no auth required)."""
    lineup_path = os.path.join(Config.DATA_DIR, "guides", "hero_lineup_reasoning.json")
    if not os.path.exists(lineup_path):
        raise NotFoundError(f"No lineup template for: {gameMode}")

    with open(lineup_path, encoding="utf-8") as f:
        data = json.load(f)

    # Templates live under lineup_scenarios; try exact match then prefix match
    scenarios = data.get("lineup_scenarios", {}) if isinstance(data, dict) else {}
    template = scenarios.get(gameMode)
    if not template:
        # Try prefix match (e.g. "bear_trap" matches "bear_trap_crazy_joe")
        for key, value in scenarios.items():
            if key.startswith(gameMode) or gameMode.startswith(key):
                template = value
                break
    if not template:
        raise NotFoundError(f"No lineup template for: {gameMode}")
    return template


@app.get("/api/lineups/general/<gameMode>")
def get_general_lineup(gameMode: str):
    """Return general lineup recommendation (no auth required)."""
    params = app.current_event.query_string_parameters or {}
    max_generation = int(params.get("max_generation", "14"))

    try:
        from engine.recommendation_engine import get_engine
        engine = get_engine()
        result = engine.lineup_builder.build_general_lineup(gameMode, max_generation=max_generation)
        return result
    except Exception as e:
        logger.warning(f"General lineup failed, returning template: {e}")
        # Fall back to template data
        lineup_path = os.path.join(Config.DATA_DIR, "guides", "hero_lineup_reasoning.json")
        if os.path.exists(lineup_path):
            with open(lineup_path, encoding="utf-8") as f:
                data = json.load(f)
            scenarios = data.get("lineup_scenarios", {}) if isinstance(data, dict) else {}
            template = scenarios.get(gameMode, {})
            if not template:
                for key, value in scenarios.items():
                    if key.startswith(gameMode) or gameMode.startswith(key):
                        template = value
                        break
            return {"game_mode": gameMode, "heroes": [], "troop_ratio": template.get("troop_ratio", {"infantry": 50, "lancer": 20, "marksman": 30}), "notes": template.get("notes", template.get("goal", "")), "confidence": "low", "recommended_to_get": []}
        return {"game_mode": gameMode, "heroes": [], "troop_ratio": {"infantry": 50, "lancer": 20, "marksman": 30}, "notes": "", "confidence": "low", "recommended_to_get": []}


@app.get("/api/lineups/build/<gameMode>")
def build_lineup_for_mode(gameMode: str):
    """Build personalized lineup for a specific game mode (auth required)."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)

    try:
        from engine.recommendation_engine import get_engine
        engine = get_engine()
        result = engine.get_lineup(gameMode, heroes=heroes, profile=profile)
        return result
    except Exception as e:
        logger.warning(f"Personalized lineup failed: {e}")
        return {"game_mode": gameMode, "heroes": [], "troop_ratio": {"infantry": 50, "lancer": 20, "marksman": 30}, "notes": "Unable to generate lineup. Add heroes to your tracker.", "confidence": "none", "recommended_to_get": []}


@app.get("/api/lineups/build-all")
def build_all_lineups():
    """Build lineups for all game modes (auth required)."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)

    try:
        from engine.recommendation_engine import get_engine
        engine = get_engine()
        result = engine.get_all_lineups(heroes=heroes, profile=profile)
        return {"lineups": result}
    except Exception as e:
        logger.warning(f"Build all lineups failed: {e}")
        return {"lineups": {}}


@app.get("/api/lineups/joiner/<attackType>")
def get_joiner_recommendation(attackType: str):
    """Get rally joiner hero recommendation (auth required)."""
    user_id = get_effective_user_id(app.current_event.raw_event)
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)

    is_attack = attackType.lower() in ("attack", "offense")

    try:
        from engine.recommendation_engine import get_engine
        engine = get_engine()
        result = engine.get_joiner_recommendation(heroes=heroes, is_attack=is_attack)
        return result
    except Exception as e:
        logger.warning(f"Joiner recommendation failed: {e}")
        return {"hero": None, "status": "no_heroes", "skill_level": None, "max_skill": 5, "recommendation": "Add heroes to your tracker to get joiner recommendations.", "action": "", "critical_note": ""}


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

    # Find the matching event type lineup (data is under lineup_scenarios)
    scenarios = lineups.get("lineup_scenarios", {}) if isinstance(lineups, dict) else {}
    event_lineup = scenarios.get(eventType)
    if not event_lineup:
        # Try prefix match (e.g. "bear_trap" matches "bear_trap_crazy_joe")
        for key, value in scenarios.items():
            if key.startswith(eventType) or eventType.startswith(key):
                event_lineup = value
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
    try:
        return app.resolve(event, context)
    except AppError as exc:
        logger.warning("Application error", extra={"error": exc.message, "status": exc.status_code})
        return {"statusCode": exc.status_code, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": exc.message})}
    except Exception as exc:
        logger.exception("Unhandled error in general handler")
        from common.error_capture import capture_error
        capture_error("general", event, exc, logger)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Internal server error"})}
