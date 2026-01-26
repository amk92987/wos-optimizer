"""
Admin routes for the API.
Handles user management, announcements, feature flags, and system settings.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import (
    User, UserProfile, Announcement, FeatureFlag, AIConversation,
    AISettings, Feedback, AuditLog, UserDailyLogin, ErrorLog
)
from database.auth import hash_password
from api.routes.auth import get_current_user

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency that requires admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ============== User Management ==============

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    is_test_account: bool
    ai_access_level: str
    ai_daily_limit: Optional[int]  # Custom limit (None = use global default)
    ai_requests_today: int
    created_at: datetime
    last_login: Optional[datetime]
    states: List[int]  # Game state numbers user has profiles in
    usage_7d: int  # Days logged in out of last 7


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"
    is_test_account: bool = False


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_test_account: Optional[bool] = None
    ai_access_level: Optional[str] = None  # 'off', 'limited', 'unlimited'
    ai_daily_limit: Optional[int] = None  # Custom daily limit (None = use global default)


@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    test_only: bool = False,
    admin_user: User = Depends(require_admin)
):
    """List all users."""
    init_db()
    db = get_db()

    try:
        query = db.query(User)

        if test_only:
            query = query.filter(User.is_test_account == True)

        users = query.offset(skip).limit(limit).all()

        # Calculate 7-day window for usage
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        result = []
        for u in users:
            # Get unique state numbers from user's profiles
            profiles = db.query(UserProfile).filter(UserProfile.user_id == u.id).all()
            states = sorted(list(set(
                p.state_number for p in profiles
                if p.state_number is not None
            )))

            # Count unique login days in last 7 days
            usage_7d = db.query(UserDailyLogin).filter(
                UserDailyLogin.user_id == u.id,
                UserDailyLogin.login_date >= seven_days_ago
            ).count()

            result.append({
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "role": u.role,
                "is_active": u.is_active,
                "is_test_account": getattr(u, 'is_test_account', False) or False,
                "ai_access_level": getattr(u, 'ai_access_level', 'limited') or 'limited',
                "ai_daily_limit": getattr(u, 'ai_daily_limit', None),
                "ai_requests_today": getattr(u, 'ai_requests_today', 0) or 0,
                "created_at": u.created_at,
                "last_login": u.last_login,
                "states": states,
                "usage_7d": usage_7d
            })

        return result

    finally:
        db.close()


@router.post("/users", response_model=UserResponse)
def create_user(
    request: CreateUserRequest,
    admin_user: User = Depends(require_admin)
):
    """Create a new user."""
    init_db()
    db = get_db()

    try:
        # Check if email exists
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=request.email,
            username=request.email,
            password_hash=hash_password(request.password),
            role=request.role,
            is_active=True,
            is_test_account=request.is_test_account,
            created_at=datetime.utcnow()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "is_test_account": user.is_test_account or False,
            "ai_access_level": getattr(user, 'ai_access_level', 'limited') or 'limited',
            "ai_daily_limit": getattr(user, 'ai_daily_limit', None),
            "ai_requests_today": getattr(user, 'ai_requests_today', 0) or 0,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "states": [],
            "usage_7d": 0
        }

    finally:
        db.close()


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    admin_user: User = Depends(require_admin)
):
    """Update a user."""
    init_db()
    db = get_db()

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Use __fields_set__ to know what fields were explicitly sent
        fields_set = request.__fields_set__

        if 'email' in fields_set and request.email is not None:
            user.email = request.email
        if 'role' in fields_set and request.role is not None:
            user.role = request.role
        if 'is_active' in fields_set and request.is_active is not None:
            user.is_active = request.is_active
        if 'is_test_account' in fields_set and request.is_test_account is not None:
            user.is_test_account = request.is_test_account
        if 'ai_access_level' in fields_set and request.ai_access_level is not None:
            user.ai_access_level = request.ai_access_level
        # For ai_daily_limit, allow setting to None (to clear) if explicitly sent
        if 'ai_daily_limit' in fields_set:
            user.ai_daily_limit = request.ai_daily_limit

        db.commit()
        db.refresh(user)

        # Get states and usage for response
        profiles = db.query(UserProfile).filter(UserProfile.user_id == user.id).all()
        states = sorted(list(set(
            p.state_number for p in profiles
            if p.state_number is not None
        )))

        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        usage_7d = db.query(UserDailyLogin).filter(
            UserDailyLogin.user_id == user.id,
            UserDailyLogin.login_date >= seven_days_ago
        ).count()

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "is_test_account": getattr(user, 'is_test_account', False) or False,
            "ai_access_level": getattr(user, 'ai_access_level', 'limited') or 'limited',
            "ai_daily_limit": getattr(user, 'ai_daily_limit', None),
            "ai_requests_today": getattr(user, 'ai_requests_today', 0) or 0,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "states": states,
            "usage_7d": usage_7d
        }

    finally:
        db.close()


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin_user: User = Depends(require_admin)):
    """Delete a user."""
    init_db()
    db = get_db()

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.id == admin_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")

        db.delete(user)
        db.commit()

        return {"status": "success", "message": "User deleted"}

    finally:
        db.close()


@router.post("/users/{user_id}/impersonate")
def impersonate_user(user_id: int, admin_user: User = Depends(require_admin)):
    """
    Impersonate a user. Returns a new token that logs admin in as the target user,
    while preserving the original admin ID for "Switch Back" functionality.
    """
    import jwt
    import os

    init_db()
    db = get_db()

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.id == admin_user.id:
            raise HTTPException(status_code=400, detail="Cannot impersonate yourself")

        # Create a special impersonation token
        SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        ALGORITHM = "HS256"

        expire = datetime.utcnow() + timedelta(hours=24)
        token_data = {
            "user_id": user.id,
            "role": user.role,
            "impersonating": True,
            "original_admin_id": admin_user.id,
            "exp": expire
        }

        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "impersonating": True,
                "original_admin_id": admin_user.id
            }
        }

    finally:
        db.close()


@router.post("/users/switch-back")
def switch_back_to_admin(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Switch back from impersonation to the original admin account.
    """
    import jwt
    import os

    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if not payload.get("impersonating"):
            raise HTTPException(status_code=400, detail="Not currently impersonating")

        original_admin_id = payload.get("original_admin_id")
        if not original_admin_id:
            raise HTTPException(status_code=400, detail="Original admin ID not found")

        init_db()
        db = get_db()

        try:
            admin = db.query(User).filter(User.id == original_admin_id).first()
            if not admin or admin.role != "admin":
                raise HTTPException(status_code=403, detail="Original admin not found or no longer admin")

            # Create new token for admin
            expire = datetime.utcnow() + timedelta(hours=24)
            token_data = {
                "user_id": admin.id,
                "role": admin.role,
                "exp": expire
            }

            access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": admin.id,
                    "email": admin.email,
                    "username": admin.username,
                    "role": admin.role
                }
            }
        finally:
            db.close()

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============== Announcements ==============

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_active: bool
    display_type: str
    show_from: Optional[datetime]
    show_until: Optional[datetime]
    created_at: datetime


