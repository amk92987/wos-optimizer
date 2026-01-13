"""
Import data from JSON export into database (SQLite or PostgreSQL).
Usage: python scripts/import_data.py --input data_export.json

WARNING: This will ADD data to existing tables. For a clean import,
ensure the target database tables are empty first.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db, init_db, engine
from database.models import (
    User, UserProfile, Hero, UserHero, UserChiefGear, UserChiefCharm,
    Item, UserInventory, UpgradeHistory, Feedback, AIConversation,
    FeatureFlag, Announcement, AuditLog, AISettings
)


def parse_datetime(value):
    """Convert ISO format string back to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return value


def import_table(db, model, table_name, rows, skip_existing=True):
    """Import rows into a table."""
    imported = 0
    skipped = 0

    # Get datetime columns
    datetime_columns = [
        col.name for col in model.__table__.columns
        if 'DATETIME' in str(col.type).upper() or 'TIMESTAMP' in str(col.type).upper()
    ]

    for row_data in rows:
        # Convert datetime strings back to datetime objects
        for col in datetime_columns:
            if col in row_data:
                row_data[col] = parse_datetime(row_data[col])

        # Check if row already exists (by id)
        if 'id' in row_data and skip_existing:
            existing = db.query(model).filter(model.id == row_data['id']).first()
            if existing:
                skipped += 1
                continue

        try:
            obj = model(**row_data)
            db.merge(obj)  # Use merge to handle existing records
            imported += 1
        except Exception as e:
            print(f"    Warning: Could not import row {row_data.get('id', '?')}: {e}")
            skipped += 1

    db.commit()
    print(f"  {table_name}: Imported {imported}, Skipped {skipped}")
    return imported, skipped


def main():
    parser = argparse.ArgumentParser(description='Import database from JSON')
    parser.add_argument('--input', '-i', required=True,
                        help='Input JSON file path')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                        help='Skip rows that already exist (default: True)')
    parser.add_argument('--clear-first', action='store_true',
                        help='Clear tables before import (DANGEROUS)')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    print(f"Loading export file: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        export_data = json.load(f)

    print(f"Export date: {export_data.get('exported_at', 'Unknown')}")
    print(f"Version: {export_data.get('version', 'Unknown')}")

    init_db()
    db = get_db()

    if args.clear_first:
        print("\n⚠️  WARNING: --clear-first will DELETE ALL EXISTING DATA!")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("Aborted.")
            sys.exit(1)

        # Clear tables in reverse order (to handle foreign keys)
        tables_to_clear = [
            AuditLog, AIConversation, Feedback, UpgradeHistory,
            UserInventory, UserChiefCharm, UserChiefGear, UserHero,
            UserProfile, User, Item, Hero, FeatureFlag, Announcement, AISettings
        ]
        for model in tables_to_clear:
            try:
                db.query(model).delete()
                print(f"  Cleared {model.__tablename__}")
            except Exception as e:
                print(f"  Warning: Could not clear {model.__tablename__}: {e}")
        db.commit()

    print("\nStarting import...")

    # Import order matters due to foreign keys
    import_order = [
        (User, "users"),
        (Hero, "heroes"),
        (Item, "items"),
        (UserProfile, "user_profiles"),
        (UserHero, "user_heroes"),
        (UserChiefGear, "user_chief_gear"),
        (UserChiefCharm, "user_chief_charms"),
        (UserInventory, "user_inventory"),
        (UpgradeHistory, "upgrade_history"),
        (Feedback, "feedback"),
        (AIConversation, "ai_conversations"),
        (FeatureFlag, "feature_flags"),
        (Announcement, "announcements"),
        (AuditLog, "audit_logs"),
        (AISettings, "ai_settings"),
    ]

    total_imported = 0
    total_skipped = 0

    for model, table_name in import_order:
        if table_name in export_data.get("tables", {}):
            rows = export_data["tables"][table_name]
            if rows:
                imported, skipped = import_table(
                    db, model, table_name, rows, args.skip_existing
                )
                total_imported += imported
                total_skipped += skipped
        else:
            print(f"  {table_name}: No data in export")

    db.close()

    print(f"\nImport complete!")
    print(f"Total imported: {total_imported}")
    print(f"Total skipped: {total_skipped}")


if __name__ == "__main__":
    main()
