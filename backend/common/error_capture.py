"""Capture unhandled exceptions to DynamoDB error store."""

import traceback

from common import admin_repo
from common.config import Config


def capture_error(
    handler_name: str,
    event: dict,
    exc: Exception,
    logger,
) -> None:
    """Log an unhandled exception to the admin error store.

    Safe to call from any Lambda handler's except block.
    Never raises -- error capture must not break the 500 response.
    """
    try:
        # Extract user_id from JWT claims if present
        user_id = None
        try:
            claims = (
                event.get("requestContext", {})
                .get("authorizer", {})
                .get("jwt", {})
                .get("claims", {})
            )
            user_id = claims.get("sub")
        except Exception:
            pass

        admin_repo.log_error(
            error_type=type(exc).__name__,
            error_message=str(exc)[:2000],
            stack_trace=traceback.format_exc()[:4000],
            page=handler_name,
            function=handler_name,
            user_id=user_id,
            environment=Config.STAGE,
        )
    except Exception:
        logger.exception("Failed to capture error to DynamoDB")