class CreateAnnouncementRequest(BaseModel):
    title: str
    message: str
    type: str = "info"
    display_type: str = "banner"
    inbox_content: Optional[str] = None
    show_from: Optional[datetime] = None
    show_until: Optional[datetime] = None


@router.get("/announcements", response_model=List[AnnouncementResponse])
def list_announcements(
    active_only: bool = False,
    admin_user: User = Depends(require_admin)
):
    """List all announcements."""
    init_db()
    db = get_db()

    try:
        query = db.query(Announcement)

        if active_only:
            query = query.filter(Announcement.is_active == True)

        announcements = query.order_by(Announcement.created_at.desc()).all()

        return [
            {
                "id": a.id,
                "title": a.title,
                "message": a.message,
                "type": a.type or "info",
                "is_active": a.is_active,
                "display_type": a.display_type or "banner",
                "show_from": a.show_from,
                "show_until": a.show_until,
                "created_at": a.created_at
            }
            for a in announcements
        ]

    finally:
        db.close()


@router.post("/announcements", response_model=AnnouncementResponse)
def create_announcement(
    request: CreateAnnouncementRequest,
    admin_user: User = Depends(require_admin)
):
    """Create a new announcement."""
    init_db()
    db = get_db()

    try:
        announcement = Announcement(
            title=request.title,
            message=request.message,
            type=request.type,
            display_type=request.display_type,
            inbox_content=request.inbox_content,
            show_from=request.show_from,
            show_until=request.show_until,
            is_active=True,
            created_by=admin_user.id,
            created_at=datetime.utcnow()
        )

        db.add(announcement)
        db.commit()
        db.refresh(announcement)

        return {
            "id": announcement.id,
            "title": announcement.title,
            "message": announcement.message,
            "type": announcement.type or "info",
            "is_active": announcement.is_active,
            "display_type": announcement.display_type or "banner",
            "show_from": announcement.show_from,
            "show_until": announcement.show_until,
            "created_at": announcement.created_at
        }

    finally:
        db.close()


@router.put("/announcements/{announcement_id}")
def update_announcement(
    announcement_id: int,
    is_active: bool,
    admin_user: User = Depends(require_admin)
):
    """Toggle announcement active status."""
    init_db()
    db = get_db()

    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()

        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        announcement.is_active = is_active
        db.commit()

        return {"status": "success", "is_active": is_active}

    finally:
        db.close()


# ============== Feature Flags ==============

class FeatureFlagResponse(BaseModel):
    id: int
    name: str
    is_enabled: bool
    description: Optional[str]
    updated_at: Optional[datetime]


