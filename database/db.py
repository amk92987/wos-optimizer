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
