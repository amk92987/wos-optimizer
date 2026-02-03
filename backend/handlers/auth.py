"""Lambda handler for authentication routes.

Provides login, registration, password management, and user migration
from the legacy bcrypt-based system to Cognito.
"""

import json
from datetime import datetime, timezone

import bcrypt
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError as PowerNotFound,
    UnauthorizedError,
)

from common.auth import get_user_id, get_user_email, get_effective_user_id
from common.config import Config
from common.exceptions import AppError, ValidationError, ConflictError
from common.user_repo import (
    get_user,
    create_user,
    update_user,
    record_daily_login,
    get_user_by_email,
)

app = APIGatewayHttpResolver()
logger = Logger()

cognito = boto3.client("cognito-idp", region_name=Config.REGION)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cognito_auth(email: str, password: str) -> dict:
    """Authenticate with Cognito and return token set."""
    resp = cognito.initiate_auth(
        ClientId=Config.USER_POOL_CLIENT_ID,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": email,
            "PASSWORD": password,
        },
    )
    result = resp["AuthenticationResult"]
    return {
        "access_token": result["AccessToken"],
        "id_token": result["IdToken"],
        "refresh_token": result.get("RefreshToken", ""),
    }


def _user_response(user: dict) -> dict:
    """Format a user record for the API response."""
    return {
        "id": user.get("user_id", ""),
        "email": user.get("email", ""),
        "username": user.get("username", ""),
        "role": user.get("role", "user"),
        "is_active": user.get("is_active", True),
        "is_test_account": user.get("is_test_account", False),
        "created_at": user.get("created_at", ""),
    }


# ---------------------------------------------------------------------------
# Public routes (no auth required)
# ---------------------------------------------------------------------------

@app.post("/api/auth/login")
def login():
    """Authenticate user and return tokens + user info."""
    body = app.current_event.json_body or {}
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        raise BadRequestError("Email and password are required")

    try:
        tokens = _cognito_auth(email, password)
    except cognito.exceptions.NotAuthorizedException:
        raise UnauthorizedError("Invalid email or password")
    except cognito.exceptions.UserNotFoundException:
        raise UnauthorizedError("Invalid email or password")
    except cognito.exceptions.UserNotConfirmedException:
        raise UnauthorizedError("Account is not confirmed. Please check your email.")
    except Exception as e:
        logger.error("Cognito auth error", error=str(e))
        raise BadRequestError("Authentication failed")

    # Look up the Cognito sub from the ID token to find the DynamoDB user
    cognito_user = cognito.get_user(AccessToken=tokens["access_token"])
    sub = None
    for attr in cognito_user.get("UserAttributes", []):
        if attr["Name"] == "sub":
            sub = attr["Value"]
            break

    if not sub:
        logger.error("No sub claim in Cognito user attributes")
        raise BadRequestError("Authentication failed")

    # Record login activity
    try:
        record_daily_login(sub)
    except Exception:
        # Daily login already recorded or DynamoDB hiccup -- non-fatal
        pass

    # Update last_login timestamp
    try:
        update_user(sub, {"last_login": datetime.now(timezone.utc).isoformat()})
    except Exception:
        pass

    # Fetch full user record from DynamoDB
    user = get_user(sub)
    if not user:
        logger.warning("Cognito user has no DynamoDB record", user_id=sub, email=email)
        # Create a minimal record so the app still works
        user = create_user(user_id=sub, email=email, username=email)

    return {
        **tokens,
        "user": _user_response(user),
    }


