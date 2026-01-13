"""
Export all data from SQLite database to JSON for migration.
Usage: python scripts/export_data.py --output data_export.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db, init_db
from database.models import (
    User, UserProfile, Hero, UserHero, UserChiefGear, UserChiefCharm,
    Item, UserInventory, UpgradeHistory, Feedback, AIConversation,
    FeatureFlag, Announcement, AuditLog, AISettings
)


def serialize_datetime(obj):
    """Convert datetime objects to ISO format strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def export_table(db, model, table_name):
    """Export all rows from a table."""
    rows = db.query(model).all()
    data = []
    for row in rows:
        row_dict = {}
        for column in row.__table__.columns:
            value = getattr(row, column.name)
            row_dict[column.name] = serialize_datetime(value)
        data.append(row_dict)
    print(f"  Exported {len(data)} rows from {table_name}")
    return data


def main():
    parser = argparse.ArgumentParser(description='Export database to JSON')
    parser.add_argument('--output', '-o', default='data_export.json',
                        help='Output file path')
    args = parser.parse_args()

    init_db()
    db = get_db()

    print("Starting database export...")

    export_data = {
        "exported_at": datetime.now().isoformat(),
        "version": "1.0",
        "tables": {}
    }

    # Export all tables
    tables = [
        (User, "users"),
        (UserProfile, "user_profiles"),
        (Hero, "heroes"),
        (UserHero, "user_heroes"),
        (UserChiefGear, "user_chief_gear"),
        (UserChiefCharm, "user_chief_charms"),
        (Item, "items"),
        (UserInventory, "user_inventory"),
        (UpgradeHistory, "upgrade_history"),
        (Feedback, "feedback"),
        (AIConversation, "ai_conversations"),
        (FeatureFlag, "feature_flags"),
        (Announcement, "announcements"),
        (AuditLog, "audit_logs"),
        (AISettings, "ai_settings"),
    ]

    for model, table_name in tables:
        try:
            export_data["tables"][table_name] = export_table(db, model, table_name)
        except Exception as e:
            print(f"  Warning: Could not export {table_name}: {e}")
            export_data["tables"][table_name] = []

    db.close()

    # Write to file
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"\nExport complete: {output_path}")
    print(f"Total tables: {len(export_data['tables'])}")

    # Summary
    total_rows = sum(len(rows) for rows in export_data['tables'].values())
    print(f"Total rows: {total_rows}")


if __name__ == "__main__":
    main()
