"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from .models import Base

# Database file location
DB_PATH = Path(__file__).parent.parent / "wos.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)

    # Run migrations for new columns on existing tables
    _run_migrations()


def _run_migrations():
    """Add new columns to existing tables (SQLite doesn't do this automatically)."""
    import sqlite3

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # List of migrations: (table, column, type, default)
    migrations = [
        ("user_profile", "state_number", "INTEGER", None),
        ("users", "ai_requests_today", "INTEGER", "0"),
        ("users", "ai_request_reset_date", "DATETIME", None),
        ("users", "last_ai_request", "DATETIME", None),
        ("ai_conversations", "is_favorite", "BOOLEAN", "0"),
        ("ai_conversations", "thread_id", "VARCHAR(36)", None),
        ("ai_conversations", "thread_title", "VARCHAR(100)", None),
    ]

    for table, column, col_type, default in migrations:
        # Check if column exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]

        if column not in columns:
            try:
                if default is not None:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}")
                else:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                conn.commit()
                print(f"Migration: Added {column} to {table}")
            except Exception as e:
                print(f"Migration warning: {e}")

    conn.close()


def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def get_or_create_profile(db: Session):
    """Get the user profile or create one if it doesn't exist."""
    from .models import UserProfile

    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