@app.post("/api/auth/register")
def register():
    """Create a new user account."""
    body = app.current_event.json_body or {}
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        raise BadRequestError("Email and password are required")

    if len(password) < 6:
        raise BadRequestError("Password must be at least 6 characters")

    # Sign up in Cognito
    try:
        signup_resp = cognito.sign_up(
            ClientId=Config.USER_POOL_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
            ],
        )
        cognito_sub = signup_resp["UserSub"]
    except cognito.exceptions.UsernameExistsException:
        raise BadRequestError("An account with this email already exists")
    except cognito.exceptions.InvalidPasswordException as e:
        raise BadRequestError(f"Password does not meet requirements: {e}")
    except Exception as e:
        logger.error("Cognito sign_up error", error=str(e))
        raise BadRequestError("Registration failed")

    # Auto-confirm the user so they can log in immediately
    try:
        cognito.admin_confirm_sign_up(
            UserPoolId=Config.USER_POOL_ID,
            Username=email,
        )
    except Exception as e:
        logger.error("Cognito admin_confirm_sign_up error", error=str(e))
        # User was created but not confirmed -- still proceed with DynamoDB record
        # They can use forgot-password flow to gain access later

    # Create DynamoDB user record with uniqueness guards
    try:
        user = create_user(
            user_id=cognito_sub,
            email=email,
            username=email,
        )
    except ConflictError:
        # Cognito user was created but DynamoDB guard failed -- edge case
        raise BadRequestError("An account with this email already exists")

    # Log the user in automatically
    try:
        tokens = _cognito_auth(email, password)
    except Exception as e:
        logger.error("Post-registration login failed", error=str(e))
        raise BadRequestError("Account created but auto-login failed. Please log in manually.")

    return {
        **tokens,
        "user": _user_response(user),
    }


@app.post("/api/auth/forgot-password")
def forgot_password():
    """Initiate Cognito forgot-password flow (sends code via email)."""
    body = app.current_event.json_body or {}
    email = body.get("email", "").strip().lower()

    if not email:
        raise BadRequestError("Email is required")

    try:
        cognito.forgot_password(
            ClientId=Config.USER_POOL_CLIENT_ID,
            Username=email,
        )
    except cognito.exceptions.UserNotFoundException:
        # Don't reveal whether the account exists
        pass
    except Exception as e:
        logger.error("Cognito forgot_password error", error=str(e))
        raise BadRequestError("Unable to process password reset request")

    return {"message": "If an account with that email exists, a reset code has been sent."}


@app.post("/api/auth/confirm-reset")
def confirm_reset():
    """Confirm a password reset with the code from email."""
    body = app.current_event.json_body or {}
    email = body.get("email", "").strip().lower()
    code = body.get("code", "").strip()
    new_password = body.get("new_password", "")

    if not email or not code or not new_password:
        raise BadRequestError("Email, code, and new_password are required")

    try:
        cognito.confirm_forgot_password(
            ClientId=Config.USER_POOL_CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            Password=new_password,
        )
    except cognito.exceptions.CodeMismatchException:
        raise BadRequestError("Invalid or expired verification code")
    except cognito.exceptions.ExpiredCodeException:
        raise BadRequestError("Verification code has expired. Please request a new one.")
    except cognito.exceptions.InvalidPasswordException as e:
        raise BadRequestError(f"Password does not meet requirements: {e}")
    except Exception as e:
        logger.error("Cognito confirm_forgot_password error", error=str(e))
        raise BadRequestError("Password reset failed")

    return {"message": "Password has been reset successfully. You can now log in."}


# ---------------------------------------------------------------------------
# Authenticated routes
# ---------------------------------------------------------------------------

@app.get("/api/auth/me")
def me():
    """Return current user's profile from JWT claims + DynamoDB."""
    event = app.current_event.raw_event
    user_id = get_user_id(event)
    email = get_user_email(event)

    user = get_user(user_id)
    if not user:
        # First time this Cognito user hits /me -- create a record
        user = create_user(user_id=user_id, email=email, username=email)

    return _user_response(user)


@app.post("/api/auth/refresh")
def refresh_token():
    """Refresh Cognito tokens using a refresh_token."""
    body = app.current_event.json_body or {}
    refresh_tok = body.get("refresh_token", "")

    if not refresh_tok:
        raise BadRequestError("refresh_token is required")

    try:
        resp = cognito.initiate_auth(
            ClientId=Config.USER_POOL_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_tok,
            },
        )
        result = resp["AuthenticationResult"]
        tokens = {
            "access_token": result["AccessToken"],
            "id_token": result["IdToken"],
            # Cognito may not return a new refresh token on refresh
            "refresh_token": result.get("RefreshToken", refresh_tok),
        }

        # Look up user from the new access token
        cognito_user = cognito.get_user(AccessToken=tokens["access_token"])
        sub = None
        for attr in cognito_user.get("UserAttributes", []):
            if attr["Name"] == "sub":
                sub = attr["Value"]
                break

        user = get_user(sub) if sub else None
        return {
            **tokens,
            "user": _user_response(user) if user else None,
        }

    except cognito.exceptions.NotAuthorizedException:
        raise UnauthorizedError("Refresh token is invalid or expired")
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        raise BadRequestError("Token refresh failed")


