"""Admin Lambda handler."""

import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from backend.common.auth import get_effective_user_id, require_admin, is_admin, get_user_id
from backend.common.exceptions import AppError, NotFoundError, ValidationError
from backend.common.config import Config
from backend.common import admin_repo, user_repo, ai_repo, profile_repo
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
    return {"users": users}


@app.post("/api/admin/users")
def create_user():
    _require_admin()
    body = app.current_event.json_body or {}

    email = body.get("email")
    username = body.get("username", email)
    role = body.get("role", "user")
    is_test = body.get("is_test_account", False)
    password_hash = body.get("password_hash", "")

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

    allowed = {"role", "is_active", "is_verified", "is_test_account", "ai_daily_limit", "ai_access_level", "theme"}
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

    allowed = {"mode", "daily_limit_free", "daily_limit_admin", "cooldown_seconds", "primary_provider", "fallback_provider", "openai_model", "anthropic_model"}
    updates = {k: v for k, v in body.items() if k in allowed}

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
    return {"announcement": announcement}, 201


@app.put("/api/admin/announcements/<announcementId>")
def update_announcement(announcementId: str):
    _require_admin()
    body = app.current_event.json_body or {}

    allowed = {"title", "message", "type", "display_type", "inbox_content", "is_active", "show_from", "show_until"}
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


# --- AI Conversations ---

@app.get("/api/admin/ai-conversations")
def list_ai_conversations():
    _require_admin()
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "50"))

    # Scan all conversations across users via admin table or main table query
    # For admin, we list recent conversations from all users
    table = get_table("main")
    resp = table.scan(
        FilterExpression="begins_with(SK, :prefix)",
        ExpressionAttributeValues={":prefix": "AICONV#"},
        Limit=limit,
    )
    conversations = resp.get("Items", [])
    conversations.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    return {"conversations": conversations[:limit]}


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

    if format not in ("json", "csv"):
        raise ValidationError("Format must be json or csv")

    alias_map = {
        "main": Config.MAIN_TABLE,
        "admin": Config.ADMIN_TABLE,
        "reference": Config.REFERENCE_TABLE,
    }
    actual_name = alias_map.get(table_name, table_name)

    valid_tables = {Config.MAIN_TABLE, Config.ADMIN_TABLE, Config.REFERENCE_TABLE}
    if actual_name not in valid_tables:
        raise ValidationError(f"Unknown table: {table_name}")

    table = get_table(actual_name)
    resp = table.scan()
    items = resp.get("Items", [])

    if format == "json":
        return {"table": actual_name, "items": items, "count": len(items)}

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


def lambda_handler(event, context):
    return app.resolve(event, context)