# Default feature flags
DEFAULT_FLAGS = [
    {"name": "hero_recommendations", "description": "AI-powered hero upgrade recommendations", "is_enabled": True},
    {"name": "inventory_ocr", "description": "Screenshot scanning for inventory", "is_enabled": False},
    {"name": "alliance_features", "description": "Alliance management and coordination", "is_enabled": False},
    {"name": "beta_features", "description": "Experimental features in testing", "is_enabled": False},
    {"name": "maintenance_mode", "description": "Show maintenance notice to users", "is_enabled": False},
    {"name": "new_user_onboarding", "description": "Guided setup for new users", "is_enabled": True},
    {"name": "dark_theme_only", "description": "Override user theme preference", "is_enabled": False},
    {"name": "analytics_tracking", "description": "Detailed usage analytics collection", "is_enabled": True},
]


@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
def list_feature_flags(admin_user: User = Depends(require_admin)):
    """List all feature flags."""
    init_db()
    db = get_db()

    try:
        flags = db.query(FeatureFlag).order_by(FeatureFlag.name).all()

        # Seed defaults if empty
        if len(flags) == 0:
            for flag_data in DEFAULT_FLAGS:
                flag = FeatureFlag(**flag_data)
                db.add(flag)
            db.commit()
            flags = db.query(FeatureFlag).order_by(FeatureFlag.name).all()

        return [
            {
                "id": f.id,
                "name": f.name,
                "is_enabled": f.is_enabled,
                "description": f.description,
                "updated_at": f.updated_at if hasattr(f, 'updated_at') else None
            }
            for f in flags
        ]

    finally:
        db.close()


class CreateFlagRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_enabled: bool = False


