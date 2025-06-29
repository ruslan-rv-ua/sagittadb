"""Test retrieval and counting operations in SagittaDB."""

from sagittadb import SagittaDB


class TestRetrievalOperations:
    """Test document retrieval operations."""

    def test_all_documents(self, populated_db: SagittaDB) -> None:
        """Test retrieving all documents."""
        results = list(populated_db.all())

        assert len(results) == 5

        # Verify all expected names are present
        names = [doc["name"] for doc in results]
        expected_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        for name in expected_names:
            assert name in names

    def test_all_with_limit(self, populated_db: SagittaDB) -> None:
        """Test retrieving all documents with limit."""
        results = list(populated_db.all(limit=3))

        assert len(results) == 3

    def test_all_with_offset(self, populated_db: SagittaDB) -> None:
        """Test retrieving all documents with offset."""
        all_results = list(populated_db.all())
        offset_results = list(populated_db.all(offset=2))

        assert len(offset_results) == len(all_results) - 2

    def test_all_with_limit_and_offset(self, populated_db: SagittaDB) -> None:
        """Test retrieving all documents with both limit and offset."""
        results = list(populated_db.all(limit=2, offset=1))

        assert len(results) == 2

    def test_all_empty_database(self, memory_db: SagittaDB) -> None:
        """Test retrieving all documents from empty database."""
        results = list(memory_db.all())

        assert len(results) == 0

    def test_all_with_zero_limit(self, populated_db: SagittaDB) -> None:
        """Test retrieving all documents with zero limit."""
        results = list(populated_db.all(limit=0))

        assert len(results) == 0

    def test_all_with_large_offset(self, populated_db: SagittaDB) -> None:
        """Test retrieving all documents with offset larger than document count."""
        results = list(populated_db.all(offset=100))

        assert len(results) == 0


class TestCountOperations:
    """Test document counting operations."""

    def test_count_all_documents(self, populated_db: SagittaDB) -> None:
        """Test counting all documents."""
        count = populated_db.count()

        assert count == 5

    def test_count_with_filter(self, populated_db: SagittaDB) -> None:
        """Test counting documents with filter."""
        count = populated_db.count({"active": True})

        assert count == 3

    def test_count_with_complex_filter(self, populated_db: SagittaDB) -> None:
        """Test counting documents with complex filter."""
        count = populated_db.count({"city": "New York", "active": True})

        assert count == 2

    def test_count_no_matches(self, populated_db: SagittaDB) -> None:
        """Test counting documents with filter that matches nothing."""
        count = populated_db.count({"name": "NonExistent"})

        assert count == 0

    def test_count_empty_database(self, memory_db: SagittaDB) -> None:
        """Test counting documents in empty database."""
        count = memory_db.count()

        assert count == 0

    def test_count_after_insert(self, memory_db: SagittaDB) -> None:
        """Test that count updates after insert."""
        initial_count = memory_db.count()
        memory_db.insert({"test": "document"})
        new_count = memory_db.count()

        assert new_count == initial_count + 1

    def test_count_after_remove(self, populated_db: SagittaDB) -> None:
        """Test that count updates after remove."""
        initial_count = populated_db.count()
        populated_db.remove({"name": "Alice"})
        new_count = populated_db.count()

        assert new_count == initial_count - 1

    def test_count_consistency(self, populated_db: SagittaDB) -> None:
        """Test that count() and len(all()) are consistent."""
        count_result = populated_db.count()
        all_result = list(populated_db.all())

        assert count_result == len(all_result)

    def test_count_with_filter_consistency(self, populated_db: SagittaDB) -> None:
        """Test that count with filter and search results are consistent."""
        filter_dict = {"active": True}
        count_result = populated_db.count(filter_dict)
        search_result = list(populated_db.search(filter_dict))

        assert count_result == len(search_result)
