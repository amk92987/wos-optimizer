"""Rate limiting using DynamoDB admin table.

Tracks failed attempts per IP+action with auto-expiring TTL records.
Used to protect public auth endpoints (login, register, forgot-password)
from brute-force and automated attacks.
"""

import time
from datetime import datetime, timezone

from common.db import admin_table


class TooManyRequestsError(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 900):
        self.retry_after = retry_after
        super().__init__(f"Too many requests. Try again in {retry_after // 60} minutes.")


def check_rate_limit(ip: str, action: str, max_attempts: int, window_seconds: int) -> None:
    """Check if IP has exceeded rate limit for this action.

    Raises TooManyRequestsError if limit exceeded.
    """
    table = admin_table()
    pk = f"RATELIMIT#{action}"

    try:
        resp = table.get_item(Key={"PK": pk, "SK": ip})
    except Exception:
        return  # DynamoDB error — fail open, don't block legitimate users

    item = resp.get("Item")
    if not item:
        return

    attempts = int(item.get("attempts", 0))
    first_attempt = item.get("first_attempt", "")

    if not first_attempt or attempts < max_attempts:
        return

    # Check if still within the window
    try:
        first_dt = datetime.fromisoformat(first_attempt)
        elapsed = (datetime.now(timezone.utc) - first_dt).total_seconds()
        if elapsed < window_seconds:
            remaining = int(window_seconds - elapsed)
            raise TooManyRequestsError(retry_after=remaining)
    except TooManyRequestsError:
        raise
    except Exception:
        pass  # Malformed timestamp — fail open


def record_failed_attempt(ip: str, action: str, window_seconds: int) -> None:
    """Record a failed attempt for this IP+action.

    Creates or increments the counter. Sets TTL for auto-expiry.
    """
    table = admin_table()
    pk = f"RATELIMIT#{action}"
    now = datetime.now(timezone.utc).isoformat()
    ttl_epoch = int(time.time()) + window_seconds + 60  # extra minute buffer

    try:
        resp = table.get_item(Key={"PK": pk, "SK": ip})
        item = resp.get("Item")

        if item:
            # Check if window has expired — if so, reset
            first_attempt = item.get("first_attempt", "")
            try:
                first_dt = datetime.fromisoformat(first_attempt)
                elapsed = (datetime.now(timezone.utc) - first_dt).total_seconds()
                if elapsed >= window_seconds:
                    item = None  # Window expired, start fresh
            except Exception:
                item = None

        if item:
            # Increment existing counter
            table.update_item(
                Key={"PK": pk, "SK": ip},
                UpdateExpression="SET attempts = attempts + :one, #ttl = :ttl",
                ExpressionAttributeNames={"#ttl": "ttl"},
                ExpressionAttributeValues={":one": 1, ":ttl": ttl_epoch},
            )
        else:
            # First attempt in this window
            table.put_item(Item={
                "PK": pk,
                "SK": ip,
                "attempts": 1,
                "first_attempt": now,
                "ttl": ttl_epoch,
            })
    except Exception:
        pass  # DynamoDB error — don't break auth flow


def clear_attempts(ip: str, action: str) -> None:
    """Clear rate limit record after successful authentication."""
    table = admin_table()
    pk = f"RATELIMIT#{action}"

    try:
        table.delete_item(Key={"PK": pk, "SK": ip})
    except Exception:
        pass  # Non-critical — TTL will clean it up eventually
