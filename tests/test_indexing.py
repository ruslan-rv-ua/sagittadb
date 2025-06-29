"""Test indexing operations in SagittaDB."""

from sagittadb import SagittaDB


class TestIndexOperations:
    """Test index creation and usage."""

    def test_create_index_basic(self, memory_db: SagittaDB) -> None:
        """Test creating a basic index."""
        # This should not raise an error
        memory_db.create_index("name")

        # Insert and search to verify index works
        memory_db.insert({"name": "Alice", "age": 30})
        results = list(memory_db.search({"name": "Alice"}))

        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_create_index_multiple_keys(self, memory_db: SagittaDB) -> None:
        """Test creating indexes on multiple keys."""
        memory_db.create_index("name")
        memory_db.create_index("age")
        memory_db.create_index("city")

        # Insert documents and verify searches work
        docs = [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "Los Angeles"},
        ]
        memory_db.insert_many(docs)

        # Test searches on indexed fields
        name_results = list(memory_db.search({"name": "Alice"}))
        age_results = list(memory_db.search({"age": 25}))
        city_results = list(memory_db.search({"city": "New York"}))

        assert len(name_results) == 1
        assert len(age_results) == 1
        assert len(city_results) == 1

    def test_create_index_if_not_exists(self, memory_db: SagittaDB) -> None:
        """Test that creating the same index multiple times doesn't cause errors."""
        # Create the same index multiple times
        memory_db.create_index("name")
        memory_db.create_index("name")
        memory_db.create_index("name")

        # Should still work normally
        memory_db.insert({"name": "Alice"})
        results = list(memory_db.search({"name": "Alice"}))

        assert len(results) == 1

    def test_create_index_invalid_key_raises_error(self, memory_db: SagittaDB) -> None:
        """Test that invalid keys raise ValueError."""
        import pytest

        with pytest.raises(
            ValueError, match="key must be a valid non-empty string identifier"
        ):
            memory_db.create_index("")

        with pytest.raises(
            ValueError, match="key must be a valid non-empty string identifier"
        ):
            memory_db.create_index("key with spaces")

        with pytest.raises(
            ValueError, match="key must be a valid non-empty string identifier"
        ):
            memory_db.create_index("123invalid")  # Can't start with number

    def test_search_performance_with_index(self, memory_db: SagittaDB) -> None:
        """Test that searches work with indexed fields."""
        # Create index before inserting data
        memory_db.create_index("user_id")

        # Insert a larger number of documents
        docs = [
            {"user_id": i, "name": f"User{i}", "active": i % 2 == 0}
            for i in range(1000)
        ]
        memory_db.insert_many(docs)

        # Search should work correctly regardless of index
        results = list(memory_db.search({"user_id": 500}))

        assert len(results) == 1
        assert results[0]["name"] == "User500"
        assert results[0]["active"] is True  # 500 % 2 == 0

    def test_index_on_non_existent_field(self, memory_db: SagittaDB) -> None:
        """Test creating index on field that doesn't exist in documents."""
        # Create index on field that doesn't exist yet
        memory_db.create_index("nonexistent")

        # Insert document without that field
        memory_db.insert({"name": "Alice", "age": 30})

        # Search for the non-existent field should return no results
        results = list(memory_db.search({"nonexistent": "value"}))
        assert len(results) == 0

        # Insert document with that field
        memory_db.insert({"name": "Bob", "nonexistent": "value"})

        # Now search should find the document
        results = list(memory_db.search({"nonexistent": "value"}))
        assert len(results) == 1
        assert results[0]["name"] == "Bob"
