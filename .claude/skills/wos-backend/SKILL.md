---
name: wos-backend
description: Build and modify Python Lambda backend handlers, DynamoDB repositories, recommendation engine, and AI integration. Covers handler patterns, data access, SAM template, and error handling.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python:*, pip:*)
---

# WoS Backend Development - Python Lambda / DynamoDB / SAM

## Purpose
Assists with building new API endpoints, modifying Lambda handlers, working with the DynamoDB data access layer, updating the recommendation engine, and managing the SAM infrastructure template.

## When to Use
- Building new Lambda handler routes
- Modifying DynamoDB data access (repos)
- Working on the recommendation/AI engine
- Updating the SAM template (new resources, permissions)
- Fixing backend bugs or adding error handling
- Managing the common layer shared across Lambdas

## Project Structure

```
backend/
├── __init__.py
├── requirements.txt              # Lambda layer dependencies
├── handlers/                     # Lambda function handlers
│   ├── __init__.py
│   ├── admin.py                  # Admin operations (users, flags, feedback, etc.)
│   ├── advisor.py                # AI advisor (conversations, threads)
│   ├── auth.py                   # Authentication (login, register, me, refresh)
│   ├── chief.py                  # Chief gear & charms CRUD
│   ├── general.py                # Health check, announcements, notifications
│   ├── heroes.py                 # Hero CRUD + reference data + images
│   ├── profiles.py               # Game profile management
│   └── recommendations.py        # Upgrade recommendations engine
├── common/                       # Shared layer (deployed as Lambda Layer)
│   ├── __init__.py
│   ├── admin_repo.py             # Admin table: flags, feedback, audit, metrics
│   ├── ai_repo.py                # AI conversations & threads
│   ├── auth.py                   # JWT validation, user ID extraction
│   ├── chief_repo.py             # Chief gear & charms data access
│   ├── config.py                 # Environment config (tables, keys, stage)
│   ├── db.py                     # DynamoDB CRUD helpers
│   ├── error_capture.py          # Error logging to admin table
│   ├── exceptions.py             # Custom exception classes
│   ├── hero_repo.py              # Hero data access (user + reference)
│   ├── models.py                 # Pydantic v2 models (entities + API schemas)
│   ├── profile_repo.py           # Profile data access
│   ├── rate_limit.py             # AI rate limiting
│   ├── requirements.txt          # Layer dependencies (separate from handler deps)
│   └── user_repo.py              # User account management
├── data/                         # Game data bundled with Lambda
│   └── heroes.json               # MUST stay in sync with data/heroes.json
├── assets/
│   └── heroes/                   # Hero portrait images (bundled for base64 API)
└── engine/                       # Recommendation engine
    ├── recommendation_engine.py  # Main orchestrator
    ├── recommender.py            # Rule-based recommendations
    ├── ai_recommender.py         # Claude/OpenAI AI integration
    └── analyzers/                # Specialized analyzers
        ├── hero_analyzer.py      # Hero upgrade analysis
        ├── gear_advisor.py       # Gear priority advisor
        ├── lineup_builder.py     # Lineup optimization
        ├── progression_tracker.py # Game phase detection
        └── request_classifier.py  # Routes questions to rules vs AI
```

## Handler Pattern

Every handler uses AWS Lambda Powertools with `APIGatewayHttpResolver`:

```python
"""Lambda handler for [resource] routes."""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from common.auth import get_effective_user_id
from common.exceptions import AppError, NotFoundError, ValidationError
from common.error_capture import capture_error

app = APIGatewayHttpResolver()
logger = Logger()


@app.get("/resource")
def list_resources():
    """List resources for the authenticated user."""
    raw_event = app.current_event.raw_event
    user_id = get_effective_user_id(raw_event)

    # Business logic here
    items = get_items_for_user(user_id)
    return {"items": items}


@app.post("/resource")
def create_resource():
    """Create a new resource."""
    raw_event = app.current_event.raw_event
    user_id = get_effective_user_id(raw_event)
    body = app.current_event.json_body

    # Validate input
    if not body.get("name"):
        raise ValidationError("name is required")

    # Create and return
    item = create_item(user_id, body)
    return {"item": item, "message": "Created successfully"}


@logger.inject_lambda_context
def handler(event, context):
    """Lambda entry point."""
    try:
        return app.resolve(event, context)
    except AppError as e:
        return {"statusCode": e.status_code, "body": json.dumps({"error": e.message})}
    except Exception as e:
        capture_error(e, event)
        logger.exception("Unhandled error")
        return {"statusCode": 500, "body": json.dumps({"error": "Internal server error"})}
```

