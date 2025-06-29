"""
In-Memory Database Example

This example demonstrates using SagittaDB as an in-memory database:
- Session-based data storage
- Cache-like operations
- Temporary data processing
- Real-time analytics
"""

import random
import time
from datetime import datetime, timedelta

from sagittadb import SagittaDB


def simulate_web_session_tracking():
    """Simulate web session tracking with in-memory database"""

    print("📊 Web Session Tracking Simulation")
    print("-" * 35)

    # Create in-memory database for session tracking
    session_db = SagittaDB(":memory:")

    # Create indexes for faster lookups
    session_db.create_index("user_id")
    session_db.create_index("session_id")
    session_db.create_index("page")

    # Simulate user sessions
    session_data = []
    session_id = 1000

    print("Generating session data...")

    for user_id in range(1, 21):  # 20 users
        # Each user has 1-3 sessions
        num_sessions = random.randint(1, 3)

        for _ in range(num_sessions):
            session_start = datetime.now() - timedelta(hours=random.randint(0, 24))

            # Each session has 3-10 page views
            num_pages = random.randint(3, 10)

            for page_num in range(num_pages):
                session_data.append(
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "page": random.choice(
                            [
                                "/home",
                                "/products",
                                "/about",
                                "/contact",
                                "/cart",
                                "/checkout",
                            ]
                        ),
                        "timestamp": (
                            session_start + timedelta(minutes=page_num * 2)
                        ).isoformat(),
                        "duration_seconds": random.randint(10, 300),
                        "user_agent": random.choice(
                            ["Chrome", "Firefox", "Safari", "Edge"]
                        ),
                        "referrer": random.choice(
                            ["google.com", "facebook.com", "direct", "twitter.com"]
                        ),
                    }
                )

            session_id += 1

    # Insert all session data
    session_db.insert_many(session_data)
    print(f"Inserted {len(session_data)} page views from {session_id - 1000} sessions")

    # Analytics queries
    print("\n📈 Real-time Analytics:")

    # 1. Most popular pages
    page_views = {}
    for view in session_db.all():
        page = view["page"]
        page_views[page] = page_views.get(page, 0) + 1

    print("Most popular pages:")
    for page, count in sorted(page_views.items(), key=lambda x: x[1], reverse=True):
        print(f"  {page}: {count} views")

    # 2. Active users
    unique_users = set()
    for view in session_db.all():
        unique_users.add(view["user_id"])
    print(f"\nActive users: {len(unique_users)}")

    # 3. Browser distribution
    browser_stats = {}
    for view in session_db.all():
        browser = view["user_agent"]
        browser_stats[browser] = browser_stats.get(browser, 0) + 1

    print("\nBrowser distribution:")
    total_views = len(session_data)
    for browser, count in sorted(
        browser_stats.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / total_views) * 100
        print(f"  {browser}: {count} views ({percentage:.1f}%)")

    # 4. User engagement (pages per session)
    sessions = {}
    for view in session_db.all():
        sid = view["session_id"]
        if sid not in sessions:
            sessions[sid] = []
        sessions[sid].append(view)

    pages_per_session = [len(views) for views in sessions.values()]
    avg_pages = sum(pages_per_session) / len(pages_per_session)
    print(f"\nAverage pages per session: {avg_pages:.1f}")

    session_db.close()
    return len(session_data)


def simulate_real_time_cache():
    """Simulate a real-time cache with TTL-like behavior"""

    print("\n💾 Real-time Cache Simulation")
    print("-" * 30)

    cache_db = SagittaDB(":memory:")
    cache_db.create_index("key")
    cache_db.create_index("expires_at")

    def cache_set(key, value, ttl_seconds=300):
        """Set a value in cache with TTL"""
        expires_at = time.time() + ttl_seconds
        cache_db.remove({"key": key})  # Remove existing
        cache_db.insert(
            {
                "key": key,
                "value": value,
                "created_at": time.time(),
                "expires_at": expires_at,
            }
        )

    def cache_get(key):
        """Get a value from cache if not expired"""
        current_time = time.time()
        entries = list(cache_db.search({"key": key}))

        if not entries:
            return None

        entry = entries[0]
        if entry["expires_at"] < current_time:
            # Expired, remove it
            cache_db.remove({"key": key})
            return None

        return entry["value"]

    def cache_cleanup():
        """Remove expired entries"""
        current_time = time.time()
        expired_count = 0

        for entry in cache_db.all():
            if entry["expires_at"] < current_time:
                cache_db.remove({"key": entry["key"]})
                expired_count += 1

        return expired_count

    # Simulate cache operations
    print("Setting cache values...")

    # Set some cache entries with different TTLs
    cache_entries = [
        ("user_session_1001", {"user_id": 1, "username": "alice"}, 60),
        ("product_data_123", {"name": "Laptop", "price": 999.99}, 300),
        ("api_response_weather", {"temp": 22, "condition": "sunny"}, 30),
        ("user_preferences_1001", {"theme": "dark", "language": "en"}, 3600),
        ("temp_calculation_xyz", {"result": 42.7, "formula": "x*y+z"}, 10),
    ]

    for key, value, ttl in cache_entries:
        cache_set(key, value, ttl)
        print(f"  Cached '{key}' for {ttl}s")

    print(f"\nCache size: {cache_db.count()} entries")

    # Test cache retrieval
    print("\nTesting cache retrieval:")
    test_keys = ["user_session_1001", "product_data_123", "nonexistent_key"]

    for key in test_keys:
        value = cache_get(key)
        if value:
            print(f"  {key}: Found - {value}")
        else:
            print(f"  {key}: Not found or expired")

    # Simulate time passing
    print("\nSimulating 35 seconds passing...")
    time.sleep(1)  # Small delay for demo

    # Mock time passing by updating expires_at for demonstration
    current_mock_time = time.time() + 35

    # Count what would be expired
    expired_count = 0
    for entry in cache_db.all():
        if entry["expires_at"] < current_mock_time:
            expired_count += 1

    print(f"Entries that would be expired: {expired_count}")

    # Test retrieval again
    print("\nTesting cache after time passage:")
    for key in test_keys:
        value = cache_get(key)
        if value:
            print(f"  {key}: Still valid - {value}")
        else:
            print(f"  {key}: Expired or not found")

    cache_db.close()


