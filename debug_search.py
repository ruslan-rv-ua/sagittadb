#!/usr/bin/env python3
"""Debug search pattern behavior."""

from sagittadb import SagittaDB


def debug_search_patterns():
    db = SagittaDB(":memory:")

    sample_docs = [
        {"name": "Alice", "age": 30, "city": "New York", "active": True},
        {"name": "Bob", "age": 25, "city": "Los Angeles", "active": False},
        {"name": "Charlie", "age": 35, "city": "Chicago", "active": True},
        {"name": "Diana", "age": 28, "city": "New York", "active": True},
        {"name": "Eve", "age": 32, "city": "Seattle", "active": False},
    ]

    db.insert_many(sample_docs)

    print("Testing pattern search behavior:")

    # Test lowercase 'a' pattern - should match 0
    results = list(db.search_pattern("name", "a.*"))
    print(f"Pattern 'a.*' matched {len(results)} names:")
    for r in results:
        print(f"  - {r['name']}")

    # Test uppercase 'A' pattern - should match 1 (Alice)
    results = list(db.search_pattern("name", "A.*"))
    print(f"\nPattern 'A.*' matched {len(results)} names:")
    for r in results:
        print(f"  - {r['name']}")

    # Test city pattern - should match New York and Los Angeles
    results = list(db.search_pattern("city", ".*o.*"))
    print(f"\nPattern '.*o.*' matched {len(results)} cities:")
    for r in results:
        print(f"  - {r['city']}")

    db.close()


if __name__ == "__main__":
    debug_search_patterns()
