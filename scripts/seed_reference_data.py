"""Seed hero reference data into the DynamoDB ReferenceTable.

Reads data/heroes.json and writes each hero as an item in the
ReferenceTable with PK=HERO, SK=<hero_name>.

Usage:
    python scripts/seed_reference_data.py --region us-east-1 --stage dev
"""

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

import boto3

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Helpers (same as db.py conventions)
# ---------------------------------------------------------------------------

def _strip_none(d: dict) -> dict:
    """Remove keys with None or empty-string values."""
    cleaned = {}
    for k, v in d.items():
        if v is None or v == "":
            continue
        if isinstance(v, dict):
            nested = _strip_none(v)
            if nested:
                cleaned[k] = nested
        else:
            cleaned[k] = v
    return cleaned


def _to_decimal(value):
    """Convert Python numerics to Decimal for DynamoDB."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, int) and not isinstance(value, bool):
        return Decimal(value)
    if isinstance(value, dict):
        return {k: _to_decimal(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_decimal(v) for v in value]
    return value


def _prepare(item: dict) -> dict:
    return _to_decimal(_strip_none(item))


# ---------------------------------------------------------------------------
# Hero fields to include in the reference table
# ---------------------------------------------------------------------------

HERO_FIELDS = [
    "name", "generation", "hero_class", "rarity",
    # Tier ratings
    "tier_overall", "tier_expedition", "tier_exploration",
    # Image
    "image_filename",
    # Obtaining
    "how_to_obtain", "notes", "best_use",
    # Exploration skills (names + descriptions)
    "exploration_skill_1", "exploration_skill_1_desc",
    "exploration_skill_2", "exploration_skill_2_desc",
    "exploration_skill_3", "exploration_skill_3_desc",
    # Expedition skills (names + descriptions)
    "expedition_skill_1", "expedition_skill_1_desc",
    "expedition_skill_2", "expedition_skill_2_desc",
    "expedition_skill_3", "expedition_skill_3_desc",
    # Mythic gear info
    "mythic_gear",
]


def load_heroes_json() -> list[dict]:
    """Load heroes from data/heroes.json."""
    heroes_path = PROJECT_ROOT / "data" / "heroes.json"
    if not heroes_path.exists():
        print(f"ERROR: heroes.json not found at {heroes_path}")
        sys.exit(1)

    with open(heroes_path, encoding="utf-8") as f:
        data = json.load(f)

    heroes = data.get("heroes", [])
    if not heroes:
        print("ERROR: No heroes found in heroes.json")
        sys.exit(1)

    return heroes


def build_hero_item(hero: dict) -> dict:
    """Convert a hero dict from heroes.json into a DynamoDB item."""
    name = hero.get("name", "Unknown")

    item = {
        "PK": "HERO",
        "SK": name,
    }

    for field in HERO_FIELDS:
        value = hero.get(field)
        if value is not None:
            item[field] = value

    # Store mythic_gear as a nested map if present
    if hero.get("mythic_gear") and isinstance(hero["mythic_gear"], dict):
        item["mythic_gear"] = hero["mythic_gear"]
    elif hero.get("mythic_gear") and isinstance(hero["mythic_gear"], str):
        item["mythic_gear_name"] = hero["mythic_gear"]

    return item


def seed_heroes(table, heroes: list[dict], dry_run: bool = False) -> int:
    """Write hero items to the ReferenceTable."""
    items = []

    for hero in heroes:
        item = _prepare(build_hero_item(hero))
        items.append(item)

    if dry_run:
        print(f"\n[DRY RUN] Would write {len(items)} hero reference items")
        for item in items[:5]:
            print(f"  HERO: {item['SK']} (Gen {item.get('generation', '?')}, {item.get('hero_class', '?')})")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
        return len(items)

    # Use batch_writer for efficiency
    with table.batch_writer() as writer:
        for item in items:
            writer.put_item(Item=item)

    return len(items)


def main():
    parser = argparse.ArgumentParser(
        description="Seed hero reference data into the DynamoDB ReferenceTable."
    )
    parser.add_argument("--region", default="us-east-1",
                        help="AWS region (default: us-east-1)")
    parser.add_argument("--stage", choices=["dev", "live"], default="dev",
                        help="Target stage (determines table name)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview items without writing to DynamoDB")

    args = parser.parse_args()

    table_name = f"wos-reference-{args.stage}"

    print(f"\n{'='*60}")
    print(f"WoS Reference Data Seeder")
    print(f"{'='*60}")
    print(f"Table:   {table_name}")
    print(f"Region:  {args.region}")
    print(f"Dry run: {args.dry_run}")
    print(f"{'='*60}\n")

    # Load heroes
    heroes = load_heroes_json()
    print(f"Loaded {len(heroes)} heroes from data/heroes.json")

    # Summarize by generation
    gen_counts: dict[int, int] = {}
    for h in heroes:
        gen = h.get("generation", 0)
        gen_counts[gen] = gen_counts.get(gen, 0) + 1

    print("\nHeroes by generation:")
    for gen in sorted(gen_counts.keys()):
        print(f"  Gen {gen:2d}: {gen_counts[gen]} heroes")

    # Connect to DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name=args.region)
    table = dynamodb.Table(table_name)

    if not args.dry_run:
        try:
            table.table_status
        except Exception as e:
            print(f"\nERROR: Could not access table '{table_name}'.")
            print(f"  Ensure the table exists in region {args.region}.")
            print(f"  Error: {e}")
            sys.exit(1)

    # Seed heroes
    print(f"\nWriting heroes to {table_name}...")
    count = seed_heroes(table, heroes, dry_run=args.dry_run)

    print(f"\n{'='*60}")
    action = "would be seeded" if args.dry_run else "seeded"
    print(f"Done! {count} hero reference items {action}.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