## Repository Pattern

Data access uses repository modules in `backend/common/`:

```python
# backend/common/some_repo.py

from common.db import main_table, get_item, put_item, query, update_item, delete_item, prepare_item

def get_user_items(user_id: str) -> list[dict]:
    """Get all items for a user."""
    return query(
        main_table(),
        pk=f"USER#{user_id}",
        sk_begins_with="ITEM#",
    )

def get_user_item(user_id: str, item_id: str) -> dict | None:
    """Get a single item."""
    return get_item(
        main_table(),
        pk=f"USER#{user_id}",
        sk=f"ITEM#{item_id}",
    )

def save_user_item(user_id: str, item_id: str, data: dict) -> dict:
    """Save/update an item."""
    item = {
        "PK": f"USER#{user_id}",
        "SK": f"ITEM#{item_id}",
        **data,
    }
    put_item(main_table(), item)
    return item
```

## DynamoDB Helpers (backend/common/db.py)

| Function | Purpose |
|----------|---------|
| `main_table()` | Get main table reference |
| `admin_table()` | Get admin table reference |
| `reference_table()` | Get reference table reference |
| `get_item(table, pk, sk)` | Fetch single item |
| `query(table, pk, sk_begins_with=, sk_value=, ...)` | Query by PK with SK conditions |
| `put_item(table, item, condition=)` | Write/overwrite item |
| `update_item(table, pk, sk, update_expression, ...)` | Update specific fields |
| `delete_item(table, pk, sk)` | Delete item |
| `batch_write(table, items)` | Batch write up to 25 items |
| `batch_delete(table, keys)` | Batch delete items |
| `transact_write_items(operations)` | Transactional writes |
| `prepare_item(dict)` | Strip None + convert to Decimal |
| `from_decimal(item)` | Convert Decimal back to int/float |

## Authentication (backend/common/auth.py)

```python
from common.auth import get_effective_user_id

# Extract user ID from Cognito JWT in API Gateway event
raw_event = app.current_event.raw_event
user_id = get_effective_user_id(raw_event)
# Returns the Cognito sub (UUID) or impersonated user ID
```

The auth module:
- Extracts the Cognito `sub` from the JWT `requestContext.authorizer.jwt.claims`
- Supports admin impersonation (reads `X-Impersonate-User` header)
- Returns the effective user ID for all downstream operations

## Exception Handling (backend/common/exceptions.py)

```python
from common.exceptions import AppError, NotFoundError, ValidationError, ForbiddenError

# Raise typed errors - they map to HTTP status codes
raise NotFoundError("Hero not found")       # 404
raise ValidationError("Invalid level")      # 400
raise ForbiddenError("Admin only")          # 403
raise AppError("Something broke", 500)      # Custom status
```

## Error Capture (backend/common/error_capture.py)

```python
from common.error_capture import capture_error

# Log errors to DynamoDB admin table for the /wos-errors skill
try:
    risky_operation()
except Exception as e:
    capture_error(e, event)  # Stores in ERRORS partition of admin table
    raise
```

## Configuration (backend/common/config.py)

The `Config` class reads from environment variables set by SAM:

```python
from common.config import Config

Config.MAIN_TABLE          # "wos-main-dev" or "wos-main-live"
Config.ADMIN_TABLE         # "wos-admin-dev" or "wos-admin-live"
Config.REFERENCE_TABLE     # "wos-reference-dev" or "wos-reference-live"
Config.USER_POOL_ID        # Cognito pool ID
Config.STAGE               # "dev" or "live"
Config.ANTHROPIC_API_KEY   # From Secrets Manager
Config.OPENAI_API_KEY      # From Secrets Manager
Config.is_production()     # True when STAGE == "live"
```

## Pydantic Models (backend/common/models.py)

Entities use Pydantic v2 with DynamoDB serialization:

