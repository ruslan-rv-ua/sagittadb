"""
Performance Benchmarking Example

This example demonstrates SagittaDB performance characteristics:
- Bulk insertion benchmarks
- Query performance with and without indexes
- Memory vs file-based database comparison
- Concurrent access patterns
"""

import random
import statistics
import string
import time
from pathlib import Path
from threading import Thread

from sagittadb import SagittaDB


def generate_random_document(doc_id):
    """Generate a random document for testing"""
    return {
        "id": doc_id,
        "name": "".join(random.choices(string.ascii_letters, k=random.randint(5, 20))),
        "category": random.choice(["A", "B", "C", "D", "E"]),
        "value": random.randint(1, 1000),
        "active": random.choice([True, False]),
        "score": round(random.uniform(0, 100), 2),
        "tags": random.sample(
            ["tag1", "tag2", "tag3", "tag4", "tag5"], k=random.randint(1, 3)
        ),
        "metadata": {
            "created_by": f"user_{random.randint(1, 100)}",
            "region": random.choice(["US", "EU", "ASIA"]),
            "priority": random.choice(["low", "medium", "high"]),
        },
    }


def benchmark_insertion(db, num_docs, batch_size=1000):
    """Benchmark document insertion"""
    print(f"Inserting {num_docs:,} documents...")

    start_time = time.time()

    # Insert in batches for better performance
    for i in range(0, num_docs, batch_size):
        batch_end = min(i + batch_size, num_docs)
        batch = [generate_random_document(j) for j in range(i, batch_end)]
        db.insert_many(batch)

        if (i + batch_size) % 10000 == 0 or batch_end == num_docs:
            elapsed = time.time() - start_time
            docs_per_sec = (i + len(batch)) / elapsed
            print(
                f"  Progress: {batch_end:,}/{num_docs:,} docs ({docs_per_sec:.0f} docs/sec)"
            )

    total_time = time.time() - start_time
    return total_time


