"""Migrate existing users to AWS Cognito User Pool.

Reads users from PostgreSQL, creates each in Cognito via
admin_create_user(), and updates the DynamoDB user records
with the Cognito sub (unique user ID).

Usage:
    python scripts/setup_cognito_users.py \
        --db-url "postgresql://user:pass@host:5432/wos" \
        --user-pool-id us-east-1_XXXXXXXXX \
        --region us-east-1 \
        --stage dev

    # Preview without creating users:
    python scripts/setup_cognito_users.py --db-url "..." --user-pool-id "..." --dry-run
"""

import argparse
import json
import sys
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import User


# ---------------------------------------------------------------------------
# Cognito helpers
# ---------------------------------------------------------------------------

def create_cognito_user(
    cognito_client,
    user_pool_id: str,
    email: str,
    username: str,
    role: str = "user",
    is_test: bool = False,
) -> dict | None:
    """Create a user in Cognito and auto-confirm them.

    Returns the Cognito user record (with 'Sub' in Attributes), or None on error.
    """
    # Use email as the Cognito username for consistency
    cognito_username = email.lower() if email else username.lower()

    user_attributes = [
        {"Name": "email", "Value": email or f"{username}@migrated.local"},
        {"Name": "email_verified", "Value": "true"},
        {"Name": "custom:role", "Value": role},
    ]

    if is_test:
        user_attributes.append({"Name": "custom:is_test", "Value": "true"})

    try:
        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=cognito_username,
            UserAttributes=user_attributes,
            # Suppress welcome email -- users will reset password on first login
            MessageAction="SUPPRESS",
            # Set temporary password (users must reset on first login)
            TemporaryPassword=f"Migrate!{username[:8]}2026",
        )

        user_record = response.get("User", {})

        # Auto-confirm the user so they don't need email verification
        cognito_client.admin_confirm_sign_up(
            UserPoolId=user_pool_id,
            Username=cognito_username,
        )

        # Set permanent password status (force change on first login)
        # The temporary password flow handles this automatically, so
        # users will be prompted to set a new password on first login.

        return user_record

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "UsernameExistsException":
            # User already exists in Cognito -- look up their sub
            try:
                existing = cognito_client.admin_get_user(
                    UserPoolId=user_pool_id,
                    Username=cognito_username,
                )
                return existing
            except ClientError:
                print(f"    WARNING: User exists but could not fetch: {cognito_username}")
                return None
        else:
            print(f"    ERROR creating {cognito_username}: {error_code} - {e.response['Error']['Message']}")
            return None


def extract_sub(cognito_user: dict) -> str | None:
    """Extract the 'sub' (unique ID) from a Cognito user record."""
    attributes = cognito_user.get("Attributes", cognito_user.get("UserAttributes", []))
    for attr in attributes:
        if attr["Name"] == "sub":
            return attr["Value"]
    return None


# ---------------------------------------------------------------------------
# DynamoDB update helper
# ---------------------------------------------------------------------------

def update_dynamo_user_cognito_sub(
    dynamodb_table,
    user_pk: str,
    cognito_sub: str,
) -> bool:
    """Update a DynamoDB user record with the Cognito sub."""
    try:
        dynamodb_table.update_item(
            Key={"PK": user_pk, "SK": "METADATA"},
            UpdateExpression="SET cognito_sub = :sub",
            ExpressionAttributeValues={":sub": cognito_sub},
        )
        return True
    except ClientError as e:
        print(f"    ERROR updating DynamoDB {user_pk}: {e.response['Error']['Message']}")
        return False


# ---------------------------------------------------------------------------
# Main migration
# ---------------------------------------------------------------------------

def migrate_users_to_cognito(
    session,
    cognito_client,
    dynamodb_table,
    user_pool_id: str,
    id_mapping: dict,
    dry_run: bool,
) -> dict:
    """Create Cognito users and update DynamoDB records.

    Args:
        session: SQLAlchemy session connected to PostgreSQL.
        cognito_client: boto3 Cognito Identity Provider client.
        dynamodb_table: DynamoDB main table resource.
        user_pool_id: Cognito User Pool ID.
        id_mapping: Dict mapping old PG user IDs to new DynamoDB user IDs.
        dry_run: If True, preview without creating users.

    Returns:
        Dict with migration stats.
    """
    users = session.query(User).all()
    stats = {
        "total": len(users),
        "created": 0,
        "already_exists": 0,
        "skipped": 0,
        "errors": 0,
        "dynamo_updated": 0,
    }
    sub_mapping = {}

    print(f"\nProcessing {len(users)} users...\n")

    for i, user in enumerate(users, 1):
        email = user.email or ""
        username = user.username or ""
        role = user.role or "user"
        is_test = user.is_test_account or False

        # Skip users without email or username
        if not email and not username:
            print(f"  [{i}/{len(users)}] SKIP: No email or username (PG ID: {user.id})")
            stats["skipped"] += 1
            continue

        # If user already has a cognito_sub, skip creation
        if user.cognito_sub:
            print(f"  [{i}/{len(users)}] EXISTING: {email or username} -> {user.cognito_sub}")
            sub_mapping[str(user.id)] = user.cognito_sub
            stats["already_exists"] += 1
            continue

        display = email or username
        dynamo_uid = id_mapping.get(str(user.id), "")

        if dry_run:
            print(f"  [{i}/{len(users)}] WOULD CREATE: {display} (role={role}, test={is_test})")
            stats["created"] += 1
            continue

        # Create in Cognito
        cognito_user = create_cognito_user(
            cognito_client=cognito_client,
            user_pool_id=user_pool_id,
            email=email,
            username=username,
            role=role,
            is_test=is_test,
        )

        if cognito_user is None:
            stats["errors"] += 1
            continue

        cognito_sub = extract_sub(cognito_user)
        if not cognito_sub:
            print(f"    WARNING: No sub returned for {display}")
            stats["errors"] += 1
            continue

        sub_mapping[str(user.id)] = cognito_sub
        stats["created"] += 1
        print(f"  [{i}/{len(users)}] CREATED: {display} -> {cognito_sub}")

        # Update DynamoDB user record with Cognito sub
        if dynamo_uid and dynamodb_table:
            user_pk = f"USER#{dynamo_uid}"
            if update_dynamo_user_cognito_sub(dynamodb_table, user_pk, cognito_sub):
                stats["dynamo_updated"] += 1

        # Rate limit: Cognito has API throttling limits
        if i % 10 == 0:
            time.sleep(0.5)

    return stats, sub_mapping


