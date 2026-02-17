"""DynamoDB client wrapper for serverless backend.

Provides a thin abstraction over boto3 DynamoDB resource with:
- Lazy-cached table references from environment config
- Helper methods for common operations (put, get, query, delete, batch, transact)
- Automatic serialization handling (Decimal, None filtering)
- Local DynamoDB support via AWS_SAM_LOCAL
"""

import logging
from decimal import Decimal
from typing import Any, Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from common.config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level cached resources
# ---------------------------------------------------------------------------
_dynamodb_resource = None
_tables: dict[str, Any] = {}

# Short alias -> Config attribute mapping for convenience
_TABLE_ALIASES: dict[str, str] = {
    "main": "MAIN_TABLE",
    "admin": "ADMIN_TABLE",
    "reference": "REFERENCE_TABLE",
}


def _get_resource():
    """Return a cached boto3 DynamoDB resource, creating it on first call."""
    global _dynamodb_resource
    if _dynamodb_resource is None:
        kwargs = {"region_name": Config.REGION}
        if Config.IS_LOCAL:
            kwargs["endpoint_url"] = "http://dynamodb:8000"
            logger.info("Using local DynamoDB endpoint")
        _dynamodb_resource = boto3.resource("dynamodb", **kwargs)
    return _dynamodb_resource


def get_table(table_name: str):
    """Return a cached DynamoDB Table reference.

    Accepts short aliases ('main', 'admin', 'reference') which are
    resolved to the actual table names from Config environment variables.
    Full table names are also accepted and used as-is.
    """
    # Resolve short alias to actual table name
    if table_name in _TABLE_ALIASES:
        table_name = getattr(Config, _TABLE_ALIASES[table_name])

    if table_name not in _tables:
        _tables[table_name] = _get_resource().Table(table_name)
    return _tables[table_name]


def get_tables() -> tuple:
    """Return (main_table, admin_table, reference_table) lazily cached."""
    return (
        get_table(Config.MAIN_TABLE),
        get_table(Config.ADMIN_TABLE),
        get_table(Config.REFERENCE_TABLE),
    )


def main_table():
    """Shortcut for the main application table."""
    return get_table(Config.MAIN_TABLE)


def admin_table():
    """Shortcut for the admin table."""
    return get_table(Config.ADMIN_TABLE)


def reference_table():
    """Shortcut for the reference/game-data table."""
    return get_table(Config.REFERENCE_TABLE)


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def strip_none(item: dict) -> dict:
    """Remove keys with None values — DynamoDB does not accept None.

    Recursively strips None from nested dicts. Lists are preserved as-is
    (DynamoDB list type allows mixed content).
    """
    cleaned = {}
    for key, value in item.items():
        if value is None:
            continue
        if isinstance(value, dict):
            nested = strip_none(value)
            if nested:  # skip empty dicts too
                cleaned[key] = nested
        else:
            cleaned[key] = value
    return cleaned


