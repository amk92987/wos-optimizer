---
name: wos-db-manage
description: Manage DynamoDB tables, run queries, perform data migrations, and debug data integrity issues. Use when database schema changes, data migrations are needed, or debugging data problems.
allowed-tools: Bash, Read, Glob, Grep
---

# WoS Database Management - DynamoDB Operations & Migrations

## Purpose
Helps with DynamoDB table operations including querying data, performing migrations, validating data integrity, and debugging data issues across the 3-table single-table design.

## When to Use
- Querying DynamoDB data for debugging
- Performing data migrations or schema changes
- Validating data integrity across tables
- Backing up or restoring data
- Understanding the PK/SK key structure
- Debugging data access issues in Lambda handlers

## Environment Setup

### Table Names by Environment

| Table | Dev | Live |
|-------|-----|------|
| Main | `wos-main-dev` | `wos-main-live` |
| Admin | `wos-admin-dev` | `wos-admin-live` |
| Reference | `wos-reference-dev` | `wos-reference-live` |

### AWS CLI Paths (Windows)
```
AWS CLI: "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
Region: us-east-1
```

### Important: ALWAYS specify --region us-east-1 with AWS CLI commands.

## Table Design

### Main Table (`wos-main-{env}`)
User data, profiles, heroes, AI conversations, threads, notifications.

| Entity | PK | SK | Description |
|--------|----|----|-------------|
| User | `USER#{cognito_sub}` | `PROFILE` | User profile metadata |
| Game Profile | `USER#{cognito_sub}` | `GAME_PROFILE#{profile_id}` | Game account profile |
| User Hero | `USER#{cognito_sub}` | `HERO#{profile_id}#{hero_name}` | Owned hero with stats |
| Chief Data | `USER#{cognito_sub}` | `CHIEF#{profile_id}` | Chief gear, charms |
| AI Conversation | `USER#{cognito_sub}` | `CONVERSATION#{ulid}` | AI advisor history |
| Thread | `USER#{cognito_sub}` | `THREAD#{thread_id}` | Conversation thread |
| Thread Message | `USER#{cognito_sub}` | `MSG#{thread_id}#{ulid}` | Messages within thread |
| Notification | `USER#{cognito_sub}` | `NOTIFICATION#{ulid}` | User notifications |

### Admin Table (`wos-admin-{env}`)
Feature flags, AI settings, audit logs, feedback, metrics, announcements.

| Entity | PK | SK | Description |
|--------|----|----|-------------|
| Feature Flag | `FLAGS` | `FLAG#{flag_name}` | Feature toggle |
| AI Settings | `AI_SETTINGS` | `GLOBAL` | AI mode, rate limits |
| Audit Log | `AUDIT` | `LOG#{timestamp}#{ulid}` | Action tracking |
| Feedback | `FEEDBACK` | `ITEM#{ulid}` | User feedback items |
| Announcement | `ANNOUNCEMENTS` | `ITEM#{ulid}` | System announcements |
| Metrics | `METRICS` | `{metric_type}#{date}` | Usage analytics |
| Error Log | `ERRORS` | `ERR#{ulid}` | Captured errors |

### Reference Table (`wos-reference-{env}`)
Static game data (heroes, items).

| Entity | PK | SK | Description |
|--------|----|----|-------------|
| Hero Reference | `HEROES` | `HERO#{hero_name}` | Static hero data |
| Item Reference | `ITEMS` | `ITEM#{item_name}` | Backpack item data |

## Common Queries

### Query a User's Profile
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query \
  --table-name wos-main-dev \
  --key-condition-expression "PK = :pk AND SK = :sk" \
  --expression-attribute-values '{":pk":{"S":"USER#abc123"},":sk":{"S":"PROFILE"}}' \
  --region us-east-1
```

### Query All Heroes for a User
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query \
  --table-name wos-main-dev \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{":pk":{"S":"USER#abc123"},":sk":{"S":"HERO#"}}' \
  --region us-east-1
```

### Scan All Users (limited)
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb scan \
  --table-name wos-main-dev \
  --filter-expression "SK = :sk" \
  --expression-attribute-values '{":sk":{"S":"PROFILE"}}' \
  --region us-east-1 \
  --max-items 20
```

### Get All Feature Flags
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query \
  --table-name wos-admin-dev \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{":pk":{"S":"FLAGS"},":sk":{"S":"FLAG#"}}' \
  --region us-east-1
```

### Get All Hero Reference Data
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query \
  --table-name wos-reference-dev \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"HEROES"}}' \
  --region us-east-1
```

### Get Recent Errors
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query \
  --table-name wos-admin-dev \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{":pk":{"S":"ERRORS"},":sk":{"S":"ERR#"}}' \
  --region us-east-1 \
  --scan-index-forward false \
  --limit 10
```