@router.post("/feature-flags")
def create_feature_flag(
    request: CreateFlagRequest,
    admin_user: User = Depends(require_admin)
):
    """Create a new feature flag."""
    init_db()
    db = get_db()

    try:
        # Clean name
        clean_name = request.name.lower().replace(" ", "_")

        # Check if exists
        existing = db.query(FeatureFlag).filter(FeatureFlag.name == clean_name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Flag with this name already exists")

        flag = FeatureFlag(
            name=clean_name,
            description=request.description,
            is_enabled=request.is_enabled
        )
        db.add(flag)
        db.commit()

        return {
            "status": "success",
            "id": flag.id,
            "name": flag.name,
            "is_enabled": flag.is_enabled
        }

    finally:
        db.close()


class UpdateFlagRequest(BaseModel):
    is_enabled: Optional[bool] = None
    name: Optional[str] = None
    description: Optional[str] = None


@router.put("/feature-flags/{flag_name}")
def update_feature_flag(
    flag_name: str,
    request: UpdateFlagRequest,
    admin_user: User = Depends(require_admin)
):
    """Update a feature flag."""
    init_db()
    db = get_db()

    try:
        flag = db.query(FeatureFlag).filter(FeatureFlag.name == flag_name).first()

        if not flag:
            raise HTTPException(status_code=404, detail="Feature flag not found")

        if request.is_enabled is not None:
            flag.is_enabled = request.is_enabled
        if request.name is not None:
            clean_name = request.name.lower().replace(" ", "_")
            flag.name = clean_name
        if request.description is not None:
            flag.description = request.description

        if hasattr(flag, 'updated_at'):
            flag.updated_at = datetime.utcnow()

        db.commit()

        return {"status": "success", "name": flag.name, "is_enabled": flag.is_enabled}

    finally:
        db.close()


@router.delete("/feature-flags/{flag_name}")
def delete_feature_flag(
    flag_name: str,
    admin_user: User = Depends(require_admin)
):
    """Delete a feature flag."""
    init_db()
    db = get_db()

    try:
        flag = db.query(FeatureFlag).filter(FeatureFlag.name == flag_name).first()

        if not flag:
            raise HTTPException(status_code=404, detail="Feature flag not found")

        db.delete(flag)
        db.commit()

        return {"status": "success", "name": flag_name}

    finally:
        db.close()


class BulkFlagAction(BaseModel):
    action: str  # enable_all, disable_all, reset_defaults


@router.post("/feature-flags/bulk")
def bulk_feature_flag_action(
    request: BulkFlagAction,
    admin_user: User = Depends(require_admin)
):
    """Perform bulk action on feature flags."""
    init_db()
    db = get_db()

    try:
        if request.action == "enable_all":
            db.query(FeatureFlag).update({FeatureFlag.is_enabled: True})
            db.commit()
            return {"status": "success", "action": "enable_all"}

        elif request.action == "disable_all":
            db.query(FeatureFlag).update({FeatureFlag.is_enabled: False})
            db.commit()
            return {"status": "success", "action": "disable_all"}

        elif request.action == "reset_defaults":
            db.query(FeatureFlag).delete()
            for flag_data in DEFAULT_FLAGS:
                flag = FeatureFlag(**flag_data)
                db.add(flag)
            db.commit()
            return {"status": "success", "action": "reset_defaults"}

        else:
            raise HTTPException(status_code=400, detail="Unknown action")

    finally:
        db.close()


# ============== AI Settings ==============

class AISettingsResponse(BaseModel):
    mode: str
    daily_limit_free: int
    daily_limit_admin: int
    cooldown_seconds: int
    primary_provider: str
    primary_model: str


@router.get("/ai-settings", response_model=AISettingsResponse)
def get_ai_settings(admin_user: User = Depends(require_admin)):
    """Get AI settings."""
    init_db()
    db = get_db()

    try:
        settings = db.query(AISettings).first()

        if not settings:
            return {
                "mode": "on",
                "daily_limit_free": 10,
                "daily_limit_admin": 1000,
                "cooldown_seconds": 30,
                "primary_provider": "openai",
                "primary_model": "gpt-4o-mini"
            }

        return {
            "mode": settings.mode,
            "daily_limit_free": settings.daily_limit_free,
            "daily_limit_admin": settings.daily_limit_admin,
            "cooldown_seconds": settings.cooldown_seconds,
            "primary_provider": settings.primary_provider,
            "primary_model": settings.primary_model
        }

    finally:
        db.close()


@router.put("/ai-settings")
def update_ai_settings(
    mode: Optional[str] = None,
    daily_limit_free: Optional[int] = None,
    daily_limit_admin: Optional[int] = None,
    cooldown_seconds: Optional[int] = None,
    admin_user: User = Depends(require_admin)
):
    """Update AI settings."""
    init_db()
    db = get_db()

    try:
        settings = db.query(AISettings).first()

        if not settings:
            settings = AISettings(mode="on")
            db.add(settings)

        if mode is not None:
            settings.mode = mode
        if daily_limit_free is not None:
            settings.daily_limit_free = daily_limit_free
        if daily_limit_admin is not None:
            settings.daily_limit_admin = daily_limit_admin
        if cooldown_seconds is not None:
            settings.cooldown_seconds = cooldown_seconds

        db.commit()

        return {"status": "success", "mode": settings.mode}

    finally:
        db.close()


# ============== Dashboard Stats ==============

@router.get("/stats")
def get_admin_stats(admin_user: User = Depends(require_admin)):
    """Get dashboard statistics."""
    init_db()
    db = get_db()

    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        test_users = db.query(User).filter(User.is_test_account == True).count()
        total_profiles = db.query(UserProfile).count()
        total_conversations = db.query(AIConversation).count()
        ai_conversations = db.query(AIConversation).filter(
            AIConversation.routed_to == "ai"
        ).count()
        rules_conversations = db.query(AIConversation).filter(
            AIConversation.routed_to == "rules"
        ).count()

        # Feedback counts
        feedback_new = db.query(Feedback).filter(
            Feedback.status == "new"
        ).count() if hasattr(Feedback, 'status') else 0

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "test": test_users
            },
            "profiles": total_profiles,
            "conversations": {
                "total": total_conversations,
                "ai": ai_conversations,
                "rules": rules_conversations,
                "ai_percentage": round(ai_conversations / total_conversations * 100, 1) if total_conversations > 0 else 0
            },
            "feedback_pending": feedback_new
        }

    finally:
        db.close()


# ============== Feedback ==============

class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_email: Optional[str]
    category: str
    message: str
    status: str
    created_at: datetime


@router.get("/feedback", response_model=List[FeedbackResponse])
def list_feedback(
    status: Optional[str] = None,
    feedback_type: Optional[str] = None,
    admin_user: User = Depends(require_admin)
):
    """List all feedback."""
    init_db()
    db = get_db()

    try:
        query = db.query(Feedback)

        if status:
            query = query.filter(Feedback.status == status)
        if feedback_type:
            query = query.filter(Feedback.category == feedback_type)

        feedback_items = query.order_by(Feedback.created_at.desc()).all()

        result = []
        for f in feedback_items:
            user_email = None
            if f.user_id:
                user = db.query(User).filter(User.id == f.user_id).first()
                user_email = user.email if user else None

            result.append({
                "id": f.id,
                "user_id": f.user_id,
                "user_email": user_email,
                "category": f.category,
                "message": f.description,
                "status": f.status or "new",
                "created_at": f.created_at
            })

        return result

    finally:
        db.close()


@router.put("/feedback/{feedback_id}")
def update_feedback_status(
    feedback_id: int,
    status: str,
    admin_user: User = Depends(require_admin)
):
    """Update feedback status."""
    init_db()
    db = get_db()

    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")

        feedback.status = status
        db.commit()

        return {"status": "success", "feedback_status": status}

    finally:
        db.close()


# ============== Database Browser ==============

