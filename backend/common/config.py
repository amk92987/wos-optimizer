"""Environment configuration for Lambda functions."""

import json
import os


def _load_secrets():
    """Load API keys from AWS Secrets Manager if available."""
    arn = os.environ.get("SECRETS_ARN", "")
    if not arn:
        return {}
    try:
        import boto3
        client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        resp = client.get_secret_value(SecretId=arn)
        return json.loads(resp["SecretString"])
    except Exception:
        return {}


# Load secrets once at module import (Lambda cold start)
# Inject into os.environ so all code (including ai_recommender) can find them
_secrets = _load_secrets()
for _key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    if _secrets.get(_key) and not os.environ.get(_key):
        os.environ[_key] = _secrets[_key]


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

    # AI providers (env vars first, then Secrets Manager)
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "") or _secrets.get("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "") or _secrets.get("OPENAI_API_KEY", "")

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
