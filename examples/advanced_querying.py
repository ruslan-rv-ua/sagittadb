"""
Advanced Querying Example for SagittaDB

This example demonstrates advanced querying capabilities:
- Complex filtering
- Pagination with limit and offset
- Pattern matching with regex
- Index creation for performance
- Working with nested data structures
"""

import time
from pathlib import Path

from sagittadb import SagittaDB


def main():
    # Create database
    db_path = Path("example_advanced.db")
    db = SagittaDB(db_path)

    print("🏹 SagittaDB Advanced Querying Example")
    print("=" * 45)

    # Clear existing data
    db.purge()

    # Create sample data - a product catalog
    print("Setting up product catalog...")
    products = [
        {
            "name": "Laptop Pro 15",
            "category": "Electronics",
            "subcategory": "Computers",
            "price": 1299.99,
            "brand": "TechCorp",
            "specs": {"cpu": "Intel i7", "ram": "16GB", "storage": "512GB SSD"},
            "tags": ["business", "gaming", "professional"],
            "in_stock": True,
            "rating": 4.5,
            "reviews_count": 234,
        },
        {
            "name": "Wireless Mouse",
            "category": "Electronics",
            "subcategory": "Accessories",
            "price": 29.99,
            "brand": "TechCorp",
            "specs": {"connection": "Bluetooth", "battery_life": "6 months"},
            "tags": ["office", "wireless"],
            "in_stock": True,
            "rating": 4.2,
            "reviews_count": 89,
        },
        {
            "name": "Gaming Chair",
            "category": "Furniture",
            "subcategory": "Office",
            "price": 299.99,
            "brand": "ComfortPlus",
            "specs": {"material": "Leather", "adjustable": True},
            "tags": ["gaming", "office", "ergonomic"],
            "in_stock": False,
            "rating": 4.7,
            "reviews_count": 156,
        },
        {
            "name": "4K Monitor",
            "category": "Electronics",
            "subcategory": "Displays",
            "price": 399.99,
            "brand": "DisplayMax",
            "specs": {
                "resolution": "3840x2160",
                "size": "27 inches",
                "refresh_rate": "60Hz",
            },
            "tags": ["professional", "design", "4k"],
            "in_stock": True,
            "rating": 4.6,
            "reviews_count": 312,
        },
        {
            "name": "Mechanical Keyboard",
            "category": "Electronics",
            "subcategory": "Accessories",
            "price": 129.99,
            "brand": "KeyMaster",
            "specs": {"switches": "Cherry MX Blue", "backlit": True},
            "tags": ["gaming", "typing", "professional"],
            "in_stock": True,
            "rating": 4.4,
            "reviews_count": 78,
        },
    ]

    # Insert products
    db.insert_many(products)
    print(f"Inserted {len(products)} products")

    # Create indexes for better performance
    print("\nCreating indexes for optimized queries...")
    db.create_index("category")
    db.create_index("price")
    db.create_index("brand")
    db.create_index("in_stock")
    print("Indexes created for: category, price, brand, in_stock")

    # 1. Basic filtering
    print("\n1. Electronics products:")
    electronics = list(db.search({"category": "Electronics"}))
    for product in electronics:
        print(f"   - {product['name']} (${product['price']})")

    # 2. Multi-field filtering
    print("\n2. In-stock Electronics:")
    in_stock_electronics = list(
        db.search({"category": "Electronics", "in_stock": True})
    )
    for product in in_stock_electronics:
        print(f"   - {product['name']} - {product['subcategory']}")

    # 3. Pattern matching for product names
    print("\n3. Products with 'Pro' in the name:")
    pro_products = list(db.search_pattern("name", r".*Pro.*"))
    for product in pro_products:
        print(f"   - {product['name']}")

    # 4. Find products by multiple brands
    print("\n4. TechCorp and KeyMaster products:")
    brand_products = list(db.find_any("brand", ["TechCorp", "KeyMaster"]))
    for product in brand_products:
        print(f"   - {product['name']} by {product['brand']}")

    # 5. Pagination example
    print("\n5. Pagination demo (2 products per page):")
    page_size = 2
    page = 0

    while True:
        offset = page * page_size
        page_products = list(db.all(limit=page_size, offset=offset))

        if not page_products:
            break

        print(f"   Page {page + 1}:")
        for product in page_products:
            print(f"     - {product['name']}")
        page += 1

    # 6. Complex pattern matching
    print("\n6. Products with email-like patterns in specs:")
    # This is a creative example - searching for products with '@' in any spec value
    # (Note: our sample data doesn't have this, but shows the capability)
    email_pattern_products = list(db.search_pattern("name", r".*@.*"))
    if email_pattern_products:
        for product in email_pattern_products:
            print(f"   - {product['name']}")
    else:
        print("   No products found with '@' in name (as expected)")

    # 7. Search for high-rated products using pattern
    print("\n7. Products with rating >= 4.5:")
    # Note: This is a demonstration - in practice, you'd want numeric comparison
    high_rated = []
    for product in db.all():
        if product["rating"] >= 4.5:
            high_rated.append(product)

    for product in high_rated:
        print(
            f"   - {product['name']}: {product['rating']} stars ({product['reviews_count']} reviews)"
        )

    # 8. Count products by category
    print("\n8. Product counts by category:")
    categories = set()
    for product in db.all():
        categories.add(product["category"])

    for category in sorted(categories):
        count = db.count({"category": category})
        print(f"   - {category}: {count} products")

    # 9. Performance demonstration
    print("\n9. Performance test with indexed vs non-indexed search:")

    # Time a search using indexed field
    start_time = time.time()
    electronics_count = db.count({"category": "Electronics"})
    indexed_time = time.time() - start_time

    print(
        f"   Indexed search (category): {electronics_count} results in {indexed_time:.6f}s"
    )

    # 10. Demonstrate limit and offset with search
    print("\n10. First 2 Electronics products (with offset):")
    first_two = list(db.search({"category": "Electronics"}, limit=2, offset=0))
    for i, product in enumerate(first_two, 1):
        print(f"   {i}. {product['name']}")

    print("\n    Next 2 Electronics products:")
    next_two = list(db.search({"category": "Electronics"}, limit=2, offset=2))
    for i, product in enumerate(next_two, 1):
        print(f"   {i + 2}. {product['name']}")

    # Clean up
    db.close()
    print(f"\nAdvanced querying complete. Data saved to: {db_path.absolute()}")


if __name__ == "__main__":
    main()
