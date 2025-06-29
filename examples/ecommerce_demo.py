"""
E-commerce Product Management Example

This example simulates a real-world e-commerce scenario with:
- Product inventory management
- Customer order tracking
- Sales analytics
- Bulk operations
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

from sagittadb import SagittaDB


def setup_sample_data(db):
    """Set up sample e-commerce data"""

    # Product categories and sample products
    categories = {
        "Electronics": [
            ("iPhone 15 Pro", 999.99, "Apple", 50),
            ("Samsung Galaxy S24", 849.99, "Samsung", 30),
            ("MacBook Air M3", 1299.99, "Apple", 25),
            ("Dell XPS 13", 1099.99, "Dell", 20),
            ("AirPods Pro", 249.99, "Apple", 100),
            ("Sony WH-1000XM5", 399.99, "Sony", 40),
        ],
        "Clothing": [
            ("Classic Blue Jeans", 79.99, "Denim Co", 200),
            ("Cotton T-Shirt", 19.99, "BasicWear", 500),
            ("Winter Jacket", 149.99, "OutdoorGear", 75),
            ("Running Shoes", 129.99, "SportsFoot", 120),
            ("Wool Sweater", 89.99, "CozyKnits", 80),
            ("Leather Boots", 199.99, "BootCraft", 45),
        ],
        "Home": [
            ("Coffee Maker", 89.99, "BrewMaster", 60),
            ("Vacuum Cleaner", 199.99, "CleanPro", 35),
            ("Desk Lamp", 49.99, "LightCorp", 90),
            ("Throw Pillow", 24.99, "HomeComfort", 150),
            ("Wall Clock", 39.99, "TimeKeepers", 70),
            ("Plant Pot", 15.99, "GreenThumb", 200),
        ],
    }

    products = []
    product_id = 1

    for category, items in categories.items():
        for name, price, brand, stock in items:
            products.append(
                {
                    "product_id": product_id,
                    "name": name,
                    "category": category,
                    "price": price,
                    "brand": brand,
                    "stock_quantity": stock,
                    "created_date": (
                        datetime.now() - timedelta(days=random.randint(1, 90))
                    ).isoformat(),
                    "status": "active",
                    "rating": round(random.uniform(3.5, 5.0), 1),
                    "reviews_count": random.randint(10, 500),
                }
            )
            product_id += 1

    db.insert_many(products)
    return len(products)


def setup_orders_data(db):
    """Set up sample order data"""

    # Get all products to create realistic orders
    all_products = list(db.all())

    orders = []
    order_id = 1000

    # Generate orders for the last 30 days
    for _ in range(50):  # 50 sample orders
        order_date = datetime.now() - timedelta(days=random.randint(0, 30))

        # Random number of items per order (1-4)
        num_items = random.randint(1, 4)
        selected_products = random.sample(all_products, num_items)

        total_amount = 0
        order_items = []

        for product in selected_products:
            quantity = random.randint(1, 3)
            item_total = product["price"] * quantity
            total_amount += item_total

            order_items.append(
                {
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "total_price": item_total,
                }
            )

        orders.append(
            {
                "order_id": order_id,
                "customer_id": random.randint(1, 100),
                "customer_email": f"customer{random.randint(1, 100)}@example.com",
                "order_date": order_date.isoformat(),
                "status": random.choice(
                    ["pending", "shipped", "delivered", "cancelled"]
                ),
                "items": order_items,
                "total_amount": round(total_amount, 2),
                "shipping_address": {
                    "street": f"{random.randint(100, 999)} Main St",
                    "city": random.choice(
                        ["New York", "Los Angeles", "Chicago", "Houston"]
                    ),
                    "country": "USA",
                },
            }
        )
        order_id += 1

    return orders


def main():
    # Create separate databases for products and orders
    products_db = SagittaDB("ecommerce_products.db")
    orders_db = SagittaDB("ecommerce_orders.db")

    print("🛒 E-commerce Product Management Example")
    print("=" * 45)

    # Clear existing data
    products_db.purge()
    orders_db.purge()

    # 1. Set up sample data
    print("1. Setting up sample product catalog...")
    product_count = setup_sample_data(products_db)
    print(f"   Inserted {product_count} products")

    print("\n2. Setting up sample orders...")
    orders = setup_orders_data(products_db)
    orders_db.insert_many(orders)
    print(f"   Inserted {len(orders)} orders")

    # Create indexes for better performance
    print("\n3. Creating performance indexes...")
    products_db.create_index("category")
    products_db.create_index("brand")
    products_db.create_index("price")
    products_db.create_index("status")

    orders_db.create_index("status")
    orders_db.create_index("customer_id")
    orders_db.create_index("order_date")
    print("   Indexes created for optimized queries")

    # 4. Product inventory analysis
    print("\n4. Product Inventory Analysis:")

    # Low stock products (< 50 items)
    print("   Low stock products (< 50 items):")
    low_stock = []
    for product in products_db.all():
        if product["stock_quantity"] < 50:
            low_stock.append(product)

    for product in sorted(low_stock, key=lambda x: x["stock_quantity"]):
        print(f"     - {product['name']}: {product['stock_quantity']} units")

    # Products by category
    print("\n   Products by category:")
    categories = ["Electronics", "Clothing", "Home"]
    for category in categories:
        count = products_db.count({"category": category})
        print(f"     - {category}: {count} products")

    # 5. Brand analysis
    print("\n5. Brand Performance:")
    brands = set()
    for product in products_db.all():
        brands.add(product["brand"])

    for brand in sorted(brands):
        products = list(products_db.search({"brand": brand}))
        avg_rating = sum(p["rating"] for p in products) / len(products)
        total_reviews = sum(p["reviews_count"] for p in products)
        print(
            f"   - {brand}: {len(products)} products, avg rating: {avg_rating:.1f}, {total_reviews} reviews"
        )

    # 6. Price range analysis
    print("\n6. Price Range Analysis:")
    price_ranges = [
        (0, 50, "Budget ($0-$50)"),
        (50, 100, "Mid-range ($50-$100)"),
        (100, 500, "Premium ($100-$500)"),
        (500, float("inf"), "Luxury ($500+)"),
    ]

    for min_price, max_price, label in price_ranges:
        count = 0
        for product in products_db.all():
            if min_price <= product["price"] < max_price:
                count += 1
        print(f"   - {label}: {count} products")

    # 7. Order analysis
    print("\n7. Order Analysis:")

    # Orders by status
    print("   Orders by status:")
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    for status in statuses:
        count = orders_db.count({"status": status})
        print(f"     - {status.title()}: {count} orders")

    # Recent orders (last 7 days)
    print("\n   Recent orders (last 7 days):")
    recent_date = (datetime.now() - timedelta(days=7)).isoformat()
    recent_orders = []
    for order in orders_db.all():
        if order["order_date"] > recent_date:
            recent_orders.append(order)

    print(f"     {len(recent_orders)} orders in the last 7 days")
    for order in sorted(recent_orders, key=lambda x: x["order_date"], reverse=True)[:5]:
        order_date = datetime.fromisoformat(order["order_date"]).strftime("%Y-%m-%d")
        print(
            f"     - Order #{order['order_id']}: ${order['total_amount']:.2f} on {order_date}"
        )

    # 8. Customer analysis
    print("\n8. Customer Analysis:")

    # Top customers by order count
    customer_orders = {}
    for order in orders_db.all():
        customer_id = order["customer_id"]
        if customer_id not in customer_orders:
            customer_orders[customer_id] = []
        customer_orders[customer_id].append(order)

    # Sort customers by number of orders
    top_customers = sorted(
        customer_orders.items(), key=lambda x: len(x[1]), reverse=True
    )[:5]

    print("   Top 5 customers by order count:")
    for customer_id, customer_order_list in top_customers:
        total_spent = sum(order["total_amount"] for order in customer_order_list)
        print(
            f"     - Customer #{customer_id}: {len(customer_order_list)} orders, ${total_spent:.2f} total"
        )

    # 9. Bulk operations example
    print("\n9. Bulk Operations Example:")

    # Update all Electronics products to add a discount
    print("   Applying 10% discount to all Electronics...")
    electronics_count = 0
    for product in products_db.search({"category": "Electronics"}):
        new_price = round(product["price"] * 0.9, 2)
        products_db.update(
            {"product_id": product["product_id"]},
            {"discounted_price": new_price, "discount_active": True},
        )
        electronics_count += 1

    print(f"   Applied discount to {electronics_count} electronics products")

    # 10. Search and filter examples
    print("\n10. Advanced Search Examples:")

    # Find Apple products
    apple_products = list(products_db.search({"brand": "Apple"}))
    print(f"   Apple products: {len(apple_products)} found")
    for product in apple_products:
        discount_info = ""
        if "discounted_price" in product:
            discount_info = f" (Discounted: ${product['discounted_price']})"
        print(f"     - {product['name']}: ${product['price']}{discount_info}")

    # Find orders with high value (> $200)
    high_value_orders = []
    for order in orders_db.all():
        if order["total_amount"] > 200:
            high_value_orders.append(order)

    print(f"\n   High-value orders (> $200): {len(high_value_orders)} found")
    for order in sorted(
        high_value_orders, key=lambda x: x["total_amount"], reverse=True
    )[:3]:
        print(
            f"     - Order #{order['order_id']}: ${order['total_amount']:.2f} ({order['status']})"
        )

    # Clean up
    products_db.close()
    orders_db.close()

    print("\n🎉 E-commerce example complete!")
    print("Databases created:")
    print(f"  - Products: {Path('ecommerce_products.db').absolute()}")
    print(f"  - Orders: {Path('ecommerce_orders.db').absolute()}")


if __name__ == "__main__":
    main()