def benchmark_queries(db, num_queries=1000):
    """Benchmark various query operations"""
    print(f"Running {num_queries:,} query operations...")

    # Get some sample data for realistic queries
    sample_docs = list(db.all(limit=100))
    categories = list(set(doc["category"] for doc in sample_docs))

    query_types = []

    # 1. Simple search queries
    start_time = time.time()
    for _ in range(num_queries // 4):
        category = random.choice(categories)
        list(db.search({"category": category}))
    simple_search_time = time.time() - start_time
    query_types.append(("Simple search", simple_search_time, num_queries // 4))

    # 2. Multi-field search
    start_time = time.time()
    for _ in range(num_queries // 4):
        category = random.choice(categories)
        active = random.choice([True, False])
        list(db.search({"category": category, "active": active}))
    multi_field_time = time.time() - start_time
    query_types.append(("Multi-field search", multi_field_time, num_queries // 4))

    # 3. Pattern matching
    start_time = time.time()
    for _ in range(num_queries // 4):
        pattern = f".*{random.choice(string.ascii_letters)}.*"
        list(db.search_pattern("name", pattern))
    pattern_time = time.time() - start_time
    query_types.append(("Pattern matching", pattern_time, num_queries // 4))

    # 4. Count operations
    start_time = time.time()
    for _ in range(num_queries // 4):
        category = random.choice(categories)
        db.count({"category": category})
    count_time = time.time() - start_time
    query_types.append(("Count operations", count_time, num_queries // 4))

    return query_types


def benchmark_updates(db, num_updates=1000):
    """Benchmark update operations"""
    print(f"Running {num_updates:,} update operations...")

    # Get some sample IDs
    sample_docs = list(db.all(limit=num_updates))
    doc_ids = [doc["id"] for doc in sample_docs]

    start_time = time.time()
    for doc_id in doc_ids:
        new_score = round(random.uniform(0, 100), 2)
        db.update({"id": doc_id}, {"score": new_score, "last_updated": time.time()})

    update_time = time.time() - start_time
    return update_time


def concurrent_access_test(db_path, num_threads=5, operations_per_thread=100):
    """Test concurrent access to database"""
    print(f"Testing concurrent access with {num_threads} threads...")

    def worker_function(thread_id, results):
        """Worker function for concurrent testing"""
        db = SagittaDB(db_path)
        thread_times = []

        try:
            for i in range(operations_per_thread):
                # Mix of operations
                start_time = time.time()

                if i % 3 == 0:
                    # Insert operation
                    doc = generate_random_document(f"thread_{thread_id}_{i}")
                    db.insert(doc)
                elif i % 3 == 1:
                    # Search operation
                    list(db.search({"category": "A"}))
                else:
                    # Count operation
                    db.count()

                thread_times.append(time.time() - start_time)
        finally:
            db.close()

        results[thread_id] = thread_times

    # Run concurrent operations
    threads = []
    results = {}

    overall_start = time.time()

    for i in range(num_threads):
        thread = Thread(target=worker_function, args=(i, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    overall_time = time.time() - overall_start

    # Analyze results
    all_times = []
    for thread_times in results.values():
        all_times.extend(thread_times)

    return {
        "total_time": overall_time,
        "total_operations": num_threads * operations_per_thread,
        "avg_operation_time": statistics.mean(all_times),
        "median_operation_time": statistics.median(all_times),
        "operations_per_second": (num_threads * operations_per_thread) / overall_time,
    }


def main():
    print("🏹 SagittaDB Performance Benchmark")
    print("=" * 40)

    # Test parameters
    num_docs = 50000  # Adjust based on your system

    # 1. File-based database benchmark
    print("\n1. File-based Database Performance")
    print("-" * 35)

    file_db_path = Path("benchmark_file.db")
    if file_db_path.exists():
        file_db_path.unlink()  # Remove existing file

    file_db = SagittaDB(file_db_path)

    # Insertion benchmark
    insert_time = benchmark_insertion(file_db, num_docs)
    print(
        f"Insertion completed in {insert_time:.2f}s ({num_docs / insert_time:.0f} docs/sec)"
    )

    # Create indexes
    print("\nCreating indexes...")
    index_start = time.time()
    file_db.create_index("category")
    file_db.create_index("value")
    file_db.create_index("active")
    index_time = time.time() - index_start
    print(f"Index creation completed in {index_time:.2f}s")

    # Query benchmarks
    query_results = benchmark_queries(file_db, 2000)
    print("\nQuery Performance:")
    for query_type, time_taken, num_ops in query_results:
        ops_per_sec = num_ops / time_taken
        print(f"  {query_type}: {ops_per_sec:.0f} ops/sec")

    # Update benchmark
    update_time = benchmark_updates(file_db, 1000)
    print(f"\nUpdate Performance: {1000 / update_time:.0f} updates/sec")

    file_db.close()

    # 2. Memory database benchmark
    print("\n\n2. In-Memory Database Performance")
    print("-" * 35)

    memory_db = SagittaDB(":memory:")

    # Insertion benchmark
    insert_time_mem = benchmark_insertion(memory_db, num_docs)
    print(
        f"Insertion completed in {insert_time_mem:.2f}s ({num_docs / insert_time_mem:.0f} docs/sec)"
    )

    # Create indexes
    print("\nCreating indexes...")
    index_start = time.time()
    memory_db.create_index("category")
    memory_db.create_index("value")
    memory_db.create_index("active")
    index_time_mem = time.time() - index_start
    print(f"Index creation completed in {index_time_mem:.2f}s")

    # Query benchmarks
    query_results_mem = benchmark_queries(memory_db, 2000)
    print("\nQuery Performance:")
    for query_type, time_taken, num_ops in query_results_mem:
        ops_per_sec = num_ops / time_taken
        print(f"  {query_type}: {ops_per_sec:.0f} ops/sec")

    # Update benchmark
    update_time_mem = benchmark_updates(memory_db, 1000)
    print(f"\nUpdate Performance: {1000 / update_time_mem:.0f} updates/sec")

    memory_db.close()

    # 3. Comparison
    print("\n\n3. Performance Comparison")
    print("-" * 30)
    print("Insertion Speed:")
    print(f"  File DB:   {num_docs / insert_time:.0f} docs/sec")
    print(f"  Memory DB: {num_docs / insert_time_mem:.0f} docs/sec")
    print(f"  Memory is {insert_time / insert_time_mem:.1f}x faster for insertion")

    print("\nIndex Creation:")
    print(f"  File DB:   {index_time:.2f}s")
    print(f"  Memory DB: {index_time_mem:.2f}s")

    # 4. Concurrent access test
    print("\n\n4. Concurrent Access Test")
    print("-" * 30)

    concurrent_results = concurrent_access_test(
        file_db_path, num_threads=3, operations_per_thread=50
    )
    print(f"Total operations: {concurrent_results['total_operations']}")
    print(f"Total time: {concurrent_results['total_time']:.2f}s")
    print(f"Operations per second: {concurrent_results['operations_per_second']:.0f}")
    print(
        f"Average operation time: {concurrent_results['avg_operation_time'] * 1000:.2f}ms"
    )
    print(
        f"Median operation time: {concurrent_results['median_operation_time'] * 1000:.2f}ms"
    )

    # 5. Database size analysis
    print("\n\n5. Database Size Analysis")
    print("-" * 30)
    if file_db_path.exists():
        file_size_mb = file_db_path.stat().st_size / (1024 * 1024)
        print(f"Database file size: {file_size_mb:.2f} MB")
        print(
            f"Average document size: {(file_size_mb * 1024 * 1024) / num_docs:.0f} bytes"
        )

    print("\n🎉 Benchmark complete!")
    print(f"Test database saved as: {file_db_path.absolute()}")


if __name__ == "__main__":
    main()
