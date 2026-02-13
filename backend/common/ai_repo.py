"""AI conversation and settings data access functions for DynamoDB."""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from .db import get_table, strip_none
from .exceptions import RateLimitError


def _generate_ulid() -> str:
    ts = int(time.time() * 1000)
    rand = uuid.uuid4().hex[:16]
    return f"{ts:012x}{rand}"


# --- AI Settings ---

def get_ai_settings() -> dict:
    """Get global AI settings from AdminTable."""
    table = get_table("admin")
    resp = table.get_item(Key={"PK": "SETTINGS", "SK": "AI"})
    item = resp.get("Item")

    if item:
        return item

    # Return defaults
    return {
        "PK": "SETTINGS",
        "SK": "AI",
        "mode": "on",
        "daily_limit_free": 20,
        "daily_limit_admin": 1000,
        "cooldown_seconds": 30,
        "primary_provider": "openai",
        "fallback_provider": None,
        "openai_model": "gpt-4o-mini",
        "anthropic_model": "claude-sonnet-4-20250514",
        "total_requests": 0,
        "total_tokens_used": 0,
    }


def update_ai_settings(updates: dict) -> dict:
    """Update AI settings."""
    table = get_table("admin")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Ensure item exists
    settings = get_ai_settings()
    if "PK" not in settings or settings.get("PK") != "SETTINGS":
        # Create the settings item
        item = {
            "PK": "SETTINGS",
            "SK": "AI",
            "mode": "on",
            "daily_limit_free": 20,
            "daily_limit_admin": 1000,
            "cooldown_seconds": 30,
            "primary_provider": "openai",
            **updates,
        }
        table.put_item(Item=strip_none(item))
        return item

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
        Key={"PK": "SETTINGS", "SK": "AI"},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


# --- Rate Limiting ---

def check_rate_limit(user: dict, settings: Optional[dict] = None) -> tuple:
    """Check if user can make an AI request. Returns (allowed, message, remaining)."""
    if settings is None:
        settings = get_ai_settings()

    mode = settings.get("mode", "on")

    if mode == "off":
        return False, "AI is currently disabled", 0

    if mode == "unlimited":
        return True, "", 999

    role = user.get("role", "user")
    daily_limit = user.get("ai_daily_limit")
    if daily_limit is None:
        daily_limit = settings.get("daily_limit_admin", 1000) if role == "admin" else settings.get("daily_limit_free", 20)

    requests_today = user.get("ai_requests_today", 0)

    # Check if counter needs reset (new day)
    reset_date = user.get("ai_request_reset_date", "")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if reset_date != today:
        requests_today = 0

    remaining = max(0, daily_limit - requests_today)

    if requests_today >= daily_limit:
        return False, f"Daily limit reached ({daily_limit} requests). Resets at midnight UTC.", 0

    # Check cooldown
    cooldown = settings.get("cooldown_seconds", 30)
    last_request = user.get("last_ai_request")
    if last_request and cooldown > 0:
        try:
            last_dt = datetime.fromisoformat(last_request.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
            if elapsed < cooldown:
                wait = int(cooldown - elapsed)
                return False, f"Please wait {wait} seconds between requests.", remaining
        except (ValueError, TypeError):
            pass

    return True, "", remaining


# --- AI Conversations ---

def log_conversation(
    user_id: str,
    profile_id: Optional[str],
    question: str,
    answer: str,
    source: str = "rules",
    provider: str = "rules",
    model: str = "rule_engine",
    context_summary: str = "",
    user_snapshot: str = "",
    tokens_input: int = 0,
    tokens_output: int = 0,
    response_time_ms: int = 0,
    thread_id: Optional[str] = None,
) -> dict:
    """Log an AI conversation to MainTable."""
    table = get_table("main")
    ulid = _generate_ulid()
    now = datetime.now(timezone.utc).isoformat()

    item = strip_none({
        "PK": f"USER#{user_id}",
        "SK": f"AICONV#{now}#{ulid}",
        "conversation_id": ulid,
        "user_id": user_id,
        "profile_id": profile_id,
        "question": question,
        "answer": answer,
        "context_summary": context_summary,
        "user_snapshot": user_snapshot,
        "provider": provider,
        "model": model,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "response_time_ms": response_time_ms,
        "routed_to": source,
        "is_favorite": False,
        "is_good_example": False,
        "is_bad_example": False,
        "thread_id": thread_id,
        "created_at": now,
    })

    table.put_item(Item=item)
    return item


def get_conversation_history(user_id: str, limit: int = 10) -> list:
    """Get recent conversations for a user."""
    table = get_table("main")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":prefix": "AICONV#",
        },
        ScanIndexForward=False,
        Limit=limit,
    )
    return resp.get("Items", [])


def get_favorites(user_id: str, limit: int = 20) -> list:
    """Get favorited conversations."""
    table = get_table("main")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        FilterExpression="is_favorite = :t",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":prefix": "AICONV#",
            ":t": True,
        },
        ScanIndexForward=False,
        Limit=limit,
    )
    return resp.get("Items", [])


def rate_conversation(user_id: str, conversation_sk: str, updates: dict) -> dict:
    """Rate or provide feedback on a conversation."""
    table = get_table("main")

    expr_parts = []
    attr_names = {}
    attr_values = {}

    for i, (key, value) in enumerate(updates.items()):
        if value is None:
            continue
        placeholder = f":v{i}"
        name_placeholder = f"#k{i}"
        expr_parts.append(f"{name_placeholder} = {placeholder}")
        attr_names[name_placeholder] = key
        attr_values[placeholder] = value

    if not expr_parts:
        return {}

    resp = table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": conversation_sk},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def delete_conversation(user_id: str, conversation_sk: str) -> bool:
    """Delete a single AI conversation. Returns True if deleted."""
    table = get_table("main")
    sk = conversation_sk if conversation_sk.startswith("AICONV#") else f"AICONV#{conversation_sk}"
    table.delete_item(Key={"PK": f"USER#{user_id}", "SK": sk})
    return True


def delete_thread(user_id: str, thread_id: str) -> int:
    """Delete all conversations in a thread. Returns count deleted."""
    table = get_table("main")
    conversations = get_conversation_history(user_id, limit=200)
    count = 0
    with table.batch_writer() as batch:
        for conv in conversations:
            if conv.get("thread_id") == thread_id:
                batch.delete_item(Key={"PK": conv["PK"], "SK": conv["SK"]})
                count += 1
    return count


def delete_conversation_history(user_id: str) -> int:
    """Delete all AI conversations for a user. Returns count deleted."""
    table = get_table("main")
    # Query all AICONV items
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":prefix": "AICONV#",
        },
        ProjectionExpression="PK, SK",
    )
    items = resp.get("Items", [])
    count = 0
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
            count += 1
    return count


def toggle_favorite(user_id: str, conversation_sk: str) -> bool:
    """Toggle favorite status. Returns new status."""
    table = get_table("main")

    # Get current status
    resp = table.get_item(Key={"PK": f"USER#{user_id}", "SK": conversation_sk})
    item = resp.get("Item", {})
    new_status = not item.get("is_favorite", False)

    table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": conversation_sk},
        UpdateExpression="SET is_favorite = :val",
        ExpressionAttributeValues={":val": new_status},
    )
    return new_status
