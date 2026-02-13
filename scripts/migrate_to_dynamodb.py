#!/usr/bin/env python3
"""Migrate live SQLite data to DynamoDB for the serverless backend.

Reads exported JSON files from export_data/ and writes to DynamoDB.
Users get a generated UUID as their DynamoDB PK. When they log in via
the Cognito User Migration Trigger, the login handler re-keys their
records to the real Cognito sub.

Usage:
    python scripts/migrate_to_dynamodb.py [--dry-run] [--table TABLE_NAME]

Requires:
    - AWS credentials configured (same as SAM deploys)
    - export_data/ directory with JSON files from export_postgres.py
"""

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import boto3

EXPORT_DIR = Path(__file__).parent.parent / "export_data"
REGION = "us-east-1"
DEFAULT_TABLE = "wos-main-dev"


def load_json(filename):
    """Load a JSON file from the export directory."""
    path = EXPORT_DIR / filename
    if not path.exists():
        print(f"  WARNING: {filename} not found, skipping")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_ulid():
    """Generate a ULID-like sortable unique ID (matches profile_repo pattern)."""
    ts = int(time.time() * 1000)
    rand = uuid.uuid4().hex[:16]
    return f"{ts:012x}{rand}"


def to_dynamo(value):
    """Convert Python values to DynamoDB-compatible types."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, int) and not isinstance(value, bool):
        return Decimal(value)
    if isinstance(value, dict):
        return {k: to_dynamo(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_dynamo(v) for v in value]
    return value


def strip_none(item):
    """Remove None values (DynamoDB doesn't accept None)."""
    return {k: v for k, v in item.items() if v is not None}


def migrate(table_name, dry_run=False):
    """Run the full migration."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(table_name)

    # Verify table exists
    try:
        table.load()
        print(f"Connected to DynamoDB table: {table_name}")
        print(f"Item count: ~{table.item_count}")
    except Exception as e:
        print(f"ERROR: Cannot access table {table_name}: {e}")
        sys.exit(1)

    # Load all exported data
    users = load_json("users.json")
    profiles = load_json("profiles.json")
    heroes = load_json("user_heroes.json")
    chief_gear = load_json("chief_gear.json")
    chief_charms = load_json("chief_charms.json")

    if not users:
        print("No users to migrate!")
        sys.exit(1)

    # Build mappings: old SQLite ID -> new DynamoDB UUID
    user_id_map = {}  # old_user_id -> new_uuid
    profile_id_map = {}  # old_profile_id -> new_ulid

    # Generate IDs for users
    for user in users:
        new_id = f"legacy-{uuid.uuid4()}"
        user_id_map[user["id"]] = new_id

    # Generate ULID-like IDs for profiles
    for profile in profiles:
        new_id = generate_ulid()
        profile_id_map[profile["id"]] = new_id
        # Small delay to ensure ULIDs are unique (timestamp-based)
        time.sleep(0.002)

    print(f"\n=== Migration Plan ===")
    print(f"Users: {len(users)}")
    print(f"Profiles: {len(profiles)}")
    print(f"Heroes: {len(heroes)}")
    print(f"Chief Gear: {len(chief_gear)}")
    print(f"Chief Charms: {len(chief_charms)}")

    # Print user mapping
    print(f"\n--- User Mapping ---")
    for user in users:
        print(f"  {user['email']} (ID {user['id']}) -> {user_id_map[user['id']]}")

    # Print profile mapping
    print(f"\n--- Profile Mapping ---")
    for profile in profiles:
        user = next((u for u in users if u["id"] == profile["user_id"]), None)
        email = user["email"] if user else "?"
        print(f"  {profile['name']} (profile {profile['id']}, user {email}) -> {profile_id_map[profile['id']]}")

    if dry_run:
        print("\n[DRY RUN] Would write the following items:")

    items_written = 0

    # --- 1. Write USER METADATA records ---
    print(f"\n--- Migrating Users ---")
    for user in users:
        new_id = user_id_map[user["id"]]
        now = datetime.now(timezone.utc).isoformat()

        item = strip_none({
            "PK": f"USER#{new_id}",
            "SK": "METADATA",
            "entity_type": "USER",
            "user_id": new_id,
            "email": user["email"],
            "username": user["username"],
            "password_hash": user["password_hash"],
            "role": user["role"],
            "theme": user.get("theme", "dark"),
            "is_active": True,
            "is_verified": bool(user.get("is_verified", False)),
            "is_test_account": False,
            "ai_requests_today": 0,
            "ai_access_level": user.get("ai_access_level", "limited"),
            "created_at": user.get("created_at", now),
            "updated_at": now,
            "last_login": user.get("last_login"),
            "legacy_user_id": user["id"],  # Keep reference to old ID
        })
        item = strip_none(item)

        if dry_run:
            print(f"  USER: {user['email']} -> PK=USER#{new_id}")
        else:
            table.put_item(Item=to_dynamo(item))
            items_written += 1

        # Email uniqueness guard
        email_guard = {
            "PK": "UNIQUE#EMAIL",
            "SK": user["email"].lower(),
            "user_id": new_id,
        }
        if not dry_run:
            table.put_item(Item=email_guard)
            items_written += 1

        # Username uniqueness guard
        username_guard = {
            "PK": "UNIQUE#USERNAME",
            "SK": user["username"].lower(),
            "user_id": new_id,
        }
        if not dry_run:
            table.put_item(Item=username_guard)
            items_written += 1

    # --- 2. Write PROFILE records ---
    print(f"\n--- Migrating Profiles ---")
    for profile in profiles:
        old_user_id = profile["user_id"]
        if old_user_id not in user_id_map:
            print(f"  SKIP: Profile {profile['id']} - user {old_user_id} not migrated")
            continue

        new_user_id = user_id_map[old_user_id]
        new_profile_id = profile_id_map[profile["id"]]
        now = datetime.now(timezone.utc).isoformat()

        item = strip_none({
            "PK": f"USER#{new_user_id}",
            "SK": f"PROFILE#{new_profile_id}",
            "profile_id": new_profile_id,
            "user_id": new_user_id,
            "name": profile["name"],
            "is_default": bool(profile.get("is_default", False)),
            "state_number": profile.get("state_number"),
            "server_age_days": profile.get("server_age_days", 0),
            "furnace_level": profile.get("furnace_level", 1),
            "furnace_fc_level": profile.get("furnace_fc_level"),
            "spending_profile": profile.get("spending_profile", "f2p"),
            "priority_focus": profile.get("priority_focus", "balanced_growth"),
            "alliance_role": profile.get("alliance_role", "filler"),
            "priority_svs": profile.get("priority_svs", 5),
            "priority_rally": profile.get("priority_rally", 4),
            "priority_castle_battle": profile.get("priority_castle_battle", 4),
            "priority_exploration": profile.get("priority_exploration", 3),
            "priority_gathering": profile.get("priority_gathering", 2),
            "svs_wins": profile.get("svs_wins", 0),
            "svs_losses": profile.get("svs_losses", 0),
            "is_farm_account": bool(profile.get("is_farm_account", False)),
            "created_at": profile.get("created_at", now),
            "updated_at": now,
            "legacy_profile_id": profile["id"],
        })
        item = strip_none(item)

        if dry_run:
            print(f"  PROFILE: {profile['name']} -> PK=USER#{new_user_id} SK=PROFILE#{new_profile_id}")
        else:
            table.put_item(Item=to_dynamo(item))
            items_written += 1

    # --- 3. Write HERO records ---
    print(f"\n--- Migrating Heroes ---")
    hero_count = 0
    for hero in heroes:
        old_profile_id = hero["profile_id"]
        if old_profile_id not in profile_id_map:
            continue

        new_profile_id = profile_id_map[old_profile_id]
        hero_name = hero["hero_name"]
        now = datetime.now(timezone.utc).isoformat()

        item = strip_none({
            "PK": f"PROFILE#{new_profile_id}",
            "SK": f"HERO#{hero_name}",
            "hero_name": hero_name,
            "profile_id": new_profile_id,
            "level": hero.get("level", 1),
            "stars": hero.get("stars", 0),
            "ascension_tier": hero.get("ascension_tier", 0),
            "exploration_skill_1_level": hero.get("exploration_skill_1_level", 1),
            "exploration_skill_2_level": hero.get("exploration_skill_2_level", 1),
            "exploration_skill_3_level": hero.get("exploration_skill_3_level", 1),
            "expedition_skill_1_level": hero.get("expedition_skill_1_level", 1),
            "expedition_skill_2_level": hero.get("expedition_skill_2_level", 1),
            "expedition_skill_3_level": hero.get("expedition_skill_3_level", 1),
            "gear_slot1_quality": hero.get("gear_slot1_quality", 0),
            "gear_slot1_level": hero.get("gear_slot1_level", 0),
            "gear_slot1_mastery": hero.get("gear_slot1_mastery", 0),
            "gear_slot2_quality": hero.get("gear_slot2_quality", 0),
            "gear_slot2_level": hero.get("gear_slot2_level", 0),
            "gear_slot2_mastery": hero.get("gear_slot2_mastery", 0),
            "gear_slot3_quality": hero.get("gear_slot3_quality", 0),
            "gear_slot3_level": hero.get("gear_slot3_level", 0),
            "gear_slot3_mastery": hero.get("gear_slot3_mastery", 0),
            "gear_slot4_quality": hero.get("gear_slot4_quality", 0),
            "gear_slot4_level": hero.get("gear_slot4_level", 0),
            "gear_slot4_mastery": hero.get("gear_slot4_mastery", 0),
            "mythic_gear_unlocked": bool(hero.get("mythic_gear_unlocked", False)),
            "mythic_gear_quality": hero.get("mythic_gear_quality", 0),
            "mythic_gear_level": hero.get("mythic_gear_level", 0),
            "mythic_gear_mastery": hero.get("mythic_gear_mastery", 0),
            "exclusive_gear_skill_level": hero.get("exclusive_gear_skill_level", 0),
            "owned": True,
            "created_at": hero.get("created_at", now),
            "updated_at": now,
        })
        item = strip_none(item)

        if not dry_run:
            table.put_item(Item=to_dynamo(item))
            items_written += 1
        hero_count += 1

    print(f"  {hero_count} heroes migrated")

    # --- 4. Write CHIEF GEAR records ---
    print(f"\n--- Migrating Chief Gear ---")
    for gear in chief_gear:
        old_profile_id = gear["profile_id"]
        if old_profile_id not in profile_id_map:
            continue

        new_profile_id = profile_id_map[old_profile_id]
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "PK": f"PROFILE#{new_profile_id}",
            "SK": "CHIEFGEAR",
            "profile_id": new_profile_id,
            "helmet_quality": gear.get("helmet_quality", 1),
            "helmet_level": gear.get("helmet_level", 1),
            "armor_quality": gear.get("armor_quality", 1),
            "armor_level": gear.get("armor_level", 1),
            "gloves_quality": gear.get("gloves_quality", 1),
            "gloves_level": gear.get("gloves_level", 1),
            "boots_quality": gear.get("boots_quality", 1),
            "boots_level": gear.get("boots_level", 1),
            "ring_quality": gear.get("ring_quality", 1),
            "ring_level": gear.get("ring_level", 1),
            "amulet_quality": gear.get("amulet_quality", 1),
            "amulet_level": gear.get("amulet_level", 1),
            "updated_at": now,
        }

        if dry_run:
            print(f"  CHIEFGEAR: profile {old_profile_id} -> PROFILE#{new_profile_id}")
        else:
            table.put_item(Item=to_dynamo(item))
            items_written += 1

    # --- 5. Write CHIEF CHARM records ---
    print(f"\n--- Migrating Chief Charms ---")
    for charm in chief_charms:
        old_profile_id = charm["profile_id"]
        if old_profile_id not in profile_id_map:
            continue

        new_profile_id = profile_id_map[old_profile_id]
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "PK": f"PROFILE#{new_profile_id}",
            "SK": "CHIEFCHARM",
            "profile_id": new_profile_id,
            "cap_slot_1": charm.get("cap_slot_1", "1"),
            "cap_slot_2": charm.get("cap_slot_2", "1"),
            "cap_slot_3": charm.get("cap_slot_3", "1"),
            "watch_slot_1": charm.get("watch_slot_1", "1"),
            "watch_slot_2": charm.get("watch_slot_2", "1"),
            "watch_slot_3": charm.get("watch_slot_3", "1"),
            "coat_slot_1": charm.get("coat_slot_1", "1"),
            "coat_slot_2": charm.get("coat_slot_2", "1"),
            "coat_slot_3": charm.get("coat_slot_3", "1"),
            "pants_slot_1": charm.get("pants_slot_1", "1"),
            "pants_slot_2": charm.get("pants_slot_2", "1"),
            "pants_slot_3": charm.get("pants_slot_3", "1"),
            "belt_slot_1": charm.get("belt_slot_1", "1"),
            "belt_slot_2": charm.get("belt_slot_2", "1"),
            "belt_slot_3": charm.get("belt_slot_3", "1"),
            "weapon_slot_1": charm.get("weapon_slot_1", "1"),
            "weapon_slot_2": charm.get("weapon_slot_2", "1"),
            "weapon_slot_3": charm.get("weapon_slot_3", "1"),
            "updated_at": now,
        }

        if dry_run:
            print(f"  CHIEFCHARM: profile {old_profile_id} -> PROFILE#{new_profile_id}")
        else:
            table.put_item(Item=to_dynamo(item))
            items_written += 1

    print(f"\n=== Migration Complete ===")
    if dry_run:
        print("[DRY RUN] No items were written to DynamoDB")
    else:
        print(f"Total items written: {items_written}")

    # Save the ID mapping for reference
    mapping = {
        "users": {str(k): v for k, v in user_id_map.items()},
        "profiles": {str(k): v for k, v in profile_id_map.items()},
        "migrated_at": datetime.now(timezone.utc).isoformat(),
        "table": table_name,
    }
    mapping_path = EXPORT_DIR / "migration_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
    print(f"ID mapping saved to: {mapping_path}")


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to DynamoDB")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be written without writing")
    parser.add_argument("--table", default=DEFAULT_TABLE, help=f"DynamoDB table name (default: {DEFAULT_TABLE})")
    args = parser.parse_args()

    print(f"=== SQLite to DynamoDB Migration ===")
    print(f"Table: {args.table}")
    print(f"Dry run: {args.dry_run}")
    print(f"Export dir: {EXPORT_DIR}")
    print()

    migrate(args.table, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
