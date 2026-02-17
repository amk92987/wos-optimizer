"""Chief gear and charms data access functions for DynamoDB."""

from datetime import datetime, timezone
from typing import Optional

from .db import get_table, strip_none, from_decimal


_DEFAULT_GEAR = {
    "helmet_quality": 1, "helmet_level": 1,
    "armor_quality": 1, "armor_level": 1,
    "gloves_quality": 1, "gloves_level": 1,
    "boots_quality": 1, "boots_level": 1,
    "ring_quality": 1, "ring_level": 1,
    "amulet_quality": 1, "amulet_level": 1,
}

_DEFAULT_CHARMS = {
    "cap_slot_1": "1", "cap_slot_2": "1", "cap_slot_3": "1",
    "watch_slot_1": "1", "watch_slot_2": "1", "watch_slot_3": "1",
    "coat_slot_1": "1", "coat_slot_2": "1", "coat_slot_3": "1",
    "pants_slot_1": "1", "pants_slot_2": "1", "pants_slot_3": "1",
    "belt_slot_1": "1", "belt_slot_2": "1", "belt_slot_3": "1",
    "weapon_slot_1": "1", "weapon_slot_2": "1", "weapon_slot_3": "1",
}


def get_chief_gear(profile_id: str) -> dict:
    """Get chief gear for a profile, creating defaults if needed."""
    table = get_table("main")
    resp = table.get_item(
        Key={"PK": f"PROFILE#{profile_id}", "SK": "CHIEFGEAR"}
    )
    item = resp.get("Item")

    if item:
        # Ensure all fields have defaults
        for key, default in _DEFAULT_GEAR.items():
            if key not in item or item[key] is None:
                item[key] = default
        return from_decimal(item)

    # Create default gear
    return _create_default_gear(profile_id)


def _create_default_gear(profile_id: str) -> dict:
    """Create default chief gear for a profile."""
    table = get_table("main")
    now = datetime.now(timezone.utc).isoformat()

    item = {
        "PK": f"PROFILE#{profile_id}",
        "SK": "CHIEFGEAR",
        "profile_id": profile_id,
        "updated_at": now,
        **_DEFAULT_GEAR,
    }

    table.put_item(Item=item)
    return item


def update_chief_gear(profile_id: str, updates: dict) -> dict:
    """Update chief gear fields."""
    table = get_table("main")

    # Ensure gear exists
    get_chief_gear(profile_id)

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

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
        return get_chief_gear(profile_id)

    resp = table.update_item(
        Key={"PK": f"PROFILE#{profile_id}", "SK": "CHIEFGEAR"},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return from_decimal(resp.get("Attributes", {}))


def get_chief_charms(profile_id: str) -> dict:
    """Get chief charms for a profile, creating defaults if needed."""
    table = get_table("main")
    resp = table.get_item(
        Key={"PK": f"PROFILE#{profile_id}", "SK": "CHIEFCHARM"}
    )
    item = resp.get("Item")

    if item:
        for key, default in _DEFAULT_CHARMS.items():
            if key not in item or item[key] is None:
                item[key] = default
        return from_decimal(item)

    return _create_default_charms(profile_id)


def _create_default_charms(profile_id: str) -> dict:
    """Create default chief charms for a profile."""
    table = get_table("main")
    now = datetime.now(timezone.utc).isoformat()

    item = {
        "PK": f"PROFILE#{profile_id}",
        "SK": "CHIEFCHARM",
        "profile_id": profile_id,
        "updated_at": now,
        **_DEFAULT_CHARMS,
    }

    table.put_item(Item=item)
    return item


def update_chief_charms(profile_id: str, updates: dict) -> dict:
    """Update chief charm fields."""
    table = get_table("main")

    # Ensure charms exist
    get_chief_charms(profile_id)

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

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
        return get_chief_charms(profile_id)

    resp = table.update_item(
        Key={"PK": f"PROFILE#{profile_id}", "SK": "CHIEFCHARM"},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return from_decimal(resp.get("Attributes", {}))
