"""
Authentication helpers for Bear's Den.
AWS-ready design using bcrypt for password hashing.
"""

import bcrypt
import streamlit as st
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from database.models import User, UserProfile, UserDailyLogin


import re

def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def normalize_email(email: str) -> str:
    """Normalize email to lowercase."""
    return email.strip().lower() if email else ""


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def create_user(db: Session, email: str, password: str,
                role: str = 'user', username: Optional[str] = None,
                skip_default_profile: bool = False) -> Optional[User]:
    """
    Create a new user account. Email is the primary identifier.
    Username is optional and defaults to email if not provided.
    Creates a default profile with {email_prefix}_city1 naming unless skip_default_profile=True.
    """
    # Normalize email
    email = normalize_email(email)

    # Email is required and must be valid
    if not is_valid_email(email):
        return None

    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        return None

    # Username defaults to email if not provided
    if not username:
        username = email

    # Check if username exists (for backwards compatibility)
    if db.query(User).filter(User.username == username).first():
        return None

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default profile for new users
    if not skip_default_profile:
        # Extract email prefix (part before @)
        email_prefix = email.split('@')[0]
        profile_name = f"{email_prefix}_city1"

        default_profile = UserProfile(
            user_id=user.id,
            name=profile_name,
            furnace_level=1,
            server_age_days=0,
            spending_profile="f2p",
            alliance_role="filler"
        )
        db.add(default_profile)
        db.commit()

    return user


def record_daily_login(db: Session, user_id: int):
    """Record a daily login for usage tracking. Only one record per user per day."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Check if already recorded today
    existing = db.query(UserDailyLogin).filter(
        UserDailyLogin.user_id == user_id,
        UserDailyLogin.login_date == today
    ).first()

    if not existing:
        login_record = UserDailyLogin(user_id=user_id, login_date=today)
        db.add(login_record)
        db.commit()


def get_days_active(db: Session, user_id: int, days: int = 7) -> int:
    """Get number of days user was active in the last N days."""
    from datetime import timedelta
    cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days-1)

    count = db.query(UserDailyLogin).filter(
        UserDailyLogin.user_id == user_id,
        UserDailyLogin.login_date >= cutoff
    ).count()

    return count


def authenticate_user(db: Session, email_or_username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email (primary) or username (legacy fallback).
    Email lookup is case-insensitive.
    """
    # Normalize input for email lookup
    normalized = normalize_email(email_or_username)

    # Try email first (primary method)
    user = db.query(User).filter(User.email == normalized).first()

    # Fall back to username for legacy accounts
    if not user:
        user = db.query(User).filter(User.username == email_or_username).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    # Update last login and record daily login
    user.last_login = datetime.utcnow()
    db.commit()
    record_daily_login(db, user.id)

    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by their username."""
    return db.query(User).filter(User.username == username).first()


def update_user_password(db: Session, user_id: int, new_password: str) -> bool:
    """Update a user's password."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    user.password_hash = hash_password(new_password)
    db.commit()
    return True


def update_user_role(db: Session, user_id: int, new_role: str) -> bool:
    """Update a user's role."""
    if new_role not in ('admin', 'user'):
        return False

    user = get_user_by_id(db, user_id)
    if not user:
        return False

    user.role = new_role
    db.commit()
    return True


def get_user_theme(db: Session, user_id: int) -> str:
    """Get user's theme preference."""
    user = get_user_by_id(db, user_id)
    if not user:
        return 'dark'
    return getattr(user, 'theme', 'dark') or 'dark'


def update_user_theme(db: Session, user_id: int, theme: str) -> bool:
    """Update user's theme preference."""
    if theme not in ('dark', 'light'):
        return False

    user = get_user_by_id(db, user_id)
    if not user:
        return False

    user.theme = theme
    db.commit()
    return True