### Get Recent Feedback
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query \
  --table-name wos-admin-dev \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{":pk":{"S":"FEEDBACK"},":sk":{"S":"ITEM#"}}' \
  --region us-east-1 \
  --scan-index-forward false
```

## Data Migration Patterns

### Adding a New Field to Existing Items

```bash
# Step 1: Scan for items that need the new field
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb scan \
  --table-name wos-main-dev \
  --filter-expression "SK = :sk AND attribute_not_exists(new_field)" \
  --expression-attribute-values '{":sk":{"S":"PROFILE"}}' \
  --region us-east-1

# Step 2: Update each item with the new field
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb update-item \
  --table-name wos-main-dev \
  --key '{"PK":{"S":"USER#abc123"},"SK":{"S":"PROFILE"}}' \
  --update-expression "SET new_field = :val" \
  --expression-attribute-values '{":val":{"S":"default_value"}}' \
  --region us-east-1
```

### Batch Migration Script Pattern
```python
# Use backend/common/db.py helpers for migrations
from common.db import main_table, query, update_item

# Query all items needing migration
items = query(main_table(), pk="USER#...", sk_begins_with="HERO#")

# Update each item
for item in items:
    update_item(
        main_table(),
        pk=item["PK"],
        sk=item["SK"],
        update_expression="SET new_field = :val",
        expression_values={":val": "default"},
    )
```

## Backup & Restore

### Export Table to JSON
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb scan \
  --table-name wos-main-dev \
  --region us-east-1 \
  --output json > backup_main_dev.json
```

### Point-in-Time Recovery
DynamoDB PITR is enabled via SAM template. To restore:
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb restore-table-to-point-in-time \
  --source-table-name wos-main-dev \
  --target-table-name wos-main-dev-restore \
  --use-latest-restorable-time \
  --region us-east-1
```

## Key Code References

### Data Access Layer
| File | Purpose |
|------|---------|
| `backend/common/db.py` | DynamoDB CRUD helpers (get_item, query, put_item, update_item, etc.) |
| `backend/common/models.py` | Pydantic v2 models with to_dynamo() / from_dynamo() |
| `backend/common/config.py` | Table name configuration from environment |
| `backend/common/hero_repo.py` | Hero data access (CRUD + reference) |
| `backend/common/profile_repo.py` | Profile data access |
| `backend/common/chief_repo.py` | Chief gear/charm data access |
| `backend/common/user_repo.py` | User account data access |
| `backend/common/admin_repo.py` | Admin table data access (flags, feedback, etc.) |
| `backend/common/ai_repo.py` | AI conversation data access |

### CRITICAL: DynamoDB Dict Gotcha
When working with DynamoDB items returned from queries, items are Python `dict` objects, NOT ORM model instances:
```python
# CORRECT - use isinstance() and .get()
if isinstance(user_hero, dict):
    level = user_hero.get("level", 1)

# WRONG - getattr() doesn't work on plain dicts
level = getattr(user_hero, "level", 1)  # Always returns 1!
```

### Serialization Helpers (from db.py)
- `prepare_item(dict)` - Strip None values + convert to Decimal before write
- `from_decimal(item)` - Convert Decimal back to int/float after read
- `strip_none(dict)` - Remove None keys (DynamoDB rejects None)
- `to_decimal(value)` - Convert numeric types to Decimal

## Data Integrity Checks

### Verify User-Hero Consistency
```bash
# Count heroes per user profile
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query \
  --table-name wos-main-dev \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{":pk":{"S":"USER#abc123"},":sk":{"S":"HERO#"}}' \
  --select COUNT \
  --region us-east-1
```

### Verify Reference Data Loaded
```bash
"C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb scan \
  --table-name wos-reference-dev \
  --select COUNT \
  --region us-east-1
```

### Seed Reference Data
```bash
cd C:\Users\adam\IdeaProjects\wos-optimizer
.venv\Scripts\python.exe scripts/seed_reference_data.py
```

## Safety Rules

1. **ALWAYS operate on dev tables first** - Test migrations on `wos-main-dev` before `wos-main-live`
2. **NEVER delete production data** without explicit confirmation from the user
3. **ALWAYS back up** before destructive operations on live tables
4. **Use conditional writes** (`attribute_not_exists`, `attribute_exists`) to prevent overwrites
5. **Batch writes are limited to 25 items** - Use batch_writer for larger sets
6. **Scan operations are expensive** - Always prefer query with PK over scan
7. **Check item counts** before and after migrations to verify correctness

## Workflow

1. **Identify the operation** - Query, migration, backup, or integrity check
2. **Determine the environment** - Dev or Live (default to Dev)
3. **Construct the command** - Use AWS CLI or Python helpers
4. **Verify before executing** - Show the command and expected impact
5. **Execute and validate** - Run the operation, check results
6. **Report findings** - Summary of changes or query results
