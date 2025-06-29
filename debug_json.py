#!/usr/bin/env python3
"""Debug JSON extraction and pattern matching."""

from sagittadb import SagittaDB


def debug_json_extraction():
    db = SagittaDB(":memory:")

    sample_docs = [
        {"name": "Alice", "age": 30},
        {"name": "Charlie", "age": 35},
        {"name": "Diana", "age": 28},
    ]

    db.insert_many(sample_docs)

    # Let's see what the raw SQL query returns
    with db._transaction() as conn:
        # Test the JSON extraction
        cursor = conn.execute("SELECT json_extract(data, '$.name') FROM documents")
        names = cursor.fetchall()
        print("Extracted names:")
        for name in names:
            print(f"  - '{name[0]}'")

        # Test the REGEXP function directly
        cursor = conn.execute(
            "SELECT json_extract(data, '$.name') FROM documents WHERE json_extract(data, '$.name') REGEXP 'a.*'"
        )
        matching_names = cursor.fetchall()
        print("\nNames matching 'a.*' pattern:")
        for name in matching_names:
            print(f"  - '{name[0]}'")

        # Test Python regex on the same strings
        import re

        print("\nPython regex test:")
        for name_tuple in names:
            name = name_tuple[0]
            matches = re.search("a.*", name) is not None
            print(f"  - '{name}' matches 'a.*': {matches}")

    db.close()


if __name__ == "__main__":
    debug_json_extraction()
