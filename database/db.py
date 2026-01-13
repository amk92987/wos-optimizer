"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from pathlib import Path
import sys

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATABASE_URL, IS_POSTGRES, IS_SQLITE

from .models import Base

# Create engine with appropriate settings for database type
if IS_POSTGRES:
    # PostgreSQL: Use connection pooling
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True  # Verify connections before use
    )
else:
    # SQLite: No connection pooling needed
    engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)

    # Run migrations for new columns on existing tables
    _run_migrations()


def _run_migrations():
    """Add new columns to existing tables."""
    if IS_SQLITE:
        _run_sqlite_migrations()
    elif IS_POSTGRES:
        _run_postgres_migrations()


def _run_sqlite_migrations():
    """SQLite-specific migrations."""
    import sqlite3
    from config import PROJECT_ROOT

    db_path = PROJECT_ROOT / "wos.db"
    conn = sqlite3.connect(str(db_path))
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


def _run_postgres_migrations():
    """PostgreSQL-specific migrations using SQLAlchemy."""
    from sqlalchemy import text

    # List of migrations: (table, column, type, default)
    migrations = [
        ("user_profile", "state_number", "INTEGER", None),
        ("users", "ai_requests_today", "INTEGER", "0"),
        ("users", "ai_request_reset_date", "TIMESTAMP", None),
        ("users", "last_ai_request", "TIMESTAMP", None),
        ("ai_conversations", "is_favorite", "BOOLEAN", "FALSE"),
        ("ai_conversations", "thread_id", "VARCHAR(36)", None),
        ("ai_conversations", "thread_title", "VARCHAR(100)", None),
    ]

    with engine.connect() as conn:
        for table, column, col_type, default in migrations:
            try:
                # Check if column exists
                result = conn.execute(text(f"""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = '{table}' AND column_name = '{column}'
                """))
                if result.fetchone() is None:
                    # Column doesn't exist, add it
                    if default is not None:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}"))
                    else:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    conn.commit()
                    print(f"Migration: Added {column} to {table}")
            except Exception as e:
                print(f"Migration warning: {e}")


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