@app.post("/api/auth/change-password")
def change_password():
    """Change password for the currently authenticated user."""
    body = app.current_event.json_body or {}
    access_token = body.get("access_token", "")
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")

    if not access_token or not old_password or not new_password:
        raise BadRequestError("access_token, old_password, and new_password are required")

    try:
        cognito.change_password(
            AccessToken=access_token,
            PreviousPassword=old_password,
            ProposedPassword=new_password,
        )
    except cognito.exceptions.NotAuthorizedException:
        raise UnauthorizedError("Current password is incorrect")
    except cognito.exceptions.InvalidPasswordException as e:
        raise BadRequestError(f"New password does not meet requirements: {e}")
    except Exception as e:
        logger.error("Cognito change_password error", error=str(e))
        raise BadRequestError("Password change failed")

    return {"message": "Password changed successfully."}


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@app.exception_handler(AppError)
def handle_app_error(ex: AppError):
    """Convert AppError subclasses into proper HTTP responses."""
    logger.warning("AppError", error=ex.message, status=ex.status_code)
    return Response(
        status_code=ex.status_code,
        content_type="application/json",
        body=json.dumps({"error": ex.message}),
    )


# ---------------------------------------------------------------------------
# Lambda entry point
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    """Main Lambda handler -- routes via Powertools resolver."""
    return app.resolve(event, context)


# ---------------------------------------------------------------------------
# Cognito User Migration Trigger
# ---------------------------------------------------------------------------

def user_migration_handler(event, context):
    """Handle Cognito user migration trigger for legacy bcrypt users.

    When an existing user tries to sign in or sign up through Cognito for
    the first time, this trigger checks whether they have an existing
    DynamoDB record with a bcrypt password hash. If the password matches,
    the user is automatically migrated into the Cognito user pool.

    Trigger sources:
        - UserMigration_Authentication: user attempting to log in
        - UserMigration_ForgotPassword: user requesting a password reset
    """
    trigger_source = event.get("triggerSource", "")
    email = event.get("userName", "").strip().lower()
    password = (event.get("request", {}).get("password") or "")

    logger.info(
        "User migration trigger",
        trigger_source=trigger_source,
        email=email,
    )

    if trigger_source == "UserMigration_Authentication":
        if not email or not password:
            logger.warning("Migration auth: missing email or password")
            raise Exception("Bad migration request")

        # Look up legacy user by email
        user = get_user_by_email(email)
        if not user:
            logger.info("Migration auth: no legacy user found", email=email)
            raise Exception("User not found")

        stored_hash = user.get("password_hash", "")
        if not stored_hash:
            logger.info("Migration auth: no password hash for user", email=email)
            raise Exception("User not found")

        # Verify bcrypt password
        if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
            logger.info("Migration auth: password mismatch", email=email)
            raise Exception("Incorrect password")

        # Password matches -- allow Cognito to create the user
        event["response"]["userAttributes"] = {
            "email": email,
            "email_verified": "true",
        }
        event["response"]["finalUserStatus"] = "CONFIRMED"
        event["response"]["messageAction"] = "SUPPRESS"
        event["response"]["forceAliasCreation"] = False

        logger.info("Migration auth: user migrated successfully", email=email)

    elif trigger_source == "UserMigration_ForgotPassword":
        # Allow forgot-password if a legacy user exists
        user = get_user_by_email(email)
        if not user:
            logger.info("Migration forgot: no legacy user found", email=email)
            raise Exception("User not found")

        event["response"]["userAttributes"] = {
            "email": email,
            "email_verified": "true",
        }
        event["response"]["messageAction"] = "SUPPRESS"

        logger.info("Migration forgot: user eligible for migration", email=email)

    else:
        logger.warning("Unknown migration trigger source", trigger_source=trigger_source)

    return event
