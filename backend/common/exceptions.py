"""Custom exception types for Lambda handlers."""


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppError):
    """Input validation failed."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=400)


class AuthenticationError(AppError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class AuthorizationError(AppError):
    """Insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class ConflictError(AppError):
    """Resource already exists or conflict."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class RateLimitError(AppError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ExternalServiceError(AppError):
    """External service (AI, SES, etc.) failed."""

    def __init__(self, message: str = "External service error"):
        super().__init__(message, status_code=502)
