"""
Admin routes for the API.
Handles user management, announcements, feature flags, and system settings.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
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
    AISettings, Feedback, AuditLog, UserDailyLogin
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


@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
def list_feature_flags(admin_user: User = Depends(require_admin)):
    """List all feature flags."""
    init_db()
    db = get_db()

    try:
        flags = db.query(FeatureFlag).all()

        return [
            {
                "id": f.id,
                "name": f.name,
                "is_enabled": f.is_enabled,
                "description": f.description
            }
            for f in flags
        ]

    finally:
        db.close()


@router.put("/feature-flags/{flag_name}")
def toggle_feature_flag(
    flag_name: str,
    is_enabled: bool,
    admin_user: User = Depends(require_admin)
):
    """Toggle a feature flag."""
    init_db()
    db = get_db()

    try:
        flag = db.query(FeatureFlag).filter(FeatureFlag.name == flag_name).first()

        if not flag:
            # Create new flag
            flag = FeatureFlag(name=flag_name, is_enabled=is_enabled)
            db.add(flag)
        else:
            flag.is_enabled = is_enabled

        db.commit()

        return {"status": "success", "name": flag_name, "is_enabled": is_enabled}

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
    user_id: int
    type: str
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
            query = query.filter(Feedback.type == feedback_type)

        feedback_items = query.order_by(Feedback.created_at.desc()).all()

        return [
            {
                "id": f.id,
                "user_id": f.user_id,
                "type": f.type,
                "message": f.message,
                "status": f.status or "new",
                "created_at": f.created_at
            }
            for f in feedback_items
        ]

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
