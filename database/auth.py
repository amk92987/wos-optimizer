"""
Authentication helpers for Bear's Den.
AWS-ready design using bcrypt for password hashing.
"""

import bcrypt
import streamlit as st
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from database.models import User


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


def create_user(db: Session, username: str, password: str, email: Optional[str] = None,
                role: str = 'user') -> Optional[User]:
    """Create a new user account."""
    # Check if username exists
    if db.query(User).filter(User.username == username).first():
        return None

    # Check if email exists (if provided)
    if email and db.query(User).filter(User.email == email).first():
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
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

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
    if not is_admin():
        st.error("Access denied. Admin privileges required.")
        st.stop()


# ============================================
# Initial Setup
# ============================================

def ensure_admin_exists(db: Session, default_password: str = "admin123"):
    """Ensure at least one admin user exists. Creates default admin if none."""
    admin = db.query(User).filter(User.role == 'admin').first()
    if not admin:
        create_user(db, username='admin', password=default_password, role='admin')
        return True
    return False