def main():
    parser = argparse.ArgumentParser(
        description="Migrate PostgreSQL users to Cognito User Pool."
    )
    parser.add_argument("--db-url", required=True,
                        help="PostgreSQL connection URL")
    parser.add_argument("--user-pool-id", required=True,
                        help="Cognito User Pool ID (e.g. us-east-1_AbCdEfGhI)")
    parser.add_argument("--region", default="us-east-1",
                        help="AWS region (default: us-east-1)")
    parser.add_argument("--stage", choices=["dev", "live"], default="dev",
                        help="Target stage for DynamoDB table names")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without creating Cognito users")
    parser.add_argument("--id-mapping-file",
                        help="Path to id_mapping JSON from migrate_data.py (optional)")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"WoS Cognito User Migration")
    print(f"{'='*60}")
    print(f"Source:       {args.db_url.split('@')[-1] if '@' in args.db_url else args.db_url}")
    print(f"User Pool:    {args.user_pool_id}")
    print(f"Region:       {args.region}")
    print(f"Stage:        {args.stage}")
    print(f"Dry run:      {args.dry_run}")
    print(f"{'='*60}")

    # ---- Load ID mapping if provided ----
    id_mapping = {}
    if args.id_mapping_file:
        mapping_path = Path(args.id_mapping_file)
        if mapping_path.exists():
            with open(mapping_path, encoding="utf-8") as f:
                data = json.load(f)
            id_mapping = data.get("users", {})
            print(f"\nLoaded ID mapping: {len(id_mapping)} user mappings")
        else:
            print(f"\nWARNING: ID mapping file not found: {args.id_mapping_file}")
    else:
        # Try default location from migrate_data.py
        default_path = PROJECT_ROOT / "scripts" / f"id_mapping_{args.stage}.json"
        if default_path.exists():
            with open(default_path, encoding="utf-8") as f:
                data = json.load(f)
            id_mapping = data.get("users", {})
            print(f"\nLoaded ID mapping from {default_path}: {len(id_mapping)} user mappings")

    # ---- Connect to PostgreSQL ----
    engine = create_engine(args.db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # ---- Connect to AWS ----
    cognito_client = boto3.client("cognito-idp", region_name=args.region)

    # Connect to DynamoDB main table for updating cognito_sub
    dynamodb = boto3.resource("dynamodb", region_name=args.region)
    main_table_name = f"wos-main-{args.stage}"
    dynamodb_table = None

    if not args.dry_run and id_mapping:
        try:
            dynamodb_table = dynamodb.Table(main_table_name)
            dynamodb_table.table_status  # Verify access
            print(f"DynamoDB table: {main_table_name} (will update cognito_sub)")
        except Exception as e:
            print(f"WARNING: Could not access {main_table_name}: {e}")
            print("  Cognito users will be created but DynamoDB records will not be updated.")
            dynamodb_table = None

    # ---- Verify User Pool ----
    if not args.dry_run:
        try:
            pool_info = cognito_client.describe_user_pool(UserPoolId=args.user_pool_id)
            pool_name = pool_info["UserPool"]["Name"]
            print(f"User Pool:  {pool_name} ({args.user_pool_id})")
        except ClientError as e:
            print(f"\nERROR: Could not access User Pool '{args.user_pool_id}'.")
            print(f"  Error: {e.response['Error']['Message']}")
            sys.exit(1)

    # ---- Run migration ----
    try:
        stats, sub_mapping = migrate_users_to_cognito(
            session=session,
            cognito_client=cognito_client,
            dynamodb_table=dynamodb_table,
            user_pool_id=args.user_pool_id,
            id_mapping=id_mapping,
            dry_run=args.dry_run,
        )

        # Print summary
        print(f"\n{'='*60}")
        print(f"Migration Summary")
        print(f"{'='*60}")
        print(f"  Total users:      {stats['total']}")
        print(f"  Created:          {stats['created']}")
        print(f"  Already existed:  {stats['already_exists']}")
        print(f"  Skipped:          {stats['skipped']}")
        print(f"  Errors:           {stats['errors']}")
        if not args.dry_run:
            print(f"  DynamoDB updated: {stats['dynamo_updated']}")
        print(f"{'='*60}")

        # Save sub mapping for reference
        if sub_mapping:
            mapping_file = PROJECT_ROOT / "scripts" / f"cognito_mapping_{args.stage}.json"
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(sub_mapping, f, indent=2)
            print(f"\nCognito sub mapping saved to: {mapping_file}")

    except Exception as e:
        print(f"\nERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
