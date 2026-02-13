"""Admin data access functions for DynamoDB (AdminTable)."""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from .db import get_table, strip_none


def _generate_ulid() -> str:
    ts = int(time.time() * 1000)
    rand = uuid.uuid4().hex[:16]
    return f"{ts:012x}{rand}"


# --- Feature Flags ---

DEFAULT_FLAGS = [
    {"name": "hero_recommendations", "description": "AI-powered hero upgrade recommendations", "is_enabled": True},
    {"name": "inventory_ocr", "description": "Screenshot scanning for inventory", "is_enabled": False},
    {"name": "alliance_features", "description": "Alliance management and coordination", "is_enabled": False},
    {"name": "beta_features", "description": "Experimental features in testing", "is_enabled": False},
    {"name": "maintenance_mode", "description": "Show maintenance notice to users", "is_enabled": False},
    {"name": "new_user_onboarding", "description": "Guided setup for new users", "is_enabled": True},
    {"name": "dark_theme_only", "description": "Override user theme preference", "is_enabled": False},
    {"name": "analytics_tracking", "description": "Detailed usage analytics collection", "is_enabled": True},
]


def get_feature_flags() -> list:
    """Get all feature flags, seeding defaults if empty."""
    table = get_table("admin")
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": "FLAG"},
    )
    flags = resp.get("Items", [])

    if not flags:
        # Seed defaults
        for flag_data in DEFAULT_FLAGS:
            _create_flag(flag_data["name"], flag_data.get("description"), flag_data.get("is_enabled", False))
        return get_feature_flags()

    return flags


def get_feature_flag(flag_name: str) -> Optional[dict]:
    """Get a specific feature flag."""
    table = get_table("admin")
    resp = table.get_item(Key={"PK": "FLAG", "SK": flag_name})
    return resp.get("Item")


def _create_flag(name: str, description: Optional[str] = None, is_enabled: bool = False) -> dict:
    """Create a feature flag."""
    table = get_table("admin")
    now = datetime.now(timezone.utc).isoformat()

    item = strip_none({
        "PK": "FLAG",
        "SK": name,
        "name": name,
        "description": description,
        "is_enabled": is_enabled,
        "created_at": now,
        "updated_at": now,
    })

    table.put_item(Item=item)
    return item


def create_feature_flag(name: str, description: Optional[str] = None, is_enabled: bool = False) -> dict:
    """Create a new feature flag (public API)."""
    clean_name = name.lower().replace(" ", "_")
    existing = get_feature_flag(clean_name)
    if existing:
        from .exceptions import ConflictError
        raise ConflictError("Flag with this name already exists")
    return _create_flag(clean_name, description, is_enabled)


def update_feature_flag(flag_name: str, updates: dict) -> dict:
    """Update a feature flag."""
    table = get_table("admin")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    if "name" in updates:
        updates["name"] = updates["name"].lower().replace(" ", "_")

    expr_parts = []
    attr_names = {}
    attr_values = {}

    for i, (key, value) in enumerate(updates.items()):
        placeholder = f":v{i}"
        name_placeholder = f"#k{i}"
        expr_parts.append(f"{name_placeholder} = {placeholder}")
        attr_names[name_placeholder] = key
        attr_values[placeholder] = value

    resp = table.update_item(
        Key={"PK": "FLAG", "SK": flag_name},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def delete_feature_flag(flag_name: str) -> None:
    """Delete a feature flag."""
    table = get_table("admin")
    table.delete_item(Key={"PK": "FLAG", "SK": flag_name})


def bulk_flag_action(action: str) -> None:
    """Perform bulk action on flags."""
    table = get_table("admin")

    if action == "enable_all":
        flags = get_feature_flags()
        for f in flags:
            update_feature_flag(f["SK"], {"is_enabled": True})

    elif action == "disable_all":
        flags = get_feature_flags()
        for f in flags:
            update_feature_flag(f["SK"], {"is_enabled": False})

    elif action == "reset_defaults":
        # Delete all existing
        flags = get_feature_flags()
        for f in flags:
            delete_feature_flag(f["SK"])
        # Recreate defaults
        for flag_data in DEFAULT_FLAGS:
            _create_flag(flag_data["name"], flag_data.get("description"), flag_data.get("is_enabled", False))


# --- Announcements ---

def get_announcements(active_only: bool = False) -> list:
    """Get all announcements."""
    table = get_table("admin")
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": "ANNOUNCE"},
        ScanIndexForward=False,
    )
    items = resp.get("Items", [])

    if active_only:
        items = [a for a in items if a.get("is_active", True)]

    return items


