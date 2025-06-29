"""
Basic Usage Example for SagittaDB

This example demonstrates the fundamental operations of SagittaDB:
- Creating a database
- Inserting documents
- Searching and filtering
- Updating and removing documents
"""

from sagittadb import SagittaDB
from pathlib import Path


def main():
    # Create or connect to a database file
    db_path = Path("example_basic.db")
    db = SagittaDB(db_path)

    print("🏹 SagittaDB Basic Usage Example")
    print("=" * 40)

    # Clear any existing data for this example
    db.purge()
    print("Database cleared for fresh start")

    # 1. Insert a single document
    print("\n1. Inserting a single document...")
    user_id = db.insert(
        {
            "name": "Alice Johnson",
            "age": 30,
            "email": "alice@example.com",
            "department": "Engineering",
            "skills": ["Python", "JavaScript", "SQL"],
        }
    )
    print(f"Inserted user with ID: {user_id}")

    # 2. Insert multiple documents
    print("\n2. Inserting multiple documents...")
    users = [
        {
            "name": "Bob Smith",
            "age": 25,
            "email": "bob@example.com",
            "department": "Design",
            "skills": ["Figma", "Photoshop", "UI/UX"],
        },
        {
            "name": "Carol Davis",
            "age": 35,
            "email": "carol@example.com",
            "department": "Engineering",
            "skills": ["Python", "Docker", "Kubernetes"],
        },
        {
            "name": "David Wilson",
            "age": 28,
            "email": "david@example.com",
            "department": "Marketing",
            "skills": ["SEO", "Content Writing", "Analytics"],
        },
    ]

    db.insert_many(users)
    print(f"Inserted {len(users)} additional users")

    # 3. Count total documents
    print(f"\n3. Total documents in database: {db.count()}")

    # 4. Retrieve all documents
    print("\n4. All documents:")
    for i, doc in enumerate(db.all(), 1):
        print(f"   {i}. {doc['name']} ({doc['department']})")

    # 5. Search by department
    print("\n5. Engineering department employees:")
    engineering_users = list(db.search({"department": "Engineering"}))
    for user in engineering_users:
        print(f"   - {user['name']}, age {user['age']}")

    # 6. Search with pattern matching (regex)
    print("\n6. Users with email ending in 'example.com':")
    example_users = list(db.search_pattern("email", r".*@example\.com$"))
    for user in example_users:
        print(f"   - {user['name']}: {user['email']}")

    # 7. Find users by multiple ages
    print("\n7. Users aged 25 or 30:")
    young_users = list(db.find_any("age", [25, 30]))
    for user in young_users:
        print(f"   - {user['name']}, age {user['age']}")

    # 8. Update a document
    print("\n8. Updating Alice's age...")
    updated_count = db.update(
        {"name": "Alice Johnson"}, {"age": 31, "last_updated": "2025-06-29"}
    )
    print(f"Updated {updated_count} document(s)")

    # Verify the update
    alice = list(db.search({"name": "Alice Johnson"}))[0]
    print(f"   Alice's new age: {alice['age']}")

    # 9. Count documents with filter
    print(
        f"\n9. Engineering department count: {db.count({'department': 'Engineering'})}"
    )

    # 10. Remove a document
    print("\n10. Removing David from the database...")
    removed_count = db.remove({"name": "David Wilson"})
    print(f"Removed {removed_count} document(s)")

    # Final count
    print(f"\nFinal document count: {db.count()}")

    # Close the database connection
    db.close()
    print("\nDatabase connection closed.")
    print(f"Data saved to: {db_path.absolute()}")


if __name__ == "__main__":
    main()
