#!/usr/bin/env python3
"""Export all PostgreSQL tables to JSON files for migration to DynamoDB.

Run on the live server:
    cd ~/wos-app && python scripts/export_postgres.py

Creates export_data/ directory with one JSON file per table.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATABASE_URL, IS_POSTGRES
from database.models import (
    User, UserProfile, Hero, UserHero, Item, UserInventory,
    UserChiefGear, UserChiefCharm, UpgradeHistory,
    Feedback, AdminMetrics, AuditLog, Announcement, FeatureFlag,
    AIConversation, AISettings, UserNotification, MessageThread, Message,
    UserDailyLogin, ErrorLog, LineupTestRun, LineupTestResult,
)
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

OUTPUT_DIR = Path(__file__).parent.parent / "export_data"


def json_serial(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def row_to_dict(row):
    """Convert a SQLAlchemy model instance to a dict."""
    mapper = inspect(type(row))
    return {col.key: getattr(row, col.key) for col in mapper.column_attrs}


def export_table(session, model, filename):
    """Export a single table to JSON."""
    rows = session.query(model).all()
    data = [row_to_dict(r) for r in rows]

    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=json_serial, indent=2, ensure_ascii=False)

    print(f"  {filename}: {len(data)} rows")
    return len(data)


def main():
    if not IS_POSTGRES:
        print(f"WARNING: Not connected to PostgreSQL. DATABASE_URL={DATABASE_URL}")
        print("This script is meant to run on the live server with PostgreSQL.")
        resp = input("Continue anyway? (y/n): ")
        if resp.lower() != 'y':
            sys.exit(1)

    print(f"Connecting to: {DATABASE_URL[:30]}...")
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Exporting to: {OUTPUT_DIR}")
    print()

    total = 0
    tables = [
        # Core user data (CRITICAL - must migrate)
        (User, "users.json"),
        (UserProfile, "user_profiles.json"),
        (Hero, "heroes.json"),
        (UserHero, "user_heroes.json"),
        (UserChiefGear, "user_chief_gear.json"),
        (UserChiefCharm, "user_chief_charms.json"),
        (UserInventory, "user_inventory.json"),
        (Item, "items.json"),

        # AI data (valuable for training)
        (AIConversation, "ai_conversations.json"),
        (AISettings, "ai_settings.json"),

        # Admin data
        (Feedback, "feedback.json"),
        (Announcement, "announcements.json"),
        (FeatureFlag, "feature_flags.json"),
        (AuditLog, "audit_log.json"),
        (AdminMetrics, "admin_metrics.json"),

        # Messaging
        (MessageThread, "message_threads.json"),
        (Message, "messages.json"),
        (UserNotification, "user_notifications.json"),

        # Analytics
        (UpgradeHistory, "upgrade_history.json"),
        (UserDailyLogin, "user_daily_logins.json"),
        (ErrorLog, "error_logs.json"),

        # Lineup testing (can skip if too large)
        (LineupTestRun, "lineup_test_runs.json"),
        (LineupTestResult, "lineup_test_results.json"),
    ]

    for model, filename in tables:
        try:
            count = export_table(session, model, filename)
            total += count
        except Exception as e:
            print(f"  {filename}: ERROR - {e}")

    session.close()
    print(f"\nTotal: {total} rows exported to {OUTPUT_DIR}")
    print("Done! SCP these files to your local machine for migration.")


if __name__ == "__main__":
    main()
