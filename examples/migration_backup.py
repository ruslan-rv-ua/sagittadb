"""
Migration and Backup Example

This example demonstrates:
- Database migration between versions
- Data backup and restore operations
- Data transformation during migration
- Validation and integrity checks
"""

import json
import shutil
import time
from datetime import datetime

from sagittadb import SagittaDB


def create_legacy_database():
    """Create     print("Files created:")
    print("  - legacy_system.db (original data)")
    print("  - new_system.db (migrated data)")
    print("  - new_system_backup.db (backup copy)")
    print("  - new_system_backup_export.json (JSON export)")
    print("  - restored_system.db (restored from backup)")

    print("\n✅ Migration and backup procedures completed!") database with old schema"""

    print("Creating legacy database...")
    legacy_db = SagittaDB("legacy_system.db")
    legacy_db.purge()  # Clear any existing data

    # Old schema: simpler user records
    legacy_users = [
        {
            "id": 1,
            "username": "alice_j",
            "email": "alice@oldmail.com",
            "full_name": "Alice Johnson",
            "role": "admin",
            "created": "2024-01-15",
            "last_login": "2024-06-20",
        },
        {
            "id": 2,
            "username": "bob_smith",
            "email": "bob@oldmail.com",
            "full_name": "Bob Smith",
            "role": "user",
            "created": "2024-02-10",
            "last_login": "2024-06-25",
        },
        {
            "id": 3,
            "username": "carol_d",
            "email": "carol@oldmail.com",
            "full_name": "Carol Davis",
            "role": "moderator",
            "created": "2024-03-05",
            "last_login": "2024-06-28",
        },
    ]

    legacy_db.insert_many(legacy_users)

    # Old schema: simple product records
    legacy_products = [
        {
            "product_id": 101,
            "name": "Laptop Pro",
            "price": 1299.99,
            "category": "electronics",
            "stock": 25,
        },
        {
            "product_id": 102,
            "name": "Wireless Mouse",
            "price": 29.99,
            "category": "electronics",
            "stock": 100,
        },
        {
            "product_id": 103,
            "name": "Office Chair",
            "price": 199.99,
            "category": "furniture",
            "stock": 15,
        },
    ]

    legacy_db.insert_many(legacy_products)

    print(f"  Created legacy database with {legacy_db.count()} records")
    legacy_db.close()

    return len(legacy_users) + len(legacy_products)


def migrate_to_new_schema():
    """Migrate data from legacy database to new schema"""

    print("\nMigrating to new schema...")

    # Open legacy database
    legacy_db = SagittaDB("legacy_system.db")

    # Create new database with improved schema
    new_db = SagittaDB("new_system.db")
    new_db.purge()  # Clear any existing data

    # Create indexes for better performance
    new_db.create_index("entity_type")
    new_db.create_index("entity_id")
    new_db.create_index("status")

    migration_stats = {
        "users_migrated": 0,
        "products_migrated": 0,
        "transformation_errors": 0,
    }

    # Migrate users with schema transformation
    print("  Migrating users...")
    for record in legacy_db.all():
        if "username" in record:  # This is a user record
            try:
                # Transform to new schema
                new_user = {
                    "entity_type": "user",
                    "entity_id": record["id"],
                    "username": record["username"],
                    "email": record["email"],
                    "profile": {
                        "full_name": record["full_name"],
                        "display_name": record["full_name"].split()[
                            0
                        ],  # Extract first name
                        "bio": "",
                        "avatar_url": "",
                    },
                    "permissions": {
                        "role": record["role"],
                        "is_admin": record["role"] == "admin",
                        "can_moderate": record["role"] in ["admin", "moderator"],
                    },
                    "timestamps": {
                        "created_at": record["created"] + "T00:00:00Z",
                        "updated_at": datetime.now().isoformat(),
                        "last_login_at": record["last_login"] + "T00:00:00Z",
                    },
                    "status": "active",
                    "version": "2.0",
                }

                new_db.insert(new_user)
                migration_stats["users_migrated"] += 1

            except Exception as e:
                print(f"    Error migrating user {record.get('id', 'unknown')}: {e}")
                migration_stats["transformation_errors"] += 1

        elif "product_id" in record:  # This is a product record
            try:
                # Transform to new schema
                new_product = {
                    "entity_type": "product",
                    "entity_id": record["product_id"],
                    "basic_info": {
                        "name": record["name"],
                        "description": f"Quality {record['name']} from our {record['category']} collection",
                        "sku": f"SKU-{record['product_id']:06d}",
                        "brand": "House Brand",
                    },
                    "pricing": {
                        "base_price": record["price"],
                        "currency": "USD",
                        "tax_rate": 0.08,
                        "discount_eligible": True,
                    },
                    "inventory": {
                        "stock_quantity": record["stock"],
                        "reserved_quantity": 0,
                        "reorder_level": 10,
                        "warehouse_location": "A-01",
                    },
                    "categorization": {
                        "primary_category": record["category"].title(),
                        "tags": [record["category"], "featured"],
                        "searchable_terms": record["name"].lower().split(),
                    },
                    "timestamps": {
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": datetime.now().isoformat(),
                    },
                    "status": "active",
                    "version": "2.0",
                }

                new_db.insert(new_product)
                migration_stats["products_migrated"] += 1

            except Exception as e:
                print(
                    f"    Error migrating product {record.get('product_id', 'unknown')}: {e}"
                )
                migration_stats["transformation_errors"] += 1

    legacy_db.close()
    new_db.close()

    print("  Migration completed:")
    print(f"    Users migrated: {migration_stats['users_migrated']}")
    print(f"    Products migrated: {migration_stats['products_migrated']}")
    print(f"    Errors: {migration_stats['transformation_errors']}")

    return migration_stats