def get_user_email(db: Session, user_id: int) -> Optional[str]:
    """Get user's email address."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    return user.email


def request_email_change(db: Session, user_id: int, new_email: str, password: str) -> tuple[bool, str]:
    """
    Request an email change. Sends verification code to new email.
    Requires current password for security.

    Returns (success, message) tuple.
    """
    import random
    from datetime import timedelta
    from database.models import PendingEmailChange
    from utils.email import send_verification_code

    user = get_user_by_id(db, user_id)
    if not user:
        return False, "User not found"

    # Verify current password
    if not verify_password(password, user.password_hash):
        return False, "Incorrect password"

    # Validate new email
    new_email = normalize_email(new_email)
    if not is_valid_email(new_email):
        return False, "Invalid email format"

    # Check if same as current
    if user.email and user.email.lower() == new_email:
        return False, "This is already your email"

    # Check if email is already in use
    existing = db.query(User).filter(User.email == new_email, User.id != user_id).first()
    if existing:
        return False, "Email already in use"

    # Generate 6-digit code
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # Delete any existing pending change for this user
    db.query(PendingEmailChange).filter(PendingEmailChange.user_id == user_id).delete()

    # Create new pending change (expires in 15 minutes)
    pending = PendingEmailChange(
        user_id=user_id,
        new_email=new_email,
        verification_code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(pending)
    db.commit()

    # Send verification email
    success, msg = send_verification_code(new_email, code)
    if not success:
        # Rollback pending change if email failed
        db.delete(pending)
        db.commit()
        return False, f"Failed to send verification email: {msg}"

    return True, "Verification code sent to your new email"


def verify_email_change(db: Session, user_id: int, code: str) -> tuple[bool, str]:
    """
    Verify email change code and complete the email update.

    Returns (success, message) tuple.
    """
    from database.models import PendingEmailChange

    user = get_user_by_id(db, user_id)
    if not user:
        return False, "User not found"

    # Get pending change
    pending = db.query(PendingEmailChange).filter(
        PendingEmailChange.user_id == user_id
    ).first()

    if not pending:
        return False, "No pending email change found"

    # Check expiration
    if datetime.utcnow() > pending.expires_at:
        db.delete(pending)
        db.commit()
        return False, "Verification code expired. Please request a new one."

    # Check attempts (max 3)
    if pending.attempts >= 3:
        db.delete(pending)
        db.commit()
        return False, "Too many failed attempts. Please request a new code."

    # Verify code
    if pending.verification_code != code.strip():
        pending.attempts += 1
        db.commit()
        remaining = 3 - pending.attempts
        if remaining > 0:
            return False, f"Incorrect code. {remaining} attempts remaining."
        else:
            db.delete(pending)
            db.commit()
            return False, "Too many failed attempts. Please request a new code."

    # Code is correct - update email and username
    new_email = pending.new_email
    user.email = new_email
    user.username = new_email  # Email = username

    # Delete pending change
    db.delete(pending)
    db.commit()

    return True, "Email updated successfully! Please use your new email to log in."


def get_pending_email_change(db: Session, user_id: int) -> Optional[str]:
    """
    Check if user has a pending email change.
    Returns the pending new email or None.
    """
    from database.models import PendingEmailChange

    pending = db.query(PendingEmailChange).filter(
        PendingEmailChange.user_id == user_id
    ).first()

    if pending and datetime.utcnow() <= pending.expires_at:
        return pending.new_email

    return None


def cancel_email_change(db: Session, user_id: int) -> bool:
    """Cancel a pending email change."""
    from database.models import PendingEmailChange

    deleted = db.query(PendingEmailChange).filter(
        PendingEmailChange.user_id == user_id
    ).delete()
    db.commit()
    return deleted > 0


# Legacy function - now just for admin use
def update_user_email(db: Session, user_id: int, new_email: Optional[str]) -> tuple[bool, str]:
    """
    Directly update a user's email (admin only, bypasses verification).
    Returns (success, message) tuple.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False, "User not found"

    # If clearing email (setting to None/empty)
    if not new_email or not new_email.strip():
        return False, "Email is required"

    new_email = normalize_email(new_email)

    # Validate email
    if not is_valid_email(new_email):
        return False, "Invalid email format"

    # Check if email is already in use by another user
    existing = db.query(User).filter(User.email == new_email, User.id != user_id).first()
    if existing:
        return False, "Email already in use"

    # Update both email and username
    user.email = new_email
    user.username = new_email
    db.commit()
    return True, "Email updated"


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user account."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True


def get_all_users(db: Session) -> list:
    """Get all users (for admin panel)."""
    return db.query(User).order_by(User.created_at.desc()).all()


# ============================================
# Session Management (Streamlit)
# ============================================

def init_session_state():
    """Initialize authentication session state."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    # Impersonation state
    if 'impersonating' not in st.session_state:
        st.session_state.impersonating = False
    if 'original_admin_id' not in st.session_state:
        st.session_state.original_admin_id = None
    if 'original_admin_username' not in st.session_state:
        st.session_state.original_admin_username = None


def login_user(user: User):
    """Set session state for logged in user."""
    st.session_state.authenticated = True
    st.session_state.user_id = user.id
    st.session_state.username = user.username
    st.session_state.user_role = user.role


def logout_user():
    """Clear session state for logout."""
    # If impersonating, return to admin
    if st.session_state.get('impersonating'):
        st.session_state.authenticated = True
        st.session_state.user_id = st.session_state.original_admin_id
        st.session_state.username = st.session_state.original_admin_username
        st.session_state.user_role = 'admin'
        st.session_state.impersonating = False
        st.session_state.original_admin_id = None
        st.session_state.original_admin_username = None
    else:
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.impersonating = False
        # Redirect to login page after logout
        st.query_params["page"] = "login"


def login_as_user(user: User):
    """Admin impersonation - login as another user while preserving admin session."""
    if not is_admin():
        return False

    # Store original admin info
    st.session_state.original_admin_id = st.session_state.user_id
    st.session_state.original_admin_username = st.session_state.username
    st.session_state.impersonating = True

    # Switch to target user
    st.session_state.user_id = user.id
    st.session_state.username = user.username
    st.session_state.user_role = user.role

    return True


def is_impersonating() -> bool:
    """Check if admin is currently impersonating a user."""
    return st.session_state.get('impersonating', False)


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    init_session_state()
    return st.session_state.authenticated


def is_admin() -> bool:
    """Check if current user is admin."""
    init_session_state()
    return st.session_state.authenticated and st.session_state.user_role == 'admin'


def get_current_user_id() -> Optional[int]:
    """Get current logged in user's ID."""
    init_session_state()
    return st.session_state.user_id if st.session_state.authenticated else None


def get_current_username() -> Optional[str]:
    """Get current logged in user's username."""
    init_session_state()
    return st.session_state.username if st.session_state.authenticated else None


def require_auth():
    """Decorator/check for pages that require authentication."""
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.stop()


def require_admin():
    """Decorator/check for pages that require admin role."""
    if not is_authenticated():
        # Not logged in - redirect to login page
        st.query_params["page"] = "login"
        st.rerun()
    elif not is_admin():
        # Logged in but not admin
        st.error("Access denied. Admin privileges required.")
        st.stop()


# ============================================
# Initial Setup
# ============================================

def ensure_admin_exists(db: Session, default_password: str = "admin123"):
    """Ensure at least one admin user exists. Creates default admin if none."""
    admin = db.query(User).filter(User.role == 'admin').first()
    if not admin:
        # Create admin with email (email = username)
        create_user(db, email='admin@bearsden.app', password=default_password, role='admin')
        return True
    return False