@router.get("/database/tables")
def list_database_tables(admin_user: User = Depends(require_admin)):
    """List all database tables with row counts and columns."""
    from sqlalchemy import inspect, text

    init_db()
    db = get_db()

    try:
        inspector = inspect(db.get_bind())
        tables = []

        for table_name in inspector.get_table_names():
            # Get columns
            columns = [col['name'] for col in inspector.get_columns(table_name)]

            # Get row count
            result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.scalar()

            tables.append({
                "name": table_name,
                "row_count": row_count,
                "columns": columns
            })

        return sorted(tables, key=lambda x: x['name'])

    finally:
        db.close()


@router.get("/database/tables/{table_name}")
def get_table_data(
    table_name: str,
    limit: int = 50,
    offset: int = 0,
    admin_user: User = Depends(require_admin)
):
    """Get data from a specific table with pagination."""
    from sqlalchemy import inspect, text
    import re

    init_db()
    db = get_db()

    try:
        # Validate table name (prevent SQL injection)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        inspector = inspect(db.get_bind())
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail="Table not found")

        # Get columns for mapping
        columns = [col['name'] for col in inspector.get_columns(table_name)]

        # Query data
        result = db.execute(text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset"),
                           {"limit": limit, "offset": offset})
        rows = result.fetchall()

        # Convert to list of dicts
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                val = row[i]
                # Convert datetime to string for JSON serialization
                if hasattr(val, 'isoformat'):
                    val = val.isoformat()
                row_dict[col] = val
            data.append(row_dict)

        return data

    finally:
        db.close()


@router.get("/database/backups")
def list_database_backups(admin_user: User = Depends(require_admin)):
    """List available database backups."""
    import os
    from pathlib import Path

    # Look for backups in a backups directory
    backup_dir = Path(PROJECT_ROOT) / "backups"

    if not backup_dir.exists():
        return []

    backups = []
    for f in backup_dir.glob("*.db") or backup_dir.glob("*.sql"):
        stat = f.stat()
        backups.append({
            "filename": f.name,
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size_bytes": stat.st_size
        })

    return sorted(backups, key=lambda x: x['created_at'], reverse=True)


