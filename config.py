"""
Application configuration - loads from environment variables.
Supports .env files via python-dotenv.
"""

import os
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

# Environment: development, staging, production
ENV = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true" if ENV == "development" else "false").lower() == "true"

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Database
# Development: SQLite (default)
# Production: PostgreSQL via DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DB_PATH = PROJECT_ROOT / "wos.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# Detect database type for migrations
IS_POSTGRES = DATABASE_URL.startswith("postgresql")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Authentication
DEV_AUTO_LOGIN = os.getenv("DEV_AUTO_LOGIN", "true" if ENV == "development" else "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# AI Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Discord OAuth (for production)
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

# Admin
ADMIN_DISCORD_IDS = os.getenv("ADMIN_DISCORD_IDS", "").split(",") if os.getenv("ADMIN_DISCORD_IDS") else []
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "adam@randomchaoslabs.com")

# Feature flags (can be overridden by database FeatureFlag table)
DEFAULT_FEATURES = {
    "hero_recommendations": True,
    "inventory_ocr": False,
    "alliance_features": False,
    "beta_features": False,
    "maintenance_mode": False,
    "new_user_onboarding": True,
    "dark_theme_only": False,
    "analytics_tracking": True,
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
