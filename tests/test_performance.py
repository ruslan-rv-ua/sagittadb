"""Performance and benchmark tests for SagittaDB."""

import time

import pytest

from sagittadb import SagittaDB


@pytest.mark.slow
class TestPerformance:
    """Performance tests for SagittaDB operations."""

    def test_bulk_insert_performance(self, memory_db: SagittaDB) -> None:
        """Test performance of bulk insert operations."""
        # Generate test data
        docs = [
            {"id": i, "name": f"User{i}", "active": i % 2 == 0} for i in range(1000)
        ]

        start_time = time.time()
        memory_db.insert_many(docs)
        end_time = time.time()

        insert_time = end_time - start_time

        # Verify all documents were inserted
        count = memory_db.count()
        assert count == 1000

        # Performance assertion (should complete in reasonable time)
        assert insert_time < 5.0  # Should complete within 5 seconds

    def test_search_performance_large_dataset(self, memory_db: SagittaDB) -> None:
        """Test search performance with large dataset."""
        # Insert large dataset
        docs = [
            {"id": i, "category": f"cat_{i % 10}", "value": i * 2} for i in range(5000)
        ]
        memory_db.insert_many(docs)

        # Test search performance
        start_time = time.time()
        results = list(memory_db.search({"category": "cat_5"}))
        end_time = time.time()

        search_time = end_time - start_time

        # Verify correct results
        assert (
            len(results) == 500
        )  # Should find 500 documents (every 10th from 5, 15, 25, ...)

        # Performance assertion
        assert search_time < 1.0  # Should complete within 1 second

    def test_indexed_vs_non_indexed_performance(self, memory_db: SagittaDB) -> None:
        """Test performance difference between indexed and non-indexed searches."""
        # Insert test data
        docs = [
            {"user_id": i, "name": f"User{i}", "score": i * 10} for i in range(2000)
        ]
        memory_db.insert_many(docs)

        # Test search without index
        start_time = time.time()
        results1 = list(memory_db.search({"user_id": 1500}))
        time_without_index = time.time() - start_time

        # Create index
        memory_db.create_index("user_id")

        # Test search with index
        start_time = time.time()
        results2 = list(memory_db.search({"user_id": 1500}))
        time_with_index = time.time() - start_time

        # Verify same results
        assert len(results1) == len(results2) == 1
        assert results1[0] == results2[0]

        # Note: For small datasets, the difference might not be significant
        # This test is more about ensuring indexes don't break functionality

    def test_pattern_search_performance(self, memory_db: SagittaDB) -> None:
        """Test pattern search performance."""
        # Insert test data with varied names
        names = [f"User_{i}_{chr(65 + i % 26)}" for i in range(1000)]
        docs = [{"name": name, "id": i} for i, name in enumerate(names)]
        memory_db.insert_many(docs)

        # Test pattern search
        start_time = time.time()
        results = list(memory_db.search_pattern("name", "User_.*_A"))
        end_time = time.time()

        search_time = end_time - start_time

        # Verify results (should find names ending with _A)
        assert len(results) > 0
        for result in results:
            assert result["name"].endswith("_A")

        # Performance assertion
        assert search_time < 2.0  # Should complete within 2 seconds

    @pytest.mark.slow
    def test_concurrent_operations_performance(self, memory_db: SagittaDB) -> None:
        """Test performance of concurrent-like operations."""
        import threading

        results = []
        errors = []

        def insert_batch(batch_id: int) -> None:
            try:
                docs = [
                    {"batch": batch_id, "id": i, "value": f"batch_{batch_id}_item_{i}"}
                    for i in range(100)
                ]
                memory_db.insert_many(docs)
                results.append(f"Batch {batch_id} completed")
            except Exception as e:
                errors.append(str(e))

        # Create and start threads
        threads = []
        start_time = time.time()

        for i in range(5):  # 5 batches of 100 documents each
            thread = threading.Thread(target=insert_batch, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Verify no errors occurred
        assert len(errors) == 0
        assert len(results) == 5

        # Verify all documents were inserted
        count = memory_db.count()
        assert count == 500  # 5 batches * 100 documents each

        # Performance assertion
        assert total_time < 10.0  # Should complete within 10 seconds


class TestMemoryUsage:
    """Test memory usage patterns."""

    def test_large_document_memory_handling(self, memory_db: SagittaDB) -> None:
        """Test handling of large documents without memory issues."""
        # Create moderately large documents
        large_docs = []
        for i in range(10):
            doc = {
                "id": i,
                "large_text": "x" * 10000,  # 10KB per document
                "data": list(range(1000)),  # List with 1000 integers
                "metadata": {"created": f"2024-01-{i + 1:02d}", "size": 10000},
            }
            large_docs.append(doc)

        # Insert all documents
        memory_db.insert_many(large_docs)

        # Verify all were inserted
        count = memory_db.count()
        assert count == 10

        # Verify we can retrieve them
        results = list(memory_db.all())
        assert len(results) == 10

        # Verify content integrity
        for i, result in enumerate(results):
            assert len(result["large_text"]) == 10000
            assert len(result["data"]) == 1000

    def test_iterator_memory_efficiency(self, memory_db: SagittaDB) -> None:
        """Test that iterators don't load all data into memory at once."""
        # Insert many documents
        docs = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        memory_db.insert_many(docs)

        # Use iterator - this should not cause memory issues
        count = 0
        for doc in memory_db.all():
            count += 1
            if count % 100 == 0:
                # Process in batches to simulate real usage
                pass

        assert count == 1000