def create_announcement(
    title: str,
    message: str,
    created_by: str,
    announcement_type: str = "info",
    display_type: str = "banner",
    inbox_content: Optional[str] = None,
    show_from: Optional[str] = None,
    show_until: Optional[str] = None,
) -> dict:
    """Create a new announcement."""
    table = get_table("admin")
    ulid = _generate_ulid()
    now = datetime.now(timezone.utc).isoformat()

    item = strip_none({
        "PK": "ANNOUNCE",
        "SK": ulid,
        "announcement_id": ulid,
        "title": title,
        "message": message,
        "type": announcement_type,
        "display_type": display_type,
        "inbox_content": inbox_content,
        "is_active": True,
        "show_from": show_from,
        "show_until": show_until,
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    })

    table.put_item(Item=item)
    return item


def update_announcement(announcement_id: str, updates: dict) -> dict:
    """Update an announcement."""
    table = get_table("admin")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    expr_parts = []
    attr_names = {}
    attr_values = {}

    for i, (key, value) in enumerate(updates.items()):
        placeholder = f":v{i}"
        name_placeholder = f"#k{i}"
        expr_parts.append(f"{name_placeholder} = {placeholder}")
        attr_names[name_placeholder] = key
        attr_values[placeholder] = value

    resp = table.update_item(
        Key={"PK": "ANNOUNCE", "SK": announcement_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def delete_announcement(announcement_id: str) -> None:
    """Delete an announcement."""
    table = get_table("admin")
    table.delete_item(Key={"PK": "ANNOUNCE", "SK": announcement_id})


# --- Feedback ---

def create_feedback(
    user_id: str,
    category: str,
    description: str,
    page: Optional[str] = None,
) -> dict:
    """Create a feedback item."""
    table = get_table("admin")
    ulid = _generate_ulid()
    now = datetime.now(timezone.utc).isoformat()

    # Determine initial status
    if category == "bug":
        status = "pending_fix"
    elif category in ["feature", "bad_recommendation"]:
        status = "pending_update"
    else:
        status = "new"

    item = strip_none({
        "PK": "FEEDBACK",
        "SK": f"{now}#{ulid}",
        "feedback_id": ulid,
        "user_id": user_id,
        "category": category,
        "description": description,
        "page": page,
        "status": status,
        "created_at": now,
    })

    table.put_item(Item=item)
    return item


def get_feedback(status_filter: Optional[str] = None, category_filter: Optional[str] = None) -> list:
    """Get feedback items."""
    table = get_table("admin")

    if status_filter:
        resp = table.query(
            IndexName="GSI1-Status",
            KeyConditionExpression="#s = :status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": status_filter},
            ScanIndexForward=False,
        )
    else:
        resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": "FEEDBACK"},
            ScanIndexForward=False,
        )

    items = resp.get("Items", [])
    if category_filter:
        items = [f for f in items if f.get("category") == category_filter]

    return items


def update_feedback(feedback_sk: str, updates: dict) -> dict:
    """Update a feedback item's status."""
    table = get_table("admin")

    expr_parts = []
    attr_names = {}
    attr_values = {}

    for i, (key, value) in enumerate(updates.items()):
        placeholder = f":v{i}"
        name_placeholder = f"#k{i}"
        expr_parts.append(f"{name_placeholder} = {placeholder}")
        attr_names[name_placeholder] = key
        attr_values[placeholder] = value

    resp = table.update_item(
        Key={"PK": "FEEDBACK", "SK": feedback_sk},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


# --- Audit Log ---

def log_audit(
    admin_id: str,
    admin_username: str,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    target_name: Optional[str] = None,
    details: Optional[str] = None,
) -> dict:
    """Log an admin action."""
    table = get_table("admin")
    ulid = _generate_ulid()
    now = datetime.now(timezone.utc)
    month = now.strftime("%Y-%m")

    item = strip_none({
        "PK": f"AUDIT#{month}",
        "SK": f"{now.isoformat()}#{ulid}",
        "admin_id": admin_id,
        "admin_username": admin_username,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "target_name": target_name,
        "details": details,
        "created_at": now.isoformat(),
    })

    table.put_item(Item=item)
    return item


def get_audit_logs(month: Optional[str] = None, limit: int = 100) -> list:
    """Get audit logs, optionally filtered by month."""
    table = get_table("admin")

    if month is None:
        month = datetime.now(timezone.utc).strftime("%Y-%m")

    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": f"AUDIT#{month}"},
        ScanIndexForward=False,
        Limit=limit,
    )
    return resp.get("Items", [])


