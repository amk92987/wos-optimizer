"""User data access functions for DynamoDB."""

from datetime import datetime, timezone
from typing import Optional

from .config import Config
from .db import get_table, strip_none, transact_write_items
from .exceptions import ConflictError, NotFoundError


def get_user(user_id: str) -> Optional[dict]:
    """Get user by cognito_sub."""
    table = get_table("main")
    resp = table.get_item(Key={"PK": f"USER#{user_id}", "SK": "METADATA"})
    return resp.get("Item")


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email via GSI1-Email."""
    table = get_table("main")
    resp = table.query(
        IndexName="GSI1-Email",
        KeyConditionExpression="#email = :email AND SK = :sk",
        ExpressionAttributeNames={"#email": "email"},
        ExpressionAttributeValues={":email": email, ":sk": "METADATA"},
        Limit=1,
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def create_user(
    user_id: str,
    email: str,
    username: str,
    role: str = "user",
    is_test_account: bool = False,
    password_hash: str = "",
) -> dict:
    """Create user with uniqueness guards (transactional)."""
    now = datetime.now(timezone.utc).isoformat()

    user_item = strip_none({
        "PK": f"USER#{user_id}",
        "SK": "METADATA",
        "entity_type": "USER",
        "user_id": user_id,
        "email": email,
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "theme": "dark",
        "is_active": True,
        "is_verified": False,
        "is_test_account": is_test_account,
        "ai_requests_today": 0,
        "ai_access_level": "limited",
        "created_at": now,
        "updated_at": now,
    })

    email_guard = {
        "PK": "UNIQUE#EMAIL",
        "SK": email.lower(),
        "user_id": user_id,
    }

    username_guard = {
        "PK": "UNIQUE#USERNAME",
        "SK": username.lower(),
        "user_id": user_id,
    }

    table_name = Config.MAIN_TABLE

    try:
        transact_write_items([
            {
                "Put": {
                    "TableName": table_name,
                    "Item": user_item,
                    "ConditionExpression": "attribute_not_exists(PK)",
                }
            },
            {
                "Put": {
                    "TableName": table_name,
                    "Item": email_guard,
                    "ConditionExpression": "attribute_not_exists(PK) OR attribute_not_exists(SK)",
                }
            },
            {
                "Put": {
                    "TableName": table_name,
                    "Item": username_guard,
                    "ConditionExpression": "attribute_not_exists(PK) OR attribute_not_exists(SK)",
                }
            },
        ])
    except Exception as e:
        if "ConditionalCheckFailed" in str(e):
            raise ConflictError("Email or username already registered")
        raise

    return user_item


def update_user(user_id: str, updates: dict) -> dict:
    """Update user attributes."""
    table = get_table("main")
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
        Key={"PK": f"USER#{user_id}", "SK": "METADATA"},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def delete_user(user_id: str) -> None:
    """Delete user and all associated data."""
    table = get_table("main")

    # Get user to find email/username for guard cleanup
    user = get_user(user_id)
    if not user:
        raise NotFoundError("User not found")

    # Collect all items to delete
    items_to_delete = []

    # User metadata
    items_to_delete.append({"PK": f"USER#{user_id}", "SK": "METADATA"})

    # Email/username guards
    if user.get("email"):
        items_to_delete.append({"PK": "UNIQUE#EMAIL", "SK": user["email"].lower()})
    if user.get("username"):
        items_to_delete.append({"PK": "UNIQUE#USERNAME", "SK": user["username"].lower()})

    # All items with PK=USER#<id> (profiles, conversations, threads, notifications, logins)
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": f"USER#{user_id}"},
        ProjectionExpression="PK, SK",
    )
    for item in resp.get("Items", []):
        items_to_delete.append({"PK": item["PK"], "SK": item["SK"]})

    # Get profile IDs to delete their child items
    profiles = [i for i in resp.get("Items", []) if i["SK"].startswith("PROFILE#")]
    for profile_item in profiles:
        profile_id = profile_item["SK"].replace("PROFILE#", "")
        # Query all items under this profile
        profile_resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"PROFILE#{profile_id}"},
            ProjectionExpression="PK, SK",
        )
        for child in profile_resp.get("Items", []):
            items_to_delete.append({"PK": child["PK"], "SK": child["SK"]})

    # Batch delete (25 items per batch)
    with table.batch_writer() as batch:
        for item_key in items_to_delete:
            batch.delete_item(Key=item_key)


def soft_delete_user(user_id: str) -> dict:
    """Soft-delete a user by setting deleted_at and deactivating."""
    table = get_table("main")
    now = datetime.now(timezone.utc).isoformat()

    resp = table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": "METADATA"},
        UpdateExpression="SET deleted_at = :now, is_active = :false, updated_at = :now2",
        ExpressionAttributeValues={":now": now, ":false": False, ":now2": now},
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def restore_user(user_id: str) -> dict:
    """Restore a soft-deleted user by removing deleted_at and reactivating."""
    table = get_table("main")
    now = datetime.now(timezone.utc).isoformat()

    resp = table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": "METADATA"},
        UpdateExpression="REMOVE deleted_at SET is_active = :true, updated_at = :now",
        ExpressionAttributeValues={":true": True, ":now": now},
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def get_deleted_users(limit: int = 500) -> list:
    """List soft-deleted users (those with deleted_at set)."""
    table = get_table("main")

    params = {
        "IndexName": "GSI4-AdminUserList",
        "KeyConditionExpression": "entity_type = :et",
        "FilterExpression": "attribute_exists(deleted_at)",
        "ExpressionAttributeValues": {":et": "USER"},
        "ScanIndexForward": False,
    }

    items = []
    while True:
        resp = table.query(**params)
        items.extend(resp.get("Items", []))
        if len(items) >= limit or "LastEvaluatedKey" not in resp:
            break
        params["ExclusiveStartKey"] = resp["LastEvaluatedKey"]

    return items[:limit]


def get_expired_deleted_users(grace_days: int = 30) -> list:
    """Get soft-deleted users whose grace period has expired."""
    from datetime import timedelta

    cutoff = (datetime.now(timezone.utc) - timedelta(days=grace_days)).isoformat()
    deleted = get_deleted_users(limit=1000)
    return [u for u in deleted if u.get("deleted_at", "") < cutoff]


def record_daily_login(user_id: str) -> None:
    """Record a daily login (idempotent - one per day)."""
    table = get_table("main")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    table.put_item(
        Item={
            "PK": f"USER#{user_id}",
            "SK": f"LOGIN#{today}",
            "login_date": today,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        ConditionExpression="attribute_not_exists(PK) OR attribute_not_exists(SK)",
    )


def get_login_count_last_n_days(user_id: str, days: int = 7) -> int:
    """Count unique login days in the last N days."""
    from datetime import timedelta

    table = get_table("main")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    resp = table.query(
        KeyConditionExpression="PK = :pk AND SK BETWEEN :start AND :end",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":start": f"LOGIN#{start_date}",
            ":end": f"LOGIN#9999-12-31",
        },
        Select="COUNT",
    )
    return resp.get("Count", 0)


def list_users(test_only: bool = False, include_deleted: bool = False, limit: int = 500) -> list:
    """List all users via GSI4-AdminUserList.

    Paginates through all DynamoDB result pages to ensure FilterExpression
    doesn't cause missing results, then truncates to `limit` in Python.
    By default excludes soft-deleted users (those with deleted_at set).
    """
    table = get_table("main")

    filter_parts = []
    expr_values = {":et": "USER"}

    if not include_deleted:
        filter_parts.append("attribute_not_exists(deleted_at)")

    if test_only:
        filter_parts.append("is_test_account = :t")
        expr_values[":t"] = True

    params = {
        "IndexName": "GSI4-AdminUserList",
        "KeyConditionExpression": "entity_type = :et",
        "ExpressionAttributeValues": expr_values,
        "ScanIndexForward": False,
    }

    if filter_parts:
        params["FilterExpression"] = " AND ".join(filter_parts)

    items = []
    while True:
        resp = table.query(**params)
        items.extend(resp.get("Items", []))
        if len(items) >= limit or "LastEvaluatedKey" not in resp:
            break
        params["ExclusiveStartKey"] = resp["LastEvaluatedKey"]

    return items[:limit]


def increment_ai_requests(user_id: str) -> dict:
    """Atomically increment AI request counter."""
    table = get_table("main")
    now = datetime.now(timezone.utc).isoformat()

    resp = table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": "METADATA"},
        UpdateExpression="SET ai_requests_today = if_not_exists(ai_requests_today, :zero) + :one, last_ai_request = :now",
        ExpressionAttributeValues={":one": 1, ":zero": 0, ":now": now},
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def reset_ai_request_counter(user_id: str) -> None:
    """Reset daily AI request counter."""
    table = get_table("main")

    table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": "METADATA"},
        UpdateExpression="SET ai_requests_today = :zero",
        ExpressionAttributeValues={":zero": 0},
    )
