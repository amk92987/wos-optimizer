"""Profile data access functions for DynamoDB."""

from datetime import datetime, timezone
from typing import Optional
import time
import uuid

from .config import Config
from .db import get_table, strip_none
from .exceptions import NotFoundError, ValidationError


def _generate_ulid() -> str:
    """Generate a ULID-like sortable unique ID."""
    ts = int(time.time() * 1000)
    rand = uuid.uuid4().hex[:16]
    return f"{ts:012x}{rand}"


def _migrate_priority_fields(item: dict) -> dict:
    """Migrate old 5-priority fields to new 4-priority fields if needed."""
    if item and 'priority_pvp_attack' not in item and 'priority_svs' in item:
        item['priority_pvp_attack'] = max(
            int(item.get('priority_svs', 5)),
            int(item.get('priority_rally', 4))
        )
        item['priority_defense'] = int(item.get('priority_castle_battle', 4))
        item['priority_pve'] = int(item.get('priority_exploration', 3))
        item['priority_economy'] = int(item.get('priority_gathering', 2))
    return item


def get_profile(user_id: str, profile_id: str) -> Optional[dict]:
    """Get a specific profile."""
    table = get_table("main")
    resp = table.get_item(Key={"PK": f"USER#{user_id}", "SK": f"PROFILE#{profile_id}"})
    item = resp.get("Item")
    return _migrate_priority_fields(item) if item else None


def get_profiles(user_id: str, include_deleted: bool = False) -> list:
    """Get all profiles for a user."""
    table = get_table("main")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":prefix": "PROFILE#",
        },
    )
    items = resp.get("Items", [])
    if not include_deleted:
        items = [p for p in items if not p.get("deleted_at")]
    return [_migrate_priority_fields(p) for p in items]


def get_deleted_profiles(user_id: str) -> list:
    """Get soft-deleted profiles for a user."""
    table = get_table("main")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"USER#{user_id}",
            ":prefix": "PROFILE#",
        },
    )
    return [_migrate_priority_fields(p) for p in resp.get("Items", []) if p.get("deleted_at")]


def get_default_profile(user_id: str) -> Optional[dict]:
    """Get the user's default (active) profile."""
    profiles = get_profiles(user_id)
    # Return the default profile, or first profile, or None
    for p in profiles:
        if p.get("is_default"):
            return p
    return profiles[0] if profiles else None


def get_or_create_profile(user_id: str) -> dict:
    """Get default profile or create one if none exist."""
    profile = get_default_profile(user_id)
    if profile:
        return profile
    return create_profile(user_id, name="Chief")


def create_profile(
    user_id: str,
    name: str = "Chief",
    state_number: Optional[int] = None,
    is_farm_account: bool = False,
) -> dict:
    """Create a new profile."""
    table = get_table("main")
    profile_id = _generate_ulid()
    now = datetime.now(timezone.utc).isoformat()

    item = strip_none({
        "PK": f"USER#{user_id}",
        "SK": f"PROFILE#{profile_id}",
        "profile_id": profile_id,
        "user_id": user_id,
        "name": name,
        "is_default": False,
        "state_number": state_number,
        "server_age_days": 0,
        "furnace_level": 1,
        "spending_profile": "f2p",
        "priority_focus": "balanced_growth",
        "alliance_role": "filler",
        "priority_pvp_attack": 5,
        "priority_defense": 4,
        "priority_pve": 3,
        "priority_economy": 2,
        "is_farm_account": is_farm_account,
        "created_at": now,
        "updated_at": now,
    })

    table.put_item(Item=item)
    return item