def simulate_data_processing_pipeline():
    """Simulate a data processing pipeline using in-memory storage"""

    print("\n🔄 Data Processing Pipeline Simulation")
    print("-" * 40)

    # Create databases for different pipeline stages
    raw_db = SagittaDB(":memory:")
    processed_db = SagittaDB(":memory:")
    analytics_db = SagittaDB(":memory:")

    # Create indexes
    raw_db.create_index("batch_id")
    processed_db.create_index("category")
    analytics_db.create_index("metric")

    print("Stage 1: Ingesting raw data...")

    # Simulate raw data ingestion
    raw_data = []
    batch_id = "batch_001"

    for i in range(1000):
        raw_data.append(
            {
                "id": i,
                "batch_id": batch_id,
                "raw_value": random.uniform(0, 100),
                "category": random.choice(["A", "B", "C"]),
                "quality": random.choice(["good", "poor", "excellent"]),
                "timestamp": (datetime.now() - timedelta(seconds=i)).isoformat(),
            }
        )

    raw_db.insert_many(raw_data)
    print(f"  Ingested {len(raw_data)} raw records")

    print("\nStage 2: Processing data...")

    # Process data: filter, transform, validate
    processed_count = 0

    for record in raw_db.search({"batch_id": batch_id}):
        # Filter out poor quality data
        if record["quality"] == "poor":
            continue

        # Transform the data
        processed_record = {
            "original_id": record["id"],
            "category": record["category"],
            "processed_value": record["raw_value"] * 1.1,  # Apply some transformation
            "normalized_value": min(record["raw_value"] / 100, 1.0),
            "quality_score": 0.8 if record["quality"] == "good" else 1.0,
            "processing_timestamp": datetime.now().isoformat(),
        }

        processed_db.insert(processed_record)
        processed_count += 1

    print(
        f"  Processed {processed_count} records (filtered out {len(raw_data) - processed_count} poor quality)"
    )

    print("\nStage 3: Generating analytics...")

    # Generate analytics from processed data
    analytics = {}

    # Category-based analytics
    categories = ["A", "B", "C"]
    for category in categories:
        category_records = list(processed_db.search({"category": category}))

        if category_records:
            values = [r["processed_value"] for r in category_records]

            analytics[f"category_{category}"] = {
                "metric": f"category_{category}_stats",
                "count": len(category_records),
                "avg_value": sum(values) / len(values),
                "min_value": min(values),
                "max_value": max(values),
                "total_value": sum(values),
            }

    # Overall analytics
    all_processed = list(processed_db.all())
    all_values = [r["processed_value"] for r in all_processed]

    analytics["overall"] = {
        "metric": "overall_stats",
        "total_records": len(all_processed),
        "avg_value": sum(all_values) / len(all_values),
        "data_quality_avg": sum(r["quality_score"] for r in all_processed)
        / len(all_processed),
    }

    # Store analytics
    for key, data in analytics.items():
        analytics_db.insert(data)

    print("  Analytics generated:")
    for metric in analytics_db.all():
        if metric["metric"].startswith("category_"):
            category = metric["metric"].split("_")[1]
            print(
                f"    Category {category}: {metric['count']} records, avg value: {metric['avg_value']:.2f}"
            )
        elif metric["metric"] == "overall_stats":
            print(
                f"    Overall: {metric['total_records']} records, quality: {metric['data_quality_avg']:.2f}"
            )

    # Performance summary
    print("\nPipeline completed:")
    print(f"  Raw data: {raw_db.count()} records")
    print(f"  Processed: {processed_db.count()} records")
    print(f"  Analytics: {analytics_db.count()} metrics")

    # Clean up
    raw_db.close()
    processed_db.close()
    analytics_db.close()


def main():
    print("🏹 SagittaDB In-Memory Database Examples")
    print("=" * 45)

    start_time = time.time()

    # Run different in-memory scenarios
    session_count = simulate_web_session_tracking()
    simulate_real_time_cache()
    simulate_data_processing_pipeline()

    total_time = time.time() - start_time

    print("\n🎉 All in-memory examples completed!")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Processed {session_count} session records plus cache and pipeline data")
    print("\nAdvantages of in-memory mode:")
    print("  ✅ Faster operations (no disk I/O)")
    print("  ✅ Perfect for temporary/session data")
    print("  ✅ No file cleanup needed")
    print("  ✅ Ideal for caching and real-time analytics")


if __name__ == "__main__":
    main()
