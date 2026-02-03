"""Admin Lambda handler."""

import json
import os
from collections import Counter
from datetime import datetime, timezone

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from backend.common.auth import get_effective_user_id, require_admin, is_admin, get_user_id
from backend.common.exceptions import AppError, NotFoundError, ValidationError
from backend.common.config import Config
from backend.common import admin_repo, user_repo, ai_repo, profile_repo, hero_repo
from backend.common.db import get_table

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

    # Enrich each user with profile_count, states, usage_7d
    for u in users:
        uid = u.get("user_id")
        try:
            profiles = profile_repo.get_profiles(uid) if uid else []
            u["profile_count"] = len(profiles)
            u["states"] = [p["state_number"] for p in profiles if p.get("state_number")]
        except Exception:
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

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "create_user", "user", user_id, username)

    return {"user": user}, 201


@app.get("/api/admin/users/<userId>")
def get_user(userId: str):
    _require_admin()
    user = user_repo.get_user(userId)
    if not user:
        raise NotFoundError("User not found")

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
    total_users = len(users)
    test_accounts = sum(1 for u in users if u.get("is_test_account"))
    active_users = sum(1 for u in users if u.get("is_active"))

    ai_settings = ai_repo.get_ai_settings()
    feedback = admin_repo.get_feedback()

    return {
        "total_users": total_users,
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
    total_users = len(users)
    test_accounts = sum(1 for u in users if u.get("is_test_account"))
    active_users = sum(1 for u in users if u.get("is_active"))

    ai_settings = ai_repo.get_ai_settings()
    feedback = admin_repo.get_feedback()
    announcements = admin_repo.get_announcements(active_only=True)

    # Count profiles and heroes
    total_profiles = 0
    total_heroes = 0
    ai_requests_today = 0
    for u in users:
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
        "total_users": total_users,
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

    users = user_repo.list_users(limit=1000)
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

    # Historical data from metrics
    historical = []
    try:
        metrics_history = admin_repo.get_metrics_history(days=days)
        for m in metrics_history:
            historical.append({
                "date": m.get("date", ""),
                "total_users": m.get("total_users", 0),
                "active_users": m.get("active_users", 0),
                "new_users": m.get("new_users", 0),
                "heroes_tracked": m.get("total_heroes", 0),
            })
    except Exception:
        pass

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
        "daily_active_users": [],  # Would need daily snapshots to populate
        "ai_usage": [],  # Would need per-day AI request tracking
        "historical": historical,
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
    table = get_table("admin")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": "ERRORS",
            ":prefix": "ERROR#",
        },
        ScanIndexForward=False,
    )
    errors = resp.get("Items", [])
    return {"errors": errors}


@app.post("/api/admin/errors/<errorId>/resolve")
def resolve_error(errorId: str):
    _require_admin()
    table = get_table("admin")
    table.update_item(
        Key={"PK": "ERRORS", "SK": f"ERROR#{errorId}"},
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
            Key={"PK": "ERRORS", "SK": f"ERROR#{errorId}"},
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
    table = get_table("admin")
    table.delete_item(Key={"PK": "ERRORS", "SK": f"ERROR#{errorId}"})
    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "delete_error", "error", errorId)
    return {"status": "deleted"}


@app.post("/api/admin/errors/bulk")
def bulk_error_action():
    _require_admin()
    body = app.current_event.json_body or {}
    action = body.get("action")
    admin_id = get_user_id(app.current_event.raw_event)

    if action == "delete_ignored":
        table = get_table("admin")
        resp = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
            ExpressionAttributeValues={":pk": "ERRORS", ":prefix": "ERROR#"},
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
    data_dir = Config.DATA_DIR

    # Check core data files
    core_files = [
        ("heroes.json", "Hero Data", "Core hero definitions and stats"),
        ("events.json", "Event Data", "Event calendar and mechanics"),
        ("chief_gear.json", "Chief Gear Data", "Chief gear stats and progression"),
        ("vip_system.json", "VIP System Data", "VIP levels and buffs"),
    ]
    for fname, check_name, description in core_files:
        fpath = os.path.join(data_dir, fname)
        exists = os.path.exists(fpath)
        valid = False
        size = 0
        if exists:
            size = os.path.getsize(fpath)
            try:
                with open(fpath, encoding="utf-8") as f:
                    json.load(f)
                valid = True
            except Exception:
                pass

        if not exists:
            status = "fail"
            details = f"File {fname} is missing"
        elif not valid:
            status = "fail"
            details = f"File {fname} exists but contains invalid JSON"
        else:
            status = "pass"
            details = f"File {fname} is valid ({size:,} bytes)"

        results.append({
            "name": check_name,
            "description": description,
            "status": status,
            "details": details,
            "count": size,
        })

    # Count all JSON data files
    json_count = 0
    for root, dirs, filenames in os.walk(data_dir):
        json_count += sum(1 for f in filenames if f.endswith(".json"))
    results.append({
        "name": "Game Data Files",
        "description": "Required JSON data files",
        "status": "pass" if json_count >= 10 else "warn",
        "details": f"{json_count} JSON files found in data directory",
        "count": json_count,
    })

    # Check hero images
    assets_dir = os.path.join(os.path.dirname(data_dir), "assets", "heroes")
    img_count = 0
    if os.path.isdir(assets_dir):
        img_count = sum(1 for f in os.listdir(assets_dir) if f.endswith((".png", ".jpg", ".jpeg")))
    results.append({
        "name": "Hero Image Files",
        "description": "Hero portraits in assets folder",
        "status": "pass" if img_count >= 40 else "warn" if img_count > 0 else "fail",
        "details": f"{img_count} hero images available",
        "count": img_count,
    })

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

    valid_actions = ("rebuild_hero_cache", "fix_orphaned_heroes", "fix_missing_profiles")
    if action not in valid_actions:
        raise ValidationError(f"Invalid action. Must be one of: {', '.join(valid_actions)}")

    fixed = 0
    if action == "rebuild_hero_cache":
        hero_repo._heroes_cache = None
        fixed = 1
    elif action == "fix_orphaned_heroes":
        # Stub - would scan for heroes without valid profiles
        fixed = 0
    elif action == "fix_missing_profiles":
        # Stub - would create default profiles for users without one
        fixed = 0

    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", f"integrity_fix_{action}", details=f"fixed={fixed}")

    return {"message": f"Action '{action}' completed", "fixed": fixed}


# --- Database (stubs for DynamoDB) ---

@app.get("/api/admin/database/backups")
def list_backups():
    _require_admin()
    return {"backups": []}


@app.post("/api/admin/database/backup")
def create_backup():
    _require_admin()
    return {"message": "DynamoDB uses point-in-time recovery. No manual backups needed."}


@app.post("/api/admin/database/cleanup/<action>")
def database_cleanup(action: str):
    _require_admin()
    admin_id = get_user_id(app.current_event.raw_event)
    admin_repo.log_audit(admin_id, "admin", "database_cleanup", details=action)
    return {"status": "ok", "action": action, "message": f"Cleanup action '{action}' processed."}


@app.post("/api/admin/database/query")
def database_query():
    _require_admin()
    return {"error": "SQL queries not supported with DynamoDB. Use the Database Browser to scan tables."}


# --- Database Browser ---

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

    # Map alias to actual table name
    alias_map = {
        "main": Config.MAIN_TABLE,
        "admin": Config.ADMIN_TABLE,
        "reference": Config.REFERENCE_TABLE,
    }
    actual_name = alias_map.get(tableName, tableName)

    # Verify table name is one of ours
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
    return app.resolve(event, context)
