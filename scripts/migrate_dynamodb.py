"""Migrate DynamoDB data from dev tables to live tables.

Usage:
    python scripts/migrate_dynamodb.py                    # dry-run (default)
    python scripts/migrate_dynamodb.py --execute          # actually copy data
    python scripts/migrate_dynamodb.py --tables main      # only main table
    python scripts/migrate_dynamodb.py --tables admin     # only admin table
    python scripts/migrate_dynamodb.py --tables main admin # both tables
"""

import argparse
import sys

import boto3

TABLE_MAP = {
    "main": ("wos-main-dev", "wos-main-live"),
    "admin": ("wos-admin-dev", "wos-admin-live"),
}


def scan_all(table):
    """Scan all items from a DynamoDB table, handling pagination."""
    items = []
    response = table.scan()
    items.extend(response["Items"])
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response["Items"])
    return items


def batch_write(table, items):
    """Write items to a DynamoDB table using batch_writer."""
    written = 0
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
            written += 1
    return written


def migrate(table_keys, dry_run=True):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    for key in table_keys:
        source_name, dest_name = TABLE_MAP[key]
        print(f"\n{'=' * 60}")
        print(f"  {source_name}  -->  {dest_name}")
        print(f"{'=' * 60}")

        source_table = dynamodb.Table(source_name)
        items = scan_all(source_table)
        print(f"  Scanned {len(items)} items from {source_name}")

        if not items:
            print("  Nothing to migrate.")
            continue

        if dry_run:
            print(f"  [DRY RUN] Would write {len(items)} items to {dest_name}")
            # Show a sample
            sample = items[0]
            pk = sample.get("PK", "?")
            sk = sample.get("SK", "?")
            print(f"  Sample item: PK={pk}, SK={sk}")
        else:
            dest_table = dynamodb.Table(dest_name)
            written = batch_write(dest_table, items)
            print(f"  Wrote {written} items to {dest_name}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Migrate DynamoDB data from dev to live")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write data (default is dry-run)",
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        choices=list(TABLE_MAP.keys()),
        default=list(TABLE_MAP.keys()),
        help="Which tables to migrate (default: all)",
    )
    args = parser.parse_args()

    if args.execute:
        print("*** EXECUTE MODE — data will be written to live tables ***")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(1)
    else:
        print("*** DRY RUN — no data will be written (use --execute to write) ***")

    migrate(args.tables, dry_run=not args.execute)


if __name__ == "__main__":
    main()