```python
from common.models import UserRole, SpendingProfile, PriorityFocus, AllianceRole

# Key enums
UserRole.admin / UserRole.user
SpendingProfile.f2p / .minnow / .dolphin / .orca / .whale
PriorityFocus.svs_combat / .balanced_growth / .economy_focus
AllianceRole.rally_lead / .filler / .farmer / .casual
```

Models provide `to_dynamo()` and `from_dynamo()` methods for serialization.

## SAM Template (infra/template.yaml)

Adding a new Lambda function:

```yaml
# 1. Define the function
NewFunction:
  Type: AWS::Serverless::Function
  Properties:
    Handler: handlers/new.handler
    CodeUri: ../backend
    Description: New feature handler
    Events:
      GetResource:
        Type: HttpApi
        Properties:
          ApiId: !Ref HttpApi
          Path: /resource
          Method: GET
      PostResource:
        Type: HttpApi
        Properties:
          ApiId: !Ref HttpApi
          Path: /resource
          Method: POST
    Policies:
      - DynamoDBCrudPolicy:
          TableName: !Ref MainTable
```

Key SAM resources:
- `HttpApi` - API Gateway HTTP API (v2)
- `MainTable`, `AdminTable`, `ReferenceTable` - DynamoDB tables
- `UserPool`, `UserPoolClient` - Cognito authentication
- `CommonLayer` - Shared Python code layer
- `AppSecrets` - Secrets Manager for API keys
- `FrontendBucket`, `FrontendDistribution` - S3 + CloudFront

## CRITICAL Rules

### 1. Data File Sync
Two copies of game data must stay in sync:
- `data/heroes.json` (source of truth, used by scripts)
- `backend/data/heroes.json` (bundled with Lambda)

After modifying heroes.json, ALWAYS copy to both locations.

### 2. DynamoDB Dict Gotcha
Items from DynamoDB are plain Python dicts, NOT model instances:
```python
# CORRECT
hero_level = user_hero.get("level", 1)

# WRONG - getattr on dict always returns default
hero_level = getattr(user_hero, "level", 1)  # BUG: always returns 1
```

### 3. Decimal Handling
DynamoDB stores numbers as Decimal. Always use db.py helpers:
```python
# Writing: prepare_item() converts int/float to Decimal
put_item(table, prepare_item({"PK": "...", "SK": "...", "level": 45}))

# Reading: from_decimal() converts back
item = from_decimal(get_item(table, pk, sk))
```

### 4. None Values
DynamoDB rejects None values. Always strip them:
```python
# prepare_item() handles this automatically
# But if building items manually:
from common.db import strip_none
clean_item = strip_none({"name": "test", "optional": None})
# Result: {"name": "test"}
```

### 5. UTF-8 Encoding
All JSON file reads must use `encoding='utf-8'`:
```python
with open(filepath, encoding='utf-8') as f:
    data = json.load(f)
```

### 6. Secrets
API keys come from AWS Secrets Manager, loaded at cold start in `config.py`.
NEVER hardcode secrets. NEVER log full API keys.

## AI Integration (backend/engine/ai_recommender.py)

The AI recommender supports dual providers:
- **Primary**: Anthropic Claude (claude-sonnet-4-20250514)
- **Fallback**: OpenAI (gpt-4o-mini)

Key behaviors:
- Address users as "Chief" (game terminology)
- Use WoS vocabulary (Settlement, Furnace, Accelerators, etc.)
- One clarifying question max when uncertain
- Jailbreak protection: only answers WoS questions
- Rate limited per user (configurable via admin table)

## Testing Backend Changes

```bash
# Validate SAM template
cd /c/Users/adam/IdeaProjects/wos-optimizer/infra
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" validate

# Build backend
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" build

# Deploy to dev
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" deploy --no-confirm-changeset

# Check Lambda logs
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" logs tail /aws/lambda/wos-dev-HeroesFunction --follow --region us-east-1
```

## Workflow

1. **Understand the requirement** - What endpoint/feature is being built or modified?
2. **Check existing code** - Read handler and repo patterns for the relevant domain
3. **Implement changes** - Follow handler pattern, use db.py helpers, handle errors
4. **Sync data files** if heroes.json was modified
5. **Update SAM template** if adding new routes or resources
6. **Test** - Validate SAM template, build, deploy to dev
7. **Verify** - Check CloudWatch logs, test endpoint with curl
