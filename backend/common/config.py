"""Environment configuration for Lambda functions."""

import os


class Config:
    """Configuration loaded from environment variables set by SAM template."""

    # AWS region
    REGION = os.environ.get("AWS_REGION", "us-east-1")

    # DynamoDB tables
    MAIN_TABLE = os.environ.get("MAIN_TABLE", "WoS-Main")
    ADMIN_TABLE = os.environ.get("ADMIN_TABLE", "WoS-Admin")
    REFERENCE_TABLE = os.environ.get("REFERENCE_TABLE", "WoS-Reference")

    # Cognito
    USER_POOL_ID = os.environ.get("USER_POOL_ID", "")
    USER_POOL_CLIENT_ID = os.environ.get("USER_POOL_CLIENT_ID", "")

    # Secrets Manager
    SECRETS_ARN = os.environ.get("SECRETS_ARN", "")

    # AI providers
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    # SES
    SES_FROM_EMAIL = os.environ.get("SES_FROM_EMAIL", "noreply@randomchaoslabs.com")

    # Environment
    STAGE = os.environ.get("STAGE", "dev")
    IS_LOCAL = os.environ.get("AWS_SAM_LOCAL", "") == "true"

    # Data directory (bundled with Lambda)
    DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

    @classmethod
    def is_production(cls) -> bool:
        return cls.STAGE == "live"