# --- Error Logs ---

def log_error(
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    page: Optional[str] = None,
    function: Optional[str] = None,
    user_id: Optional[str] = None,
    environment: Optional[str] = None,
) -> dict:
    """Log an application error."""
    table = get_table("admin")
    ulid = _generate_ulid()
    now = datetime.now(timezone.utc)
    month = now.strftime("%Y-%m")

    item = strip_none({
        "PK": "ERRORS",
        "SK": f"{now.isoformat()}#{ulid}",
        "error_id": ulid,
        "error_type": error_type,
        "error_message": error_message,
        "stack_trace": stack_trace,
        "page": page,
        "function": function,
        "user_id": user_id,
        "environment": environment,
        "status": "new",
        "created_at": now.isoformat(),
    })

    table.put_item(Item=item)

    # Send email notification (rate-limited)
    try:
        send_error_notification(item)
    except Exception:
        pass  # Never break error logging

    return item


def get_errors(limit: int = 100) -> list:
    """Get error logs, newest first."""
    table = get_table("admin")
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": "ERRORS"},
        ScanIndexForward=False,
        Limit=limit,
    )
    items = resp.get("Items", [])
    # Add 'id' field for frontend (use error_id which is URL-safe)
    for item in items:
        item["id"] = item.get("error_id", item.get("SK", ""))
    return items


def _find_error_by_id(error_id: str) -> dict | None:
    """Find an error item by its error_id (ULID). Returns the item or None."""
    table = get_table("admin")
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        FilterExpression="error_id = :eid",
        ExpressionAttributeValues={":pk": "ERRORS", ":eid": error_id},
    )
    items = resp.get("Items", [])
    return items[0] if items else None


# Module-level rate limiter for error emails
_last_error_email_time: float = 0


def send_error_notification(error_item: dict) -> None:
    """Send SES email for new error. Rate limited: max 1 per 5 minutes per Lambda instance."""
    import boto3
    global _last_error_email_time

    now = time.time()
    if now - _last_error_email_time < 300:  # 5 minutes
        return
    _last_error_email_time = now

    from .config import Config
    if Config.IS_LOCAL:
        return

    try:
        ses = boto3.client("ses", region_name=Config.REGION)

        stage = Config.STAGE.upper()
        domain = "wosdev.randomchaoslabs.com" if Config.STAGE == "dev" else "wos.randomchaoslabs.com"
        admin_url = f"https://{domain}/admin/inbox"

        body = f"""New Error in {stage} environment

Type: {error_item.get('error_type', 'Unknown')}
Message: {error_item.get('error_message', 'No message')[:500]}
Handler: {error_item.get('page', 'Unknown')}
User: {error_item.get('user_id', 'N/A')}
Time: {error_item.get('created_at', 'Unknown')}

Stack Trace:
{error_item.get('stack_trace', 'No stack trace')[:2000]}

View in Admin Panel: {admin_url}
"""

        ses.send_email(
            Source=Config.SES_FROM_EMAIL,
            Destination={"ToAddresses": ["wos@randomchaoslabs.com"]},
            Message={
                "Subject": {"Data": f"[WoS {stage}] Error: {error_item.get('error_type', 'Unknown')}"},
                "Body": {"Text": {"Data": body}},
            },
        )
    except Exception:
        pass  # Never let email failure break error logging


# --- Admin Metrics ---

def save_daily_metrics(metrics: dict) -> dict:
    """Save daily metrics snapshot."""
    table = get_table("admin")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    item = {
        "PK": "METRICS",
        "SK": today,
        "date": today,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **metrics,
    }

    table.put_item(Item=item)
    return item


def get_metrics_history(days: int = 90) -> list:
    """Get historical metrics."""
    from datetime import timedelta
    table = get_table("admin")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    resp = table.query(
        KeyConditionExpression="PK = :pk AND SK >= :start",
        ExpressionAttributeValues={
            ":pk": "METRICS",
            ":start": start_date,
        },
        ScanIndexForward=True,
    )
    return resp.get("Items", [])