def update_profile(user_id: str, profile_id: str, updates: dict) -> dict:
    """Update a profile's attributes."""
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
        Key={"PK": f"USER#{user_id}", "SK": f"PROFILE#{profile_id}"},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def delete_profile(user_id: str, profile_id: str, hard: bool = False) -> dict:
    """Soft-delete or hard-delete a profile."""
    table = get_table("main")

    if hard:
        # Delete profile and all child items (heroes, gear, charms, inventory)
        _delete_profile_children(profile_id)
        table.delete_item(Key={"PK": f"USER#{user_id}", "SK": f"PROFILE#{profile_id}"})
        return {"status": "deleted", "permanent": True}
    else:
        now = datetime.now(timezone.utc).isoformat()
        table.update_item(
            Key={"PK": f"USER#{user_id}", "SK": f"PROFILE#{profile_id}"},
            UpdateExpression="SET deleted_at = :now",
            ExpressionAttributeValues={":now": now},
        )
        return {"status": "deleted", "permanent": False}


def restore_profile(user_id: str, profile_id: str) -> dict:
    """Restore a soft-deleted profile."""
    table = get_table("main")
    table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": f"PROFILE#{profile_id}"},
        UpdateExpression="REMOVE deleted_at",
    )
    return {"status": "restored", "profile_id": profile_id}


def activate_profile(user_id: str, profile_id: str) -> None:
    """Set a profile as the default/active profile."""
    # Unset all other profiles' is_default
    profiles = get_profiles(user_id)
    table = get_table("main")

    for p in profiles:
        if p.get("is_default"):
            table.update_item(
                Key={"PK": p["PK"], "SK": p["SK"]},
                UpdateExpression="SET is_default = :f",
                ExpressionAttributeValues={":f": False},
            )

    # Set the target profile as default
    table.update_item(
        Key={"PK": f"USER#{user_id}", "SK": f"PROFILE#{profile_id}"},
        UpdateExpression="SET is_default = :t",
        ExpressionAttributeValues={":t": True},
    )


def duplicate_profile(user_id: str, source_profile_id: str, new_name: str) -> dict:
    """Duplicate a profile with all its heroes."""
    source = get_profile(user_id, source_profile_id)
    if not source:
        raise NotFoundError("Profile not found")

    # Create new profile with same settings
    new_profile = create_profile(
        user_id=user_id,
        name=new_name,
        state_number=source.get("state_number"),
        is_farm_account=False,
    )
    new_profile_id = new_profile["profile_id"]

    # Copy settings
    settings_fields = [
        "server_age_days", "furnace_level", "furnace_fc_level",
        "spending_profile", "priority_focus", "alliance_role",
        "priority_pvp_attack", "priority_defense",
        "priority_pve", "priority_economy",
    ]
    updates = {k: source[k] for k in settings_fields if k in source and source[k] is not None}
    if updates:
        update_profile(user_id, new_profile_id, updates)

    # Copy heroes using batch_writer for efficiency
    from .hero_repo import get_heroes
    heroes = get_heroes(source_profile_id)
    if heroes:
        table = get_table("main")
        now = datetime.now(timezone.utc).isoformat()
        with table.batch_writer() as batch:
            for hero in heroes:
                hero_name = hero["SK"].replace("HERO#", "")
                item = {k: v for k, v in hero.items() if k not in ("PK", "SK", "created_at", "updated_at")}
                item["PK"] = f"PROFILE#{new_profile_id}"
                item["SK"] = f"HERO#{hero_name}"
                item["profile_id"] = new_profile_id
                item["created_at"] = now
                item["updated_at"] = now
                batch.put_item(Item=strip_none(item))

    return get_profile(user_id, new_profile_id)


def get_hero_count(profile_id: str) -> int:
    """Get count of heroes in a profile."""
    table = get_table("main")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"PROFILE#{profile_id}",
            ":prefix": "HERO#",
        },
        Select="COUNT",
    )
    return resp.get("Count", 0)


def _delete_profile_children(profile_id: str) -> None:
    """Delete all items under a profile (heroes, gear, charms, inventory)."""
    table = get_table("main")
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": f"PROFILE#{profile_id}"},
        ProjectionExpression="PK, SK",
    )
    with table.batch_writer() as batch:
        for item in resp.get("Items", []):
            batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
