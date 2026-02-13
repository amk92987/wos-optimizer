"""Hero data access functions for DynamoDB."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

from .config import Config
from .db import get_table, strip_none
from .exceptions import NotFoundError


def get_heroes(profile_id: str) -> list:
    """Get all heroes for a profile."""
    table = get_table("main")
    resp = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
        ExpressionAttributeValues={
            ":pk": f"PROFILE#{profile_id}",
            ":prefix": "HERO#",
        },
    )
    return resp.get("Items", [])


def get_hero(profile_id: str, hero_name: str) -> Optional[dict]:
    """Get a specific hero for a profile."""
    table = get_table("main")
    resp = table.get_item(
        Key={"PK": f"PROFILE#{profile_id}", "SK": f"HERO#{hero_name}"}
    )
    return resp.get("Item")


def put_hero(profile_id: str, hero_name: str, data: dict) -> dict:
    """Create or update a hero for a profile."""
    table = get_table("main")
    now = datetime.now(timezone.utc).isoformat()

    item = strip_none({
        "PK": f"PROFILE#{profile_id}",
        "SK": f"HERO#{hero_name}",
        "hero_name": hero_name,
        "profile_id": profile_id,
        "level": data.get("level", 1),
        "stars": data.get("stars", 0),
        "ascension_tier": data.get("ascension", data.get("ascension_tier", 0)),
        # Exploration skills
        "exploration_skill_1_level": data.get("exploration_skill_1", data.get("exploration_skill_1_level", 1)),
        "exploration_skill_2_level": data.get("exploration_skill_2", data.get("exploration_skill_2_level", 1)),
        "exploration_skill_3_level": data.get("exploration_skill_3", data.get("exploration_skill_3_level", 1)),
        # Expedition skills
        "expedition_skill_1_level": data.get("expedition_skill_1", data.get("expedition_skill_1_level", 1)),
        "expedition_skill_2_level": data.get("expedition_skill_2", data.get("expedition_skill_2_level", 1)),
        "expedition_skill_3_level": data.get("expedition_skill_3", data.get("expedition_skill_3_level", 1)),
        # Gear slots
        "gear_slot1_quality": data.get("gear_slot1_quality", 0),
        "gear_slot1_level": data.get("gear_slot1_level", 0),
        "gear_slot1_mastery": data.get("gear_slot1_mastery", 0),
        "gear_slot2_quality": data.get("gear_slot2_quality", 0),
        "gear_slot2_level": data.get("gear_slot2_level", 0),
        "gear_slot2_mastery": data.get("gear_slot2_mastery", 0),
        "gear_slot3_quality": data.get("gear_slot3_quality", 0),
        "gear_slot3_level": data.get("gear_slot3_level", 0),
        "gear_slot3_mastery": data.get("gear_slot3_mastery", 0),
        "gear_slot4_quality": data.get("gear_slot4_quality", 0),
        "gear_slot4_level": data.get("gear_slot4_level", 0),
        "gear_slot4_mastery": data.get("gear_slot4_mastery", 0),
        # Mythic gear
        "mythic_gear_unlocked": data.get("mythic_gear_unlocked", False),
        "mythic_gear_quality": data.get("mythic_gear_quality", 0),
        "mythic_gear_level": data.get("mythic_gear_level", 0),
        "mythic_gear_mastery": data.get("mythic_gear_mastery", 0),
        "exclusive_gear_skill_level": data.get("exclusive_gear_skill_level", 0),
        # Metadata
        "owned": True,
        "updated_at": now,
    })

    # Preserve created_at if updating
    existing = get_hero(profile_id, hero_name)
    if existing:
        item["created_at"] = existing.get("created_at", now)
    else:
        item["created_at"] = now

    table.put_item(Item=item)
    return item


def update_hero(profile_id: str, hero_name: str, updates: dict) -> dict:
    """Update specific fields of a hero."""
    table = get_table("main")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Map API field names to DB field names
    field_mapping = {
        "ascension": "ascension_tier",
        "exploration_skill_1": "exploration_skill_1_level",
        "exploration_skill_2": "exploration_skill_2_level",
        "exploration_skill_3": "exploration_skill_3_level",
        "expedition_skill_1": "expedition_skill_1_level",
        "expedition_skill_2": "expedition_skill_2_level",
        "expedition_skill_3": "expedition_skill_3_level",
    }

    expr_parts = []
    attr_names = {}
    attr_values = {}

    for i, (key, value) in enumerate(updates.items()):
        if value is None:
            continue
        db_key = field_mapping.get(key, key)
        placeholder = f":v{i}"
        name_placeholder = f"#k{i}"
        expr_parts.append(f"{name_placeholder} = {placeholder}")
        attr_names[name_placeholder] = db_key
        attr_values[placeholder] = value

    if not expr_parts:
        return get_hero(profile_id, hero_name) or {}

    resp = table.update_item(
        Key={"PK": f"PROFILE#{profile_id}", "SK": f"HERO#{hero_name}"},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})


def delete_hero(profile_id: str, hero_name: str) -> None:
    """Delete a hero from a profile."""
    table = get_table("main")
    table.delete_item(
        Key={"PK": f"PROFILE#{profile_id}", "SK": f"HERO#{hero_name}"}
    )


def batch_update_heroes(profile_id: str, heroes: list[dict]) -> list[dict]:
    """Batch update multiple heroes using batch_writer for efficiency."""
    table = get_table("main")
    now = datetime.now(timezone.utc).isoformat()
    results = []

    # Pre-fetch existing heroes to preserve created_at timestamps
    existing = {h["SK"].replace("HERO#", ""): h for h in get_heroes(profile_id)}

    items = []
    for hero_data in heroes:
        hero_name = hero_data.pop("name", hero_data.pop("hero_name", None))
        if not hero_name:
            continue
        item = strip_none({
            "PK": f"PROFILE#{profile_id}",
            "SK": f"HERO#{hero_name}",
            "hero_name": hero_name,
            "profile_id": profile_id,
            "level": hero_data.get("level", 1),
            "stars": hero_data.get("stars", 0),
            "ascension_tier": hero_data.get("ascension", hero_data.get("ascension_tier", 0)),
            "exploration_skill_1_level": hero_data.get("exploration_skill_1", hero_data.get("exploration_skill_1_level", 1)),
            "exploration_skill_2_level": hero_data.get("exploration_skill_2", hero_data.get("exploration_skill_2_level", 1)),
            "exploration_skill_3_level": hero_data.get("exploration_skill_3", hero_data.get("exploration_skill_3_level", 1)),
            "expedition_skill_1_level": hero_data.get("expedition_skill_1", hero_data.get("expedition_skill_1_level", 1)),
            "expedition_skill_2_level": hero_data.get("expedition_skill_2", hero_data.get("expedition_skill_2_level", 1)),
            "expedition_skill_3_level": hero_data.get("expedition_skill_3", hero_data.get("expedition_skill_3_level", 1)),
            "gear_slot1_quality": hero_data.get("gear_slot1_quality", 0),
            "gear_slot1_level": hero_data.get("gear_slot1_level", 0),
            "gear_slot1_mastery": hero_data.get("gear_slot1_mastery", 0),
            "gear_slot2_quality": hero_data.get("gear_slot2_quality", 0),
            "gear_slot2_level": hero_data.get("gear_slot2_level", 0),
            "gear_slot2_mastery": hero_data.get("gear_slot2_mastery", 0),
            "gear_slot3_quality": hero_data.get("gear_slot3_quality", 0),
            "gear_slot3_level": hero_data.get("gear_slot3_level", 0),
            "gear_slot3_mastery": hero_data.get("gear_slot3_mastery", 0),
            "gear_slot4_quality": hero_data.get("gear_slot4_quality", 0),
            "gear_slot4_level": hero_data.get("gear_slot4_level", 0),
            "gear_slot4_mastery": hero_data.get("gear_slot4_mastery", 0),
            "mythic_gear_unlocked": hero_data.get("mythic_gear_unlocked", False),
            "mythic_gear_quality": hero_data.get("mythic_gear_quality", 0),
            "mythic_gear_level": hero_data.get("mythic_gear_level", 0),
            "mythic_gear_mastery": hero_data.get("mythic_gear_mastery", 0),
            "exclusive_gear_skill_level": hero_data.get("exclusive_gear_skill_level", 0),
            "owned": True,
            "updated_at": now,
            "created_at": existing[hero_name].get("created_at", now) if hero_name in existing else now,
        })
        items.append(item)

    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    return items


# --- Reference data ---

_heroes_cache: Optional[dict] = None


def load_heroes_json() -> dict:
    """Load heroes.json from data directory. Cached in memory."""
    global _heroes_cache
    if _heroes_cache is not None:
        return _heroes_cache

    data_dir = Config.DATA_DIR
    heroes_path = os.path.join(data_dir, "heroes.json")

    if os.path.exists(heroes_path):
        with open(heroes_path, encoding="utf-8") as f:
            data = json.load(f)
        _heroes_cache = {h["name"]: h for h in data.get("heroes", [])}
    else:
        _heroes_cache = {}

    return _heroes_cache


def get_all_heroes_reference() -> list:
    """Get all hero reference data from heroes.json."""
    heroes_map = load_heroes_json()
    return list(heroes_map.values())


def get_hero_reference(hero_name: str) -> Optional[dict]:
    """Get reference data for a specific hero from heroes.json."""
    heroes_map = load_heroes_json()
    return heroes_map.get(hero_name)


def get_reference_hero_from_db(hero_name: str) -> Optional[dict]:
    """Get hero reference from ReferenceTable."""
    table = get_table("reference")
    resp = table.get_item(Key={"PK": "HERO", "SK": hero_name})
    return resp.get("Item")


def get_all_reference_heroes_from_db() -> list:
    """Get all heroes from ReferenceTable."""
    table = get_table("reference")
    resp = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": "HERO"},
    )
    return resp.get("Items", [])
