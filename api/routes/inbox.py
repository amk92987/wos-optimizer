"""
User Inbox Routes - Notifications and messages for users.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database.db import init_db, get_db
from database.models import User, UserNotification, Announcement, MessageThread, Message
from api.routes.auth import get_current_user

router = APIRouter(prefix="/inbox", tags=["inbox"])


class NotificationResponse(BaseModel):
    id: int
    announcement_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class UnreadCountResponse(BaseModel):
    unread_notifications: int
    unread_messages: int
    total_unread: int


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(current_user: User = Depends(get_current_user)):
    """Get count of unread notifications and messages for current user."""
    init_db()
    db = get_db()

    try:
        # Count unread notifications
        unread_notifications = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.id,
            UserNotification.is_read == False
        ).count()

        # Count unread messages (messages in threads where the user hasn't read the latest)
        # For now, count threads with messages from admin that aren't read
        unread_messages = db.query(Message).join(MessageThread).filter(
            MessageThread.user_id == current_user.id,
            Message.sender_id != current_user.id,
            Message.is_read == False
        ).count()

        return {
            "unread_notifications": unread_notifications,
            "unread_messages": unread_messages,
            "total_unread": unread_notifications + unread_messages
        }
    finally:
        db.close()


@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(current_user: User = Depends(get_current_user)):
    """Get all notifications for the current user."""
    init_db()
    db = get_db()

    try:
        notifications = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.id
        ).order_by(UserNotification.created_at.desc()).all()

        result = []
        for n in notifications:
            announcement = db.query(Announcement).filter(
                Announcement.id == n.announcement_id
            ).first()

            if announcement:
                result.append({
                    "id": n.id,
                    "announcement_id": n.announcement_id,
                    "title": announcement.title,
                    "message": announcement.inbox_content or announcement.message,
                    "type": announcement.type or "info",
                    "is_read": n.is_read,
                    "created_at": n.created_at
                })

        return result
    finally:
        db.close()


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    init_db()
    db = get_db()

    try:
        notification = db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == current_user.id
        ).first()

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()

        return {"success": True}
    finally:
        db.close()


@router.post("/notifications/mark-all-read")
def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    """Mark all notifications as read for the current user."""
    init_db()
    db = get_db()

    try:
        db.query(UserNotification).filter(
            UserNotification.user_id == current_user.id,
            UserNotification.is_read == False
        ).update({
            UserNotification.is_read: True,
            UserNotification.read_at: datetime.utcnow()
        })
        db.commit()

        return {"success": True}
    finally:
        db.close()