def to_decimal(value) -> Any:
    """Convert Python numeric types to Decimal for DynamoDB.

    - int/float -> Decimal
    - dict -> recursively converted
    - list/tuple -> recursively converted
    - Everything else passes through unchanged.
    """
    if isinstance(value, float):
        # Use string conversion to avoid floating-point representation issues
        return Decimal(str(value))
    if isinstance(value, int) and not isinstance(value, bool):
        return Decimal(value)
    if isinstance(value, dict):
        return {k: to_decimal(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_decimal(v) for v in value]
    return value


def prepare_item(item: dict) -> dict:
    """Prepare a Python dict for DynamoDB: strip Nones and convert numerics."""
    return to_decimal(strip_none(item))


def from_decimal(item) -> Any:
    """Convert Decimals back to int/float for JSON-friendly output.

    Integers stay as int; fractional values become float.
    """
    if isinstance(item, Decimal):
        if item == item.to_integral_value():
            return int(item)
        return float(item)
    if isinstance(item, dict):
        return {k: from_decimal(v) for k, v in item.items()}
    if isinstance(item, list):
        return [from_decimal(v) for v in item]
    return item


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def put_item(table, item: dict, condition: Optional[str] = None, **kwargs) -> dict:
    """Write an item to the table, preparing it for DynamoDB first.

    Args:
        table: A DynamoDB Table resource.
        item: The item dict (will be serialized automatically).
        condition: Optional ConditionExpression string
            (e.g. 'attribute_not_exists(PK)' for create-only).
        **kwargs: Additional arguments passed to table.put_item().

    Returns:
        The raw DynamoDB response.

    Raises:
        ClientError: On conditional check failure or other DynamoDB errors.
    """
    params: dict[str, Any] = {"Item": prepare_item(item)}
    if condition:
        params["ConditionExpression"] = condition
    params.update(kwargs)
    return table.put_item(**params)


def get_item(table, pk: str, sk: str) -> Optional[dict]:
    """Fetch a single item by primary key.

    Returns:
        The item dict with Decimals converted, or None if not found.
    """
    response = table.get_item(Key={"PK": pk, "SK": sk})
    item = response.get("Item")
    return from_decimal(item) if item else None


def query(
    table,
    pk: str,
    sk_begins_with: Optional[str] = None,
    sk_between: Optional[tuple[str, str]] = None,
    sk_value: Optional[str] = None,
    index_name: Optional[str] = None,
    scan_forward: bool = True,
    limit: Optional[int] = None,
    filter_expression=None,
    projection: Optional[str] = None,
    **kwargs,
) -> list[dict]:
    """Query items by partition key with optional sort key conditions.

    Args:
        table: DynamoDB Table resource.
        pk: Partition key value.
        sk_begins_with: Sort key prefix filter.
        sk_between: Tuple of (low, high) for range query on SK.
        sk_value: Exact sort key match.
        index_name: GSI name if querying a secondary index.
        scan_forward: True for ascending, False for descending.
        limit: Maximum items to return.
        filter_expression: Optional boto3 filter expression.
        projection: Comma-separated projection expression.
        **kwargs: Additional arguments passed to table.query().

    Returns:
        List of item dicts with Decimals converted.
    """
    key_condition = Key("PK").eq(pk)

    if sk_value is not None:
        key_condition = key_condition & Key("SK").eq(sk_value)
    elif sk_begins_with is not None:
        key_condition = key_condition & Key("SK").begins_with(sk_begins_with)
    elif sk_between is not None:
        key_condition = key_condition & Key("SK").between(*sk_between)

    params: dict[str, Any] = {
        "KeyConditionExpression": key_condition,
        "ScanIndexForward": scan_forward,
    }

    if index_name:
        params["IndexName"] = index_name
    if limit:
        params["Limit"] = limit
    if filter_expression:
        params["FilterExpression"] = filter_expression
    if projection:
        params["ProjectionExpression"] = projection
    params.update(kwargs)

    # Paginate to collect all results
    items = []
    while True:
        response = table.query(**params)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key or (limit and len(items) >= limit):
            break
        params["ExclusiveStartKey"] = last_key

    return from_decimal(items[:limit] if limit else items)


def delete_item(table, pk: str, sk: str, condition: Optional[str] = None, **kwargs) -> dict:
    """Delete an item by primary key.

    Args:
        table: DynamoDB Table resource.
        pk: Partition key value.
        sk: Sort key value.
        condition: Optional ConditionExpression string.
        **kwargs: Additional arguments passed to table.delete_item().

    Returns:
        The raw DynamoDB response.
    """
    params: dict[str, Any] = {"Key": {"PK": pk, "SK": sk}}
    if condition:
        params["ConditionExpression"] = condition
    params.update(kwargs)
    return table.delete_item(**params)


def batch_write(table, items: list[dict]) -> None:
    """Write up to 25 items in a single batch.

    Items are prepared (None-stripped, Decimal-converted) automatically.
    Handles unprocessed items with automatic retries.

    Args:
        table: DynamoDB Table resource.
        items: List of item dicts to write.
    """
    prepared = [prepare_item(item) for item in items]

    with table.batch_writer() as writer:
        for item in prepared:
            writer.put_item(Item=item)


def batch_delete(table, keys: list[dict]) -> None:
    """Delete multiple items by key in a single batch.

    Args:
        table: DynamoDB Table resource.
        keys: List of key dicts, each with 'PK' and 'SK'.
    """
    with table.batch_writer() as writer:
        for key in keys:
            writer.delete_item(Key={"PK": key["PK"], "SK": key["SK"]})


def transact_write(items: list[dict]) -> dict:
    """Execute a DynamoDB TransactWriteItems operation.

    Provides all-or-nothing writes across one or more tables using
    Python-native types (not raw DynamoDB typed attributes). The resource
    client handles type serialization automatically.

    Args:
        items: List of transact item dicts. Each dict should have exactly
            one key from: 'Put', 'Delete', 'Update', 'ConditionCheck'.

            Example::

                [
                    {
                        "Put": {
                            "TableName": "WoS-Main",
                            "Item": {"PK": "USER#123", "SK": "PROFILE"},
                        }
                    },
                    {
                        "Delete": {
                            "TableName": "WoS-Main",
                            "Key": {"PK": "USER#123", "SK": "OLD"},
                        }
                    },
                ]

            Note: For 'Put' operations that need None-stripping and Decimal
            conversion, use ``transact_write_items()`` instead.

    Returns:
        The raw DynamoDB response.
    """
    client = _get_resource().meta.client
    return client.transact_write_items(TransactItems=items)


def transact_write_items(operations: list[dict]) -> dict:
    """Higher-level transact write using boto3 Table-style dicts.

    Each operation is a dict with one key: 'Put', 'Update', 'Delete', or
    'ConditionCheck'. Put items are automatically prepared (None-stripped,
    Decimal-converted). Type serialization is handled automatically by the
    DynamoDB resource client — do NOT pre-serialize with TypeSerializer.

    Example::

        transact_write_items([
            {
                "Put": {
                    "TableName": Config.MAIN_TABLE,
                    "Item": {"PK": "USER#123", "SK": "PROFILE", "name": "Ada"},
                }
            },
            {
                "Delete": {
                    "TableName": Config.MAIN_TABLE,
                    "Key": {"PK": "USER#123", "SK": "OLD_ITEM"},
                }
            },
        ])

    Returns:
        The raw DynamoDB response.
    """
    transact_items = []
    for op in operations:
        for action, params in op.items():
            built: dict[str, Any] = {"TableName": params["TableName"]}

            if action == "Put":
                built["Item"] = prepare_item(params["Item"])
            elif action in ("Delete", "ConditionCheck"):
                built["Key"] = params["Key"]
            elif action == "Update":
                built["Key"] = params["Key"]
                if "UpdateExpression" in params:
                    built["UpdateExpression"] = params["UpdateExpression"]
                if "ExpressionAttributeValues" in params:
                    built["ExpressionAttributeValues"] = to_decimal(
                        params["ExpressionAttributeValues"]
                    )
                if "ExpressionAttributeNames" in params:
                    built["ExpressionAttributeNames"] = params["ExpressionAttributeNames"]

            if "ConditionExpression" in params:
                built["ConditionExpression"] = params["ConditionExpression"]

            transact_items.append({action: built})

    client = _get_resource().meta.client
    return client.transact_write_items(TransactItems=transact_items)


def update_item(
    table,
    pk: str,
    sk: str,
    update_expression: str,
    expression_values: Optional[dict] = None,
    expression_names: Optional[dict] = None,
    condition: Optional[str] = None,
    return_values: str = "ALL_NEW",
    **kwargs,
) -> Optional[dict]:
    """Update an item with an UpdateExpression.

    Args:
        table: DynamoDB Table resource.
        pk: Partition key value.
        sk: Sort key value.
        update_expression: DynamoDB UpdateExpression string.
        expression_values: ExpressionAttributeValues (auto Decimal-converted).
        expression_names: ExpressionAttributeNames for reserved words.
        condition: Optional ConditionExpression string.
        return_values: What to return ('NONE', 'ALL_OLD', 'ALL_NEW', etc.).
        **kwargs: Additional arguments passed to table.update_item().

    Returns:
        The updated item dict (or None if return_values is 'NONE').
    """
    params: dict[str, Any] = {
        "Key": {"PK": pk, "SK": sk},
        "UpdateExpression": update_expression,
        "ReturnValues": return_values,
    }

    if expression_values:
        params["ExpressionAttributeValues"] = to_decimal(expression_values)
    if expression_names:
        params["ExpressionAttributeNames"] = expression_names
    if condition:
        params["ConditionExpression"] = condition
    params.update(kwargs)

    response = table.update_item(**params)
    item = response.get("Attributes")
    return from_decimal(item) if item else None
