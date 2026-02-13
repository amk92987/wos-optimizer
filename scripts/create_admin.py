"""Create the first admin user after a fresh SAM deployment.

Solves the bootstrap problem: you need to be admin to create an admin,
but after a fresh deploy there are no admins.

Usage:
    python scripts/create_admin.py --stage live --email adamkirschner@outlook.com
    python scripts/create_admin.py --stage dev  --email adamkirschner@outlook.com

Prerequisites:
    - SAM stack deployed (Cognito pool + DynamoDB tables exist)
    - AWS credentials configured (aws configure)
    - pip install boto3
"""

import argparse
import getpass
import json
import sys
from datetime import datetime, timezone

import boto3


def get_stack_outputs(stack_name: str, region: str) -> dict:
    """Get CloudFormation stack outputs as a dict."""
    cf = boto3.client("cloudformation", region_name=region)
    try:
        resp = cf.describe_stacks(StackName=stack_name)
    except cf.exceptions.ClientError as e:
        print(f"Error: Stack '{stack_name}' not found. Is it deployed?")
        sys.exit(1)
    outputs = resp["Stacks"][0].get("Outputs", [])
    return {o["OutputKey"]: o["OutputValue"] for o in outputs}


def create_admin(stage: str, email: str, password: str, region: str = "us-east-1"):
    stack_name = f"wos-{stage}"
    print(f"\nLooking up stack: {stack_name}")

    outputs = get_stack_outputs(stack_name, region)
    pool_id = outputs.get("UserPoolId")
    table_name = outputs.get("MainTableName")

    if not pool_id:
        print("Error: UserPoolId not found in stack outputs.")
        print("  (If using a shared Cognito pool, pass --pool-id manually)")
        sys.exit(1)
    if not table_name:
        print("Error: MainTableName not found in stack outputs.")
        sys.exit(1)

    print(f"  Cognito Pool: {pool_id}")
    print(f"  DynamoDB Table: {table_name}")

    cognito = boto3.client("cognito-idp", region_name=region)
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)

    # --- Step 1: Create Cognito user ---
    print(f"\nCreating Cognito user: {email}")
    try:
        cognito.admin_create_user(
            UserPoolId=pool_id,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
            MessageAction="SUPPRESS",
        )
        print("  Cognito user created.")
    except cognito.exceptions.UsernameExistsException:
        print("  Cognito user already exists, continuing.")

    # Set permanent password
    cognito.admin_set_user_password(
        UserPoolId=pool_id,
        Username=email,
        Password=password,
        Permanent=True,
    )
    print("  Password set.")

    # Get the Cognito sub (user ID)
    resp = cognito.admin_get_user(UserPoolId=pool_id, Username=email)
    sub = None
    for attr in resp.get("UserAttributes", []):
        if attr["Name"] == "sub":
            sub = attr["Value"]
            break
    if not sub:
        print("Error: Could not find Cognito sub for user.")
        sys.exit(1)
    print(f"  Cognito sub: {sub}")

    # --- Step 2: Create DynamoDB records ---
    now = datetime.now(timezone.utc).isoformat()
    user_item = {
        "PK": f"USER#{sub}",
        "SK": "METADATA",
        "entity_type": "USER",
        "user_id": sub,
        "email": email,
        "username": email,
        "password_hash": "",
        "role": "admin",
        "theme": "dark",
        "is_active": True,
        "is_verified": True,
        "is_test_account": False,
        "ai_requests_today": 0,
        "ai_access_level": "unlimited",
        "created_at": now,
        "updated_at": now,
    }

    email_guard = {
        "PK": "UNIQUE#EMAIL",
        "SK": email.lower(),
        "user_id": sub,
    }

    username_guard = {
        "PK": "UNIQUE#USERNAME",
        "SK": email.lower(),
        "user_id": sub,
    }

    print(f"\nWriting DynamoDB records to {table_name}")
    client = boto3.client("dynamodb", region_name=region)
    try:
        client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": boto3.dynamodb.types.TypeSerializer().serialize(user_item)["M"],
                        "ConditionExpression": "attribute_not_exists(PK)",
                    }
                },
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": boto3.dynamodb.types.TypeSerializer().serialize(email_guard)["M"],
                    }
                },
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": boto3.dynamodb.types.TypeSerializer().serialize(username_guard)["M"],
                    }
                },
            ]
        )
        print("  User record created (admin role).")
        print("  Email uniqueness guard created.")
        print("  Username uniqueness guard created.")
    except client.exceptions.TransactionCanceledException:
        print("  User already exists in DynamoDB. Updating role to admin...")
        table.update_item(
            Key={"PK": f"USER#{sub}", "SK": "METADATA"},
            UpdateExpression="SET #role = :role, updated_at = :now",
            ExpressionAttributeNames={"#role": "role"},
            ExpressionAttributeValues={":role": "admin", ":now": now},
        )
        print("  Role updated to admin.")

    print(f"\n{'=' * 50}")
    print(f"  Admin account ready!")
    print(f"  Email: {email}")
    print(f"  Stage: {stage}")
    print(f"  Login at the app and use these credentials.")
    print(f"{'=' * 50}\n")


def main():
    parser = argparse.ArgumentParser(description="Create first admin user after fresh deploy")
    parser.add_argument("--stage", required=True, choices=["dev", "live"], help="Which environment")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--pool-id", default=None, help="Override Cognito pool ID (for shared pools)")
    args = parser.parse_args()

    password = getpass.getpass(f"Set password for {args.email}: ")
    if len(password) < 6:
        print("Error: Password must be at least 6 characters.")
        sys.exit(1)

    create_admin(args.stage, args.email, password, args.region)


if __name__ == "__main__":
    main()