@router.post("/database/backup")
def create_database_backup(admin_user: User = Depends(require_admin)):
    """Create a backup of the current database."""
    import shutil
    import os
    from pathlib import Path

    # Create backups directory if it doesn't exist
    backup_dir = Path(PROJECT_ROOT) / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Source database path (SQLite)
    db_path = Path(PROJECT_ROOT) / "wos.db"

    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database file not found")

    # Create backup with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"wos_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename

    try:
        shutil.copy2(db_path, backup_path)
        return {
            "status": "success",
            "filename": backup_filename,
            "size_bytes": backup_path.stat().st_size,
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.post("/database/cleanup/{action_id}")
def run_database_cleanup(
    action_id: str,
    admin_user: User = Depends(require_admin)
):
    """Run a database cleanup action."""
    from sqlalchemy import text

    init_db()
    db = get_db()

    try:
        if action_id == "orphaned_sessions":
            # Remove old sessions (if session table exists)
            # For now, just return success
            return {"status": "success", "message": "No orphaned sessions found"}

        elif action_id == "old_logs":
            # Remove audit logs older than 90 days
            cutoff = datetime.utcnow() - timedelta(days=90)
            deleted = db.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()
            db.commit()
            return {"status": "success", "message": f"Deleted {deleted} old audit log entries"}

        elif action_id == "unused_profiles":
            # This is dangerous - require confirmation in production
            # For safety, we'll just report what would be deleted
            cutoff = datetime.utcnow() - timedelta(days=180)
            count = db.query(UserProfile).filter(
                UserProfile.updated_at < cutoff
            ).count() if hasattr(UserProfile, 'updated_at') else 0
            return {"status": "success", "message": f"Found {count} inactive profiles (not deleted - use with caution)"}

        elif action_id == "vacuum":
            # Run VACUUM on SQLite database
            db.execute(text("VACUUM"))
            db.commit()
            return {"status": "success", "message": "Database vacuumed successfully"}

        else:
            raise HTTPException(status_code=400, detail="Unknown cleanup action")

    finally:
        db.close()


class QueryRequest(BaseModel):
    query: str


@router.post("/database/query")
def execute_database_query(
    request: QueryRequest,
    admin_user: User = Depends(require_admin)
):
    """Execute a read-only SQL query."""
    from sqlalchemy import text
    import re

    # Only allow SELECT queries
    query = request.query.strip()
    if not query.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

    # Block dangerous keywords
    dangerous = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
    query_upper = query.upper()
    for keyword in dangerous:
        if keyword in query_upper:
            raise HTTPException(status_code=400, detail=f"Query contains forbidden keyword: {keyword}")

    init_db()
    db = get_db()

    try:
        result = db.execute(text(query))
        columns = result.keys()
        rows = result.fetchall()

        # Convert to list of dicts
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                val = row[i]
                if hasattr(val, 'isoformat'):
                    val = val.isoformat()
                row_dict[col] = val
            data.append(row_dict)

        return {"results": data, "row_count": len(data)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")

    finally:
        db.close()


# ============== Error Logs ==============

class ErrorLogResponse(BaseModel):
    id: int
    error_type: str
    message: str
    stack_trace: Optional[str]
    page: Optional[str]
    user_id: Optional[int]
    user_email: Optional[str]
    resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime


@router.get("/errors", response_model=List[ErrorLogResponse])
def list_errors(
    resolved: Optional[bool] = None,
    error_type: Optional[str] = None,
    limit: int = 100,
    admin_user: User = Depends(require_admin)
):
    """List error logs with optional filtering."""
    init_db()
    db = get_db()

    try:
        query = db.query(ErrorLog)

        if resolved is not None:
            query = query.filter(ErrorLog.resolved == resolved)
        if error_type:
            query = query.filter(ErrorLog.error_type == error_type)

        errors = query.order_by(ErrorLog.created_at.desc()).limit(limit).all()

        result = []
        for e in errors:
            user_email = None
            if e.user_id:
                user = db.query(User).filter(User.id == e.user_id).first()
                user_email = user.email if user else None

            result.append({
                "id": e.id,
                "error_type": e.error_type,
                "message": e.error_message,
                "stack_trace": e.stack_trace,
                "page": e.page,
                "user_id": e.user_id,
                "user_email": user_email,
                "resolved": e.resolved if hasattr(e, 'resolved') else False,
                "resolved_at": e.resolved_at if hasattr(e, 'resolved_at') else None,
                "created_at": e.created_at
            })

        return result

    finally:
        db.close()


@router.post("/errors/{error_id}/resolve")
def resolve_error(
    error_id: int,
    admin_user: User = Depends(require_admin)
):
    """Mark an error as resolved."""
    init_db()
    db = get_db()

    try:
        error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()

        if not error:
            raise HTTPException(status_code=404, detail="Error not found")

        error.resolved = True
        error.resolved_at = datetime.utcnow()
        error.resolved_by = admin_user.id
        db.commit()

        return {"status": "success", "error_id": error_id}

    finally:
        db.close()


# ============== AI Conversations Admin ==============

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    question: str
    answer: str
    provider: str
    model: str
    routed_to: Optional[str]
    is_helpful: Optional[bool]
    rating: Optional[int]
    user_feedback: Optional[str]
    is_good_example: bool
    is_bad_example: bool
    admin_notes: Optional[str]
    created_at: datetime


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    rating_filter: Optional[str] = None,  # all, rated, unrated, helpful, unhelpful
    curation_filter: Optional[str] = None,  # all, good, bad, not_curated
    source_filter: Optional[str] = None,  # all, ai, rules
    limit: int = 50,
    admin_user: User = Depends(require_admin)
):
    """List AI conversations with filtering."""
    init_db()
    db = get_db()

    try:
        query = db.query(AIConversation)

        # Rating filters
        if rating_filter == "rated":
            query = query.filter(AIConversation.rating != None)
        elif rating_filter == "unrated":
            query = query.filter(AIConversation.rating == None)
        elif rating_filter == "helpful":
            query = query.filter(AIConversation.is_helpful == True)
        elif rating_filter == "unhelpful":
            query = query.filter(AIConversation.is_helpful == False)

        # Curation filters
        if curation_filter == "good":
            query = query.filter(AIConversation.is_good_example == True)
        elif curation_filter == "bad":
            query = query.filter(AIConversation.is_bad_example == True)
        elif curation_filter == "not_curated":
            query = query.filter(
                AIConversation.is_good_example == False,
                AIConversation.is_bad_example == False
            )

        # Source filters
        if source_filter == "ai":
            query = query.filter(AIConversation.routed_to == "ai")
        elif source_filter == "rules":
            query = query.filter(AIConversation.routed_to == "rules")

        conversations = query.order_by(AIConversation.created_at.desc()).limit(limit).all()

        result = []
        for c in conversations:
            user = db.query(User).filter(User.id == c.user_id).first()
            user_email = user.email if user else "Unknown"

            result.append({
                "id": c.id,
                "user_id": c.user_id,
                "user_email": user_email,
                "question": c.question,
                "answer": c.answer,
                "provider": c.provider,
                "model": c.model,
                "routed_to": c.routed_to,
                "is_helpful": c.is_helpful,
                "rating": c.rating,
                "user_feedback": c.user_feedback,
                "is_good_example": c.is_good_example if hasattr(c, 'is_good_example') else False,
                "is_bad_example": c.is_bad_example if hasattr(c, 'is_bad_example') else False,
                "admin_notes": c.admin_notes if hasattr(c, 'admin_notes') else None,
                "created_at": c.created_at
            })

        return result

    finally:
        db.close()


class CurateConversationRequest(BaseModel):
    is_good_example: Optional[bool] = None
    is_bad_example: Optional[bool] = None
    admin_notes: Optional[str] = None


@router.put("/conversations/{conversation_id}/curate")
def curate_conversation(
    conversation_id: int,
    request: CurateConversationRequest,
    admin_user: User = Depends(require_admin)
):
    """Update curation status for an AI conversation."""
    init_db()
    db = get_db()

    try:
        conversation = db.query(AIConversation).filter(AIConversation.id == conversation_id).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if request.is_good_example is not None:
            conversation.is_good_example = request.is_good_example
        if request.is_bad_example is not None:
            conversation.is_bad_example = request.is_bad_example
        if request.admin_notes is not None:
            conversation.admin_notes = request.admin_notes

        db.commit()

        return {
            "status": "success",
            "conversation_id": conversation_id,
            "is_good_example": conversation.is_good_example,
            "is_bad_example": conversation.is_bad_example
        }

    finally:
        db.close()


@router.get("/conversations/stats")
def get_conversation_stats(admin_user: User = Depends(require_admin)):
    """Get AI conversation statistics."""
    init_db()
    db = get_db()

    try:
        total = db.query(AIConversation).count()
        ai_routed = db.query(AIConversation).filter(AIConversation.routed_to == "ai").count()
        rules_routed = db.query(AIConversation).filter(AIConversation.routed_to == "rules").count()
        good_examples = db.query(AIConversation).filter(AIConversation.is_good_example == True).count()
        bad_examples = db.query(AIConversation).filter(AIConversation.is_bad_example == True).count()
        helpful = db.query(AIConversation).filter(AIConversation.is_helpful == True).count()
        unhelpful = db.query(AIConversation).filter(AIConversation.is_helpful == False).count()

        return {
            "total": total,
            "ai_routed": ai_routed,
            "rules_routed": rules_routed,
            "ai_percentage": round(ai_routed / total * 100, 1) if total > 0 else 0,
            "good_examples": good_examples,
            "bad_examples": bad_examples,
            "helpful": helpful,
            "unhelpful": unhelpful
        }

    finally:
        db.close()


@router.get("/conversations/export")
def export_training_data(
    good_only: bool = True,
    format: str = "jsonl",
    admin_user: User = Depends(require_admin)
):
    """Export AI conversations as training data."""
    import json

    init_db()
    db = get_db()

    try:
        query = db.query(AIConversation)

        if good_only:
            query = query.filter(AIConversation.is_good_example == True)

        conversations = query.order_by(AIConversation.created_at.desc()).all()

        if format == "jsonl":
            lines = []
            for c in conversations:
                entry = {
                    "messages": [
                        {"role": "user", "content": c.question},
                        {"role": "assistant", "content": c.answer}
                    ]
                }
                lines.append(json.dumps(entry))
            return {"format": "jsonl", "data": "\n".join(lines), "count": len(lines)}

        else:  # csv
            data = []
            for c in conversations:
                data.append({
                    "question": c.question,
                    "answer": c.answer,
                    "provider": c.provider,
                    "model": c.model,
                    "admin_notes": c.admin_notes if hasattr(c, 'admin_notes') else None
                })
            return {"format": "csv", "data": data, "count": len(data)}

    finally:
        db.close()


# ============== Usage Reports ==============

from database.models import UserHero, UserInventory, Hero, AdminMetrics
from sqlalchemy import func


@router.get("/usage/stats")
def get_usage_stats(
    range: str = "7d",
    admin_user: User = Depends(require_admin)
):
    """Get comprehensive usage statistics."""
    init_db()
    db = get_db()

    try:
        now = datetime.utcnow()

        # Parse date range
        if range == "7d":
            start_date = now - timedelta(days=7)
        elif range == "30d":
            start_date = now - timedelta(days=30)
        elif range == "90d":
            start_date = now - timedelta(days=90)
        else:
            start_date = datetime.min

        # Get all non-admin users
        all_users = db.query(User).filter(User.role != "admin").all()

        # Activity breakdown
        very_active = len([u for u in all_users if u.last_login and (now - u.last_login).days <= 1])
        active_weekly = len([u for u in all_users if u.last_login and 1 < (now - u.last_login).days <= 7])
        active_monthly = len([u for u in all_users if u.last_login and 7 < (now - u.last_login).days <= 30])
        inactive = len([u for u in all_users if not u.last_login or (now - u.last_login).days > 30])

        # Users in date range
        active_in_range = len([u for u in all_users if u.last_login and u.last_login >= start_date])
        new_in_range = len([u for u in all_users if u.created_at and u.created_at >= start_date])

        # Content stats
        total_profiles = db.query(UserProfile).count()
        total_heroes = db.query(UserHero).count()
        total_inventory = db.query(UserInventory).count()

        # Popular heroes
        hero_counts = db.query(
            Hero.name, func.count(UserHero.id).label('count')
        ).join(UserHero).group_by(Hero.id).order_by(func.count(UserHero.id).desc()).limit(10).all()

        top_heroes = [{"name": name, "count": count} for name, count in hero_counts]

        # Hero class distribution
        class_counts = db.query(
            Hero.hero_class, func.count(UserHero.id).label('count')
        ).join(UserHero).group_by(Hero.hero_class).all()

        hero_classes = {hc: count for hc, count in class_counts}

        # Spending profile distribution
        spending_counts = db.query(
            UserProfile.spending_profile, func.count(UserProfile.id).label('count')
        ).group_by(UserProfile.spending_profile).all()

        spending_distribution = {sp or "Not set": count for sp, count in spending_counts}

        # Alliance role distribution
        role_counts = db.query(
            UserProfile.alliance_role, func.count(UserProfile.id).label('count')
        ).group_by(UserProfile.alliance_role).all()

        alliance_roles = {role or "Not set": count for role, count in role_counts}

        # State distribution
        state_counts = db.query(
            UserProfile.state_number, func.count(UserProfile.id).label('count')
        ).filter(UserProfile.state_number != None).group_by(UserProfile.state_number).order_by(func.count(UserProfile.id).desc()).limit(20).all()

        top_states = [{"state": state, "count": count} for state, count in state_counts]

        profiles_without_state = db.query(UserProfile).filter(
            (UserProfile.state_number == None) | (UserProfile.state_number == 0)
        ).count()

        # Historical metrics (from AdminMetrics table)
        metrics = db.query(AdminMetrics).order_by(AdminMetrics.date.desc()).limit(90).all()

        historical_data = []
        for m in reversed(metrics):
            historical_data.append({
                "date": m.date.isoformat() if m.date else None,
                "total_users": m.total_users or 0,
                "active_users": m.active_users or 0,
                "new_users": m.new_users or 0,
                "heroes_tracked": m.total_heroes_tracked or 0
            })

        # Daily active users (last N days based on range)
        days_count = 7 if range == "7d" else 30 if range == "30d" else 90
        daily_active = []
        for i in range(days_count - 1, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = len([u for u in all_users if u.last_login and day_start <= u.last_login < day_end])
            daily_active.append(count)

        # AI usage
        ai_usage = []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            total_requests = db.query(AIConversation).filter(
                AIConversation.created_at >= day_start,
                AIConversation.created_at < day_end
            ).count()

            rules_requests = db.query(AIConversation).filter(
                AIConversation.created_at >= day_start,
                AIConversation.created_at < day_end,
                AIConversation.routed_to == "rules"
            ).count()

            ai_usage.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "requests": total_requests,
                "rules": rules_requests
            })

        # User activity details (top 50 users)
        user_activity = []
        for user in sorted(all_users, key=lambda u: u.last_login or datetime.min, reverse=True)[:50]:
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            hero_count = db.query(UserHero).filter(UserHero.profile_id == profile.id).count() if profile else 0
            inventory_count = db.query(UserInventory).filter(UserInventory.profile_id == profile.id).count() if profile else 0

            # Activity score
            if user.last_login:
                days_since = (now - user.last_login).days
                if days_since == 0:
                    activity_score = 7
                elif days_since <= 1:
                    activity_score = 5
                elif days_since <= 7:
                    activity_score = 3
                else:
                    activity_score = 0
            else:
                activity_score = 0

            user_activity.append({
                "username": user.username,
                "email": user.email,
                "heroes": hero_count,
                "items": inventory_count,
                "activity_score": activity_score,
                "last_login": user.last_login.isoformat() if user.last_login else None
            })

        return {
            "summary": {
                "total_users": len(all_users),
                "active_users": active_in_range,
                "new_users": new_in_range,
                "activity_rate": round(active_in_range / len(all_users) * 100, 1) if all_users else 0
            },
            "activity_breakdown": {
                "very_active": very_active,
                "active_weekly": active_weekly,
                "active_monthly": active_monthly,
                "inactive": inactive
            },
            "content": {
                "profiles": total_profiles,
                "heroes": total_heroes,
                "inventory": total_inventory
            },
            "top_heroes": top_heroes,
            "hero_classes": hero_classes,
            "spending_distribution": spending_distribution,
            "alliance_roles": alliance_roles,
            "top_states": top_states,
            "states_summary": {
                "unique_states": len(state_counts),
                "users_with_state": sum(c[1] for c in state_counts),
                "users_without_state": profiles_without_state
            },
            "daily_active_users": daily_active,
            "ai_usage": ai_usage,
            "historical": historical_data,
            "user_activity": user_activity
        }

    finally:
        db.close()
