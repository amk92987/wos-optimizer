"""Messaging and notification service layer."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import (
    User, Announcement, UserNotification, MessageThread, Message
)

# Import error logger - use lazy import to avoid circular dependencies
def _log_error(exception, function_name, extra_context=None):
    """Log error to database with messaging context."""
    try:
        from utils.error_logger import log_error
        log_error(
            exception,
            page="Messaging Service",
            function=function_name,
            extra_context=extra_context,
            send_email=True
        )
    except Exception:
        # If error logging fails, at least print to console
        print(f"[MESSAGING ERROR] {function_name}: {exception}")


# ============================================
# NOTIFICATIONS (Announcements to User Inboxes)
# ============================================

def create_notification_for_users(
    db: Session,
    announcement_id: int,
    user_ids: Optional[List[int]] = None
) -> int:
    """Create UserNotification records for an announcement.

    Args:
        db: Database session
        announcement_id: ID of the announcement to notify about
        user_ids: List of user IDs to notify. If None, notifies all active non-admin users.

    Returns:
        Number of notifications created (0 on error)
    """
    try:
        if user_ids is None:
            # Get all active non-admin users
            users = db.query(User).filter(
                User.is_active == True,
                User.role != 'admin'
            ).all()
            user_ids = [u.id for u in users]

        count = 0
        for user_id in user_ids:
            # Check if notification already exists
            existing = db.query(UserNotification).filter(
                UserNotification.user_id == user_id,
                UserNotification.announcement_id == announcement_id
            ).first()

            if not existing:
                notification = UserNotification(
                    user_id=user_id,
                    announcement_id=announcement_id,
                    is_read=False
                )
                db.add(notification)
                count += 1

        db.commit()
        return count
    except Exception as e:
        db.rollback()
        _log_error(e, "create_notification_for_users", {"announcement_id": announcement_id, "user_count": len(user_ids) if user_ids else 0})
        return 0


def get_user_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    limit: int = 50
) -> List[UserNotification]:
    """Get notifications for a user.

    Args:
        db: Database session
        user_id: User ID
        unread_only: If True, only return unread notifications
        limit: Maximum number to return

    Returns:
        List of UserNotification objects with announcement data loaded (empty list on error)
    """
    try:
        query = db.query(UserNotification).filter(
            UserNotification.user_id == user_id
        )

        if unread_only:
            query = query.filter(UserNotification.is_read == False)

        # Join with Announcement to filter only active ones
        query = query.join(Announcement).filter(
            Announcement.is_active == True,
            or_(
                Announcement.display_type == 'inbox',
                Announcement.display_type == 'both'
            )
        )

        return query.order_by(UserNotification.created_at.desc()).limit(limit).all()
    except Exception as e:
        _log_error(e, "get_user_notifications", {"user_id": user_id})
        return []


def mark_notification_read(db: Session, notification_id: int, user_id: int) -> bool:
    """Mark a notification as read.

    Args:
        db: Database session
        notification_id: ID of the notification
        user_id: User ID (for security - ensure user owns notification)

    Returns:
        True if marked, False if not found or error
    """
    try:
        notification = db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id
        ).first()

        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        _log_error(e, "mark_notification_read", {"notification_id": notification_id, "user_id": user_id})
        return False


def mark_notification_unread(db: Session, notification_id: int, user_id: int) -> bool:
    """Mark a notification as unread.

    Args:
        db: Database session
        notification_id: ID of the notification
        user_id: User ID (for security - ensure user owns notification)

    Returns:
        True if marked, False if not found or error
    """
    try:
        notification = db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id
        ).first()

        if notification:
            notification.is_read = False
            notification.read_at = None
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        _log_error(e, "mark_notification_unread", {"notification_id": notification_id, "user_id": user_id})
        return False


def mark_all_notifications_read(db: Session, user_id: int) -> int:
    """Mark all notifications as read for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of notifications marked as read (0 on error)
    """
    try:
        count = db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False
        ).update({
            UserNotification.is_read: True,
            UserNotification.read_at: datetime.utcnow()
        })
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        _log_error(e, "mark_all_notifications_read", {"user_id": user_id})
        return 0


# ============================================
# MESSAGES (Admin-to-User Direct Messaging)
# ============================================

def create_message_thread(
    db: Session,
    user_id: int,
    subject: str,
    admin_id: int,
    initial_message: str
) -> Optional[MessageThread]:
    """Admin creates a new conversation with a user.

    Args:
        db: Database session
        user_id: Target user ID
        subject: Thread subject
        admin_id: Admin's user ID
        initial_message: First message content

    Returns:
        The created MessageThread, or None on error
    """
    try:
        # Create thread
        thread = MessageThread(
            user_id=user_id,
            subject=subject
        )
        db.add(thread)
        db.flush()  # Get thread ID

        # Add initial message from admin
        message = Message(
            thread_id=thread.id,
            sender_id=admin_id,
            content=initial_message,
            is_from_admin=True,
            is_read=False  # Unread by user
        )
        db.add(message)
        db.commit()
        db.refresh(thread)

        return thread
    except Exception as e:
        db.rollback()
        _log_error(e, "create_message_thread", {"user_id": user_id, "admin_id": admin_id, "subject": subject})
        return None


def add_message_to_thread(
    db: Session,
    thread_id: int,
    sender_id: int,
    content: str,
    is_from_admin: bool
) -> Optional[Message]:
    """Add a reply to an existing thread.

    Args:
        db: Database session
        thread_id: Thread ID
        sender_id: User ID of sender
        content: Message content
        is_from_admin: True if admin is sending

    Returns:
        The created Message, or None if thread not found or error
    """
    try:
        thread = db.query(MessageThread).filter(
            MessageThread.id == thread_id
        ).first()

        if not thread or thread.is_closed:
            return None

        message = Message(
            thread_id=thread_id,
            sender_id=sender_id,
            content=content,
            is_from_admin=is_from_admin,
            is_read=False
        )
        db.add(message)

        # Update thread timestamp
        thread.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)
        return message
    except Exception as e:
        db.rollback()
        _log_error(e, "add_message_to_thread", {"thread_id": thread_id, "sender_id": sender_id, "is_from_admin": is_from_admin})
        return None


def get_user_threads(db: Session, user_id: int, limit: int = 20) -> List[MessageThread]:
    """Get all message threads for a user.

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number to return

    Returns:
        List of MessageThread objects ordered by most recent activity (empty list on error)
    """
    try:
        return db.query(MessageThread).filter(
            MessageThread.user_id == user_id
        ).order_by(MessageThread.updated_at.desc()).limit(limit).all()
    except Exception as e:
        _log_error(e, "get_user_threads", {"user_id": user_id})
        return []


def get_thread_messages(db: Session, thread_id: int) -> List[Message]:
    """Get all messages in a thread.

    Args:
        db: Database session
        thread_id: Thread ID

    Returns:
        List of Message objects ordered by creation time (empty list on error)
    """
    try:
        return db.query(Message).filter(
            Message.thread_id == thread_id
        ).order_by(Message.created_at.asc()).all()
    except Exception as e:
        _log_error(e, "get_thread_messages", {"thread_id": thread_id})
        return []


def mark_thread_messages_read(db: Session, thread_id: int, user_id: int) -> int:
    """Mark all messages in thread as read for a user.

    Only marks messages FROM admin as read when user opens thread.
    (Admin messages TO user should be marked read when user views them)

    Args:
        db: Database session
        thread_id: Thread ID
        user_id: User ID viewing the thread

    Returns:
        Number of messages marked as read (0 on error)
    """
    try:
        # Get thread to verify ownership
        thread = db.query(MessageThread).filter(
            MessageThread.id == thread_id,
            MessageThread.user_id == user_id
        ).first()

        if not thread:
            return 0

        # Mark all admin messages (to user) as read
        count = db.query(Message).filter(
            Message.thread_id == thread_id,
            Message.is_from_admin == True,
            Message.is_read == False
        ).update({
            Message.is_read: True,
            Message.read_at: datetime.utcnow()
        })
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        _log_error(e, "mark_thread_messages_read", {"thread_id": thread_id, "user_id": user_id})
        return 0


def mark_message_unread(db: Session, message_id: int) -> bool:
    """Mark a specific message as unread.

    Args:
        db: Database session
        message_id: Message ID

    Returns:
        True if marked, False if not found or error
    """
    try:
        message = db.query(Message).filter(Message.id == message_id).first()

        if message:
            message.is_read = False
            message.read_at = None
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        _log_error(e, "mark_message_unread", {"message_id": message_id})
        return False


def mark_message_read(db: Session, message_id: int) -> bool:
    """Mark a specific message as read.

    Args:
        db: Database session
        message_id: Message ID

    Returns:
        True if marked, False if not found or error
    """
    try:
        message = db.query(Message).filter(Message.id == message_id).first()

        if message:
            message.is_read = True
            message.read_at = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        _log_error(e, "mark_message_read", {"message_id": message_id})
        return False


def close_thread(db: Session, thread_id: int) -> bool:
    """Close a message thread (admin action).

    Args:
        db: Database session
        thread_id: Thread ID

    Returns:
        True if closed, False if not found or error
    """
    try:
        thread = db.query(MessageThread).filter(
            MessageThread.id == thread_id
        ).first()

        if thread:
            thread.is_closed = True
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        _log_error(e, "close_thread", {"thread_id": thread_id})
        return False


def reopen_thread(db: Session, thread_id: int) -> bool:
    """Reopen a closed message thread (admin action).

    Args:
        db: Database session
        thread_id: Thread ID

    Returns:
        True if reopened, False if not found or error
    """
    try:
        thread = db.query(MessageThread).filter(
            MessageThread.id == thread_id
        ).first()

        if thread:
            thread.is_closed = False
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        _log_error(e, "reopen_thread", {"thread_id": thread_id})
        return False


# ============================================
# ADMIN VIEWS
# ============================================

def get_admin_conversations(db: Session, limit: int = 50) -> List[MessageThread]:
    """Get all conversations for admin view.

    Args:
        db: Database session
        limit: Maximum number to return

    Returns:
        List of MessageThread objects with user data loaded (empty list on error)
    """
    try:
        return db.query(MessageThread).order_by(
            MessageThread.updated_at.desc()
        ).limit(limit).all()
    except Exception as e:
        _log_error(e, "get_admin_conversations", {})
        return []


def has_unread_user_replies(db: Session, thread_id: int) -> bool:
    """Check if thread has unread messages from user (for admin view).

    Args:
        db: Database session
        thread_id: Thread ID

    Returns:
        True if there are unread user messages (False on error)
    """
    try:
        count = db.query(Message).filter(
            Message.thread_id == thread_id,
            Message.is_from_admin == False,
            Message.is_read == False
        ).count()
        return count > 0
    except Exception as e:
        _log_error(e, "has_unread_user_replies", {"thread_id": thread_id})
        return False


def mark_user_replies_read(db: Session, thread_id: int) -> int:
    """Mark all user replies in a thread as read (admin viewing thread).

    Args:
        db: Database session
        thread_id: Thread ID

    Returns:
        Number of messages marked as read (0 on error)
    """
    try:
        count = db.query(Message).filter(
            Message.thread_id == thread_id,
            Message.is_from_admin == False,
            Message.is_read == False
        ).update({
            Message.is_read: True,
            Message.read_at: datetime.utcnow()
        })
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        _log_error(e, "mark_user_replies_read", {"thread_id": thread_id})
        return 0


# ============================================
# UNREAD COUNTS
# ============================================

def get_unread_notification_count(db: Session, user_id: int) -> int:
    """Get count of unread notifications for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of unread notifications (0 on error)
    """
    try:
        return db.query(UserNotification).join(Announcement).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False,
            Announcement.is_active == True,
            or_(
                Announcement.display_type == 'inbox',
                Announcement.display_type == 'both'
            )
        ).count()
    except Exception as e:
        _log_error(e, "get_unread_notification_count", {"user_id": user_id})
        return 0


def get_unread_message_count(db: Session, user_id: int) -> int:
    """Get count of unread messages for a user (from admin).

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of unread messages (0 on error)
    """
    try:
        return db.query(Message).join(MessageThread).filter(
            MessageThread.user_id == user_id,
            Message.is_from_admin == True,
            Message.is_read == False
        ).count()
    except Exception as e:
        _log_error(e, "get_unread_message_count", {"user_id": user_id})
        return 0


def get_unread_count(db: Session, user_id: int) -> int:
    """Get total unread count (notifications + messages) for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Total unread count (0 on error)
    """
    try:
        notifications = get_unread_notification_count(db, user_id)
        messages = get_unread_message_count(db, user_id)
        return notifications + messages
    except Exception as e:
        _log_error(e, "get_unread_count", {"user_id": user_id})
        return 0


def get_admin_unread_count(db: Session) -> int:
    """Get count of unread user replies across all threads (for admin badge).

    Args:
        db: Database session

    Returns:
        Number of unread user replies (0 on error)
    """
    try:
        return db.query(Message).filter(
            Message.is_from_admin == False,
            Message.is_read == False
        ).count()
    except Exception as e:
        _log_error(e, "get_admin_unread_count", {})
        return 0