def backup_database(db_path, backup_path):
    """Create a backup of the database"""

    print(f"\nCreating backup: {backup_path}")

    # Method 1: File copy (fastest for complete backup)
    start_time = time.time()
    shutil.copy2(db_path, backup_path)
    copy_time = time.time() - start_time

    print(f"  File copy backup completed in {copy_time:.3f}s")

    # Method 2: JSON export (portable, human-readable)
    json_backup_path = backup_path.replace(".db", "_export.json")

    start_time = time.time()
    db = SagittaDB(db_path)

    backup_data = {
        "metadata": {
            "backup_date": datetime.now().isoformat(),
            "source_database": str(db_path),
            "record_count": db.count(),
            "backup_version": "1.0",
        },
        "records": list(db.all()),
    }

    with open(json_backup_path, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    db.close()
    json_time = time.time() - start_time

    print(f"  JSON export completed in {json_time:.3f}s")
    print("  Backup files created:")
    print(f"    Database copy: {backup_path}")
    print(f"    JSON export: {json_backup_path}")

    return backup_path, json_backup_path


def restore_from_backup(backup_path, restore_path):
    """Restore database from backup"""

    print(f"\nRestoring from backup: {backup_path}")

    if backup_path.endswith(".json"):
        # Restore from JSON export
        print("  Restoring from JSON export...")

        with open(backup_path, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        restored_db = SagittaDB(restore_path)
        restored_db.purge()  # Clear existing data

        # Restore metadata info
        metadata = backup_data.get("metadata", {})
        print(f"    Original backup date: {metadata.get('backup_date', 'unknown')}")
        print(f"    Original record count: {metadata.get('record_count', 'unknown')}")

        # Restore records
        records = backup_data.get("records", [])
        if records:
            restored_db.insert_many(records)

        print(f"    Restored {restored_db.count()} records")
        restored_db.close()

    else:
        # Simple file copy restore
        print("  Restoring from database file copy...")
        shutil.copy2(backup_path, restore_path)

        # Verify the restore
        restored_db = SagittaDB(restore_path)
        record_count = restored_db.count()
        restored_db.close()

        print(f"    Restored database with {record_count} records")


def validate_migration():
    """Validate the migration was successful"""

    print("\nValidating migration...")

    legacy_db = SagittaDB("legacy_system.db")
    new_db = SagittaDB("new_system.db")

    validation_results = {
        "legacy_count": legacy_db.count(),
        "new_count": new_db.count(),
        "data_integrity": True,
        "schema_compliance": True,
        "errors": [],
    }

    # Check record counts match
    if validation_results["legacy_count"] != validation_results["new_count"]:
        validation_results["data_integrity"] = False
        validation_results["errors"].append("Record count mismatch")

    # Check schema compliance
    required_fields = ["entity_type", "entity_id", "status", "version"]

    sample_records = list(new_db.all(limit=5))
    for record in sample_records:
        for field in required_fields:
            if field not in record:
                validation_results["schema_compliance"] = False
                validation_results["errors"].append(f"Missing required field: {field}")
                break

    # Check entity types
    entity_types = set()
    for record in new_db.all():
        entity_types.add(record.get("entity_type", "unknown"))

    expected_types = {"user", "product"}
    if not expected_types.issubset(entity_types):
        validation_results["schema_compliance"] = False
        validation_results["errors"].append("Missing expected entity types")

    legacy_db.close()
    new_db.close()

    print(f"  Legacy records: {validation_results['legacy_count']}")
    print(f"  New records: {validation_results['new_count']}")
    print(
        f"  Data integrity: {'✅ PASS' if validation_results['data_integrity'] else '❌ FAIL'}"
    )
    print(
        f"  Schema compliance: {'✅ PASS' if validation_results['schema_compliance'] else '❌ FAIL'}"
    )

    if validation_results["errors"]:
        print("  Validation errors:")
        for error in validation_results["errors"]:
            print(f"    - {error}")

    return validation_results


def main():
    print("🏹 SagittaDB Migration & Backup Example")
    print("=" * 42)

    # Step 1: Create legacy database
    legacy_count = create_legacy_database()

    # Step 2: Migrate to new schema
    migration_stats = migrate_to_new_schema()

    # Step 3: Validate migration
    validation = validate_migration()

    # Step 4: Create backups
    db_backup, json_backup = backup_database("new_system.db", "new_system_backup.db")

    # Step 5: Test restore
    restore_from_backup(json_backup, "restored_system.db")

    # Step 6: Verify restored database
    print("\nVerifying restored database...")
    restored_db = SagittaDB("restored_system.db")
    restored_count = restored_db.count()
    restored_db.close()

    print(f"  Restored database has {restored_count} records")

    # Summary
    print("\n📊 Migration & Backup Summary:")
    print(f"  Original legacy records: {legacy_count}")
    print(
        f"  Migrated records: {migration_stats['users_migrated'] + migration_stats['products_migrated']}"
    )
    print(f"  Migration errors: {migration_stats['transformation_errors']}")
    print(
        f"  Validation: {'PASSED' if validation['data_integrity'] and validation['schema_compliance'] else 'FAILED'}"
    )
    print(f"  Backup & restore: {'SUCCESSFUL' if restored_count > 0 else 'FAILED'}")

    print("\nFiles created:")
    print("  - legacy_system.db (original data)")
    print("  - new_system.db (migrated data)")
    print("  - new_system_backup.db (backup copy)")
    print("  - new_system_backup_export.json (JSON export)")
    print("  - restored_system.db (restored from backup)")

    print("\n✅ Migration and backup procedures completed!")


if __name__ == "__main__":
    main()
