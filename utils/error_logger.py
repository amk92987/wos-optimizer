"""
Error logging utility for Bear's Den.
Logs errors to database and sends email notifications.

Usage:
    from utils.error_logger import log_error, handle_errors

    # Manual logging
    try:
        risky_operation()
    except Exception as e:
        log_error(e, page="Hero Tracker", extra_context={"hero_id": 123})

    # Decorator for automatic error handling
    @handle_errors(page="AI Advisor")
    def my_function():
        ...
"""

import traceback
import streamlit as st
from datetime import datetime
from functools import wraps
from typing import Optional, Any
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import ENV, ADMIN_EMAIL


def log_error(
    exception: Exception,
    page: Optional[str] = None,
    function: Optional[str] = None,
    extra_context: Optional[dict] = None,
    send_email: bool = True
) -> Optional[int]:
    """
    Log an error to the database and optionally send email notification.

    Args:
        exception: The exception that occurred
        page: Which page/module the error occurred in
        function: Function name if available
        extra_context: Additional debug information as dict
        send_email: Whether to send email notification (default True)

    Returns:
        Error log ID if saved successfully, None otherwise
    """
    from database.db import get_db
    from database.models import ErrorLog

    try:
        db = get_db()

        # Get user context from session state
        user_id = st.session_state.get('user_id')
        profile_id = st.session_state.get('profile_id')

        # Get session ID if available
        session_id = None
        try:
            session_id = st.runtime.scriptrunner.get_script_run_ctx().session_id
        except:
            pass

        # Build error details
        error_type = type(exception).__name__
        error_message = str(exception)
        stack_trace = traceback.format_exc()

        # Create error log entry
        error_log = ErrorLog(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            page=page,
            function=function,
            user_id=user_id,
            profile_id=profile_id,
            session_id=session_id,
            extra_context=extra_context,
            environment=ENV,
            status='new',
            email_sent=False
        )

        db.add(error_log)
        db.commit()
        db.refresh(error_log)

        # Send email notification
        if send_email and ENV in ('production', 'staging'):
            _send_error_email(error_log)
            error_log.email_sent = True
            db.commit()

        return error_log.id

    except Exception as log_error:
        # Don't let logging errors crash the app
        print(f"[ERROR LOGGER] Failed to log error: {log_error}")
        print(f"[ERROR LOGGER] Original error: {exception}")
        traceback.print_exc()
        return None


def _send_error_email(error_log) -> bool:
    """Send email notification for an error."""
    from utils.email import send_email

    admin_email = ADMIN_EMAIL

    subject = f"[Bear's Den {error_log.environment}] Error: {error_log.error_type}"

    body_text = f"""An error occurred in Bear's Den ({error_log.environment}):

Error Type: {error_log.error_type}
Message: {error_log.error_message}
Page: {error_log.page or 'Unknown'}
Function: {error_log.function or 'Unknown'}
User ID: {error_log.user_id or 'Anonymous'}
Time: {error_log.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Stack Trace:
{error_log.stack_trace}

Extra Context:
{error_log.extra_context or 'None'}

---
Error ID: {error_log.id}
Review in Admin or run: /wos-errors
"""

    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
        .container {{ max-width: 700px; margin: 0 auto; background: #16213e; padding: 20px; border-radius: 8px; border-left: 4px solid #e74c3c; }}
        h2 {{ color: #e74c3c; margin-top: 0; }}
        .field {{ margin: 10px 0; }}
        .label {{ color: #7dd3fc; font-weight: bold; }}
        .value {{ color: #fff; }}
        pre {{ background: #0f0f23; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 12px; color: #ccc; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #888; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Error Alert: {error_log.error_type}</h2>

        <div class="field">
            <span class="label">Environment:</span>
            <span class="value">{error_log.environment}</span>
        </div>

        <div class="field">
            <span class="label">Message:</span>
            <span class="value">{error_log.error_message}</span>
        </div>

        <div class="field">
            <span class="label">Page:</span>
            <span class="value">{error_log.page or 'Unknown'}</span>
        </div>

        <div class="field">
            <span class="label">User ID:</span>
            <span class="value">{error_log.user_id or 'Anonymous'}</span>
        </div>

        <div class="field">
            <span class="label">Time:</span>
            <span class="value">{error_log.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
        </div>

        <div class="field">
            <span class="label">Stack Trace:</span>
            <pre>{error_log.stack_trace}</pre>
        </div>

        <div class="footer">
            Error ID: {error_log.id} | Review in Admin or run: /wos-errors
        </div>
    </div>
</body>
</html>
"""

    success, msg = send_email(admin_email, subject, body_text, body_html)
    return success


def handle_errors(page: str = None, show_user_message: bool = True):
    """
    Decorator to automatically catch and log errors from a function.

    Args:
        page: Page name for context
        show_user_message: Whether to show error message to user (default True)

    Usage:
        @handle_errors(page="AI Advisor")
        def risky_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_id = log_error(
                    e,
                    page=page,
                    function=func.__name__,
                    extra_context={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]}
                )

                if show_user_message:
                    st.error(f"An error occurred. Our team has been notified. (Error #{error_id})")

                # Re-raise in development for debugging
                if ENV == 'development':
                    raise

        return wrapper
    return decorator


def get_recent_errors(limit: int = 20, status: str = None, page: str = None):
    """
    Get recent errors from the database.

    Args:
        limit: Maximum number of errors to return
        status: Filter by status (new, reviewed, fixed, ignored)
        page: Filter by page name

    Returns:
        List of ErrorLog objects
    """
    from database.db import get_db
    from database.models import ErrorLog

    db = get_db()
    query = db.query(ErrorLog)

    if status:
        query = query.filter(ErrorLog.status == status)
    if page:
        query = query.filter(ErrorLog.page == page)

    return query.order_by(ErrorLog.created_at.desc()).limit(limit).all()


def mark_error_reviewed(error_id: int, reviewer_id: int, fix_notes: str = None, new_status: str = 'reviewed'):
    """
    Mark an error as reviewed.

    Args:
        error_id: Error log ID
        reviewer_id: User ID of reviewer
        fix_notes: Notes about the fix
        new_status: New status (reviewed, fixed, ignored)
    """
    from database.db import get_db
    from database.models import ErrorLog

    db = get_db()
    error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()

    if error:
        error.status = new_status
        error.reviewed_by = reviewer_id
        error.reviewed_at = datetime.utcnow()
        if fix_notes:
            error.fix_notes = fix_notes
        db.commit()
        return True

    return False


def get_error_summary():
    """Get summary of error counts by status."""
    from database.db import get_db
    from database.models import ErrorLog
    from sqlalchemy import func

    db = get_db()

    results = db.query(
        ErrorLog.status,
        func.count(ErrorLog.id)
    ).group_by(ErrorLog.status).all()

    summary = {status: count for status, count in results}

    # Also get count from last 24 hours
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_count = db.query(ErrorLog).filter(ErrorLog.created_at >= yesterday).count()
    summary['last_24h'] = recent_count

    return summary
