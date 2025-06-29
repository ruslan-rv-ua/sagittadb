"""Test update and remove operations in SagittaDB."""

import pytest

from sagittadb import SagittaDB


class TestUpdateOperations:
    """Test document update operations."""

    def test_update_single_field(self, populated_db: SagittaDB) -> None:
        """Test updating a single field."""
        # Update Alice's age
        updated_count = populated_db.update({"name": "Alice"}, {"age": 31})

        assert updated_count == 1

        # Verify the update
        results = list(populated_db.search({"name": "Alice"}))
        assert len(results) == 1
        assert results[0]["age"] == 31

    def test_update_multiple_fields(self, populated_db: SagittaDB) -> None:
        """Test updating multiple fields."""
        updated_count = populated_db.update(
            {"name": "Bob"}, {"age": 26, "city": "San Francisco", "active": True}
        )

        assert updated_count == 1

        # Verify all updates
        results = list(populated_db.search({"name": "Bob"}))
        assert len(results) == 1
        doc = results[0]
        assert doc["age"] == 26
        assert doc["city"] == "San Francisco"
        assert doc["active"]

    def test_update_multiple_documents(self, populated_db: SagittaDB) -> None:
        """Test updating multiple documents."""
        # Update all documents in New York
        updated_count = populated_db.update({"city": "New York"}, {"active": False})

        assert updated_count == 2

        # Verify updates
        results = list(populated_db.search({"city": "New York"}))
        assert len(results) == 2
        for doc in results:
            assert not doc["active"]

    def test_update_no_matches(self, populated_db: SagittaDB) -> None:
        """Test updating with filter that matches no documents."""
        updated_count = populated_db.update({"name": "NonExistent"}, {"age": 100})

        assert updated_count == 0

    def test_update_empty_filter_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that empty filter dict raises ValueError."""
        with pytest.raises(ValueError, match="filter_dict must be a non-empty dict"):
            populated_db.update({}, {"age": 30})

    def test_update_empty_update_dict_raises_error(
        self, populated_db: SagittaDB
    ) -> None:
        """Test that empty update dict raises ValueError."""
        with pytest.raises(ValueError, match="update_dict must be a non-empty dict"):
            populated_db.update({"name": "Alice"}, {})

    def test_update_none_values_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that None values in update dict raise ValueError."""
        with pytest.raises(ValueError, match="Values in update_dict cannot be None"):
            populated_db.update({"name": "Alice"}, {"age": None})

    def test_update_invalid_keys_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that invalid keys in update dict raise ValueError."""
        with pytest.raises(
            ValueError, match="All keys in update_dict must be non-empty strings"
        ):
            populated_db.update({"name": "Alice"}, {"": "value"})

    def test_update_add_new_field(self, populated_db: SagittaDB) -> None:
        """Test adding a new field to existing documents."""
        updated_count = populated_db.update(
            {"name": "Alice"}, {"email": "alice@example.com"}
        )

        assert updated_count == 1

        # Verify new field was added
        results = list(populated_db.search({"name": "Alice"}))
        assert len(results) == 1
        assert results[0]["email"] == "alice@example.com"


class TestRemoveOperations:
    """Test document removal operations."""

    def test_remove_single_document(self, populated_db: SagittaDB) -> None:
        """Test removing a single document."""
        initial_count = populated_db.count()
        removed_count = populated_db.remove({"name": "Alice"})

        assert removed_count == 1
        assert populated_db.count() == initial_count - 1

        # Verify document was removed
        results = list(populated_db.search({"name": "Alice"}))
        assert len(results) == 0

    def test_remove_multiple_documents(self, populated_db: SagittaDB) -> None:
        """Test removing multiple documents."""
        initial_count = populated_db.count()
        removed_count = populated_db.remove({"city": "New York"})

        assert removed_count == 2
        assert populated_db.count() == initial_count - 2

        # Verify documents were removed
        results = list(populated_db.search({"city": "New York"}))
        assert len(results) == 0

    def test_remove_no_matches(self, populated_db: SagittaDB) -> None:
        """Test removing with filter that matches no documents."""
        initial_count = populated_db.count()
        removed_count = populated_db.remove({"name": "NonExistent"})

        assert removed_count == 0
        assert populated_db.count() == initial_count

    def test_remove_empty_filter_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that empty filter dict raises ValueError."""
        with pytest.raises(ValueError, match="filter_dict must be a non-empty dict"):
            populated_db.remove({})

    def test_remove_complex_filter(self, populated_db: SagittaDB) -> None:
        """Test removing with complex filter."""
        removed_count = populated_db.remove({"active": True, "age": 30})

        assert removed_count == 1  # Should only match Alice

        # Verify correct document was removed
        results = list(populated_db.search({"name": "Alice"}))
        assert len(results) == 0

        # Verify other active users are still there
        results = list(populated_db.search({"active": True}))
        assert len(results) == 2  # Charlie and Diana


class TestPurgeOperation:
    """Test purge operation."""

    def test_purge_all_documents(self, populated_db: SagittaDB) -> None:
        """Test purging all documents."""
        # Verify database has documents
        initial_count = populated_db.count()
        assert initial_count > 0

        # Purge all documents
        result = populated_db.purge()

        assert result is True
        assert populated_db.count() == 0

        # Verify all documents are gone
        results = list(populated_db.all())
        assert len(results) == 0

    def test_purge_empty_database(self, memory_db: SagittaDB) -> None:
        """Test purging an already empty database."""
        result = memory_db.purge()

        assert result is True
        assert memory_db.count() == 0
