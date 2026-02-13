"""Cognito token validation and auth helpers.

JWT validation is handled by API Gateway's Cognito authorizer.
This module extracts user info from the validated JWT claims
placed in the event's requestContext by API Gateway HTTP API.

Claims path: event['requestContext']['authorizer']['jwt']['claims']
"""

from typing import Optional

from common.exceptions import AuthenticationError, AuthorizationError
from common.user_repo import get_user


def get_user_claims(event: dict) -> dict:
    """Extract all JWT claims from API Gateway event.

    API Gateway HTTP API places validated JWT claims at:
        event['requestContext']['authorizer']['jwt']['claims']

    Returns:
        dict of JWT claims.

    Raises:
        AuthenticationError: If claims are missing from the event.
    """
    try:
        return event["requestContext"]["authorizer"]["jwt"]["claims"]
    except (KeyError, TypeError):
        raise AuthenticationError("Missing or invalid authentication token")


def get_user_id(event: dict) -> str:
    """Extract cognito_sub from API Gateway event.

    Returns:
        The Cognito user ID (sub claim).

    Raises:
        AuthenticationError: If the sub claim is missing.
    """
    claims = get_user_claims(event)
    sub = claims.get("sub")
    if not sub:
        raise AuthenticationError("Missing user identifier in token")
    return sub


def get_user_email(event: dict) -> str:
    """Extract email from JWT claims.

    Returns:
        The user's email address.

    Raises:
        AuthenticationError: If the email claim is missing.
    """
    claims = get_user_claims(event)
    email = claims.get("email")
    if not email:
        raise AuthenticationError("Missing email in token")
    return email


def is_admin(event: dict) -> bool:
    """Check if current user has admin role.

    Looks up the user's role from DynamoDB since Cognito access
    tokens don't include custom attributes.

    Returns:
        True if the user's role is 'admin', False otherwise.
    """
    user_id = get_user_id(event)
    user = get_user(user_id)
    if not user:
        return False
    return user.get("role") == "admin"


def is_test_account(event: dict) -> bool:
    """Check if current user is a test account.

    Looks up the user's test flag from DynamoDB since Cognito access
    tokens don't include custom attributes.

    Returns:
        True if the user is a test account.
    """
    user_id = get_user_id(event)
    user = get_user(user_id)
    if not user:
        return False
    return user.get("is_test_account", False) is True


def require_admin(event: dict) -> None:
    """Raise AuthorizationError if the current user is not an admin.

    Use this as a guard at the top of admin-only handlers.

    Raises:
        AuthorizationError: If the user does not have admin role.
    """
    if not is_admin(event):
        raise AuthorizationError("Admin access required")


def get_impersonation_target(event: dict) -> Optional[str]:
    """Check for X-Impersonate-User header (admin only).

    Allows admins to act on behalf of another user by passing
    their cognito_sub in the X-Impersonate-User request header.

    Returns:
        The target user's cognito_sub if impersonation is requested
        and the caller is an admin, otherwise None.

    Raises:
        AuthorizationError: If a non-admin attempts impersonation.
    """
    headers = event.get("headers") or {}
    # HTTP API lowercases all header names
    target = headers.get("x-impersonate-user")
    if not target:
        return None

    if not is_admin(event):
        raise AuthorizationError("Only admins can impersonate users")

    return target


def get_effective_user_id(event: dict) -> str:
    """Get the effective user ID, accounting for admin impersonation.

    If an admin passes the X-Impersonate-User header, the target
    user's ID is returned. Otherwise, the authenticated user's own
    ID is returned.

    Returns:
        The cognito_sub of the effective user.

    Raises:
        AuthenticationError: If user identity cannot be determined.
        AuthorizationError: If a non-admin attempts impersonation.
    """
    target = get_impersonation_target(event)
    if target:
        return target
    return get_user_id(event)
