"""Test search operations in SagittaDB."""

import pytest

from sagittadb import SagittaDB


class TestSearchOperations:
    """Test document search operations."""

    def test_search_by_single_field(self, populated_db: SagittaDB) -> None:
        """Test searching by a single field."""
        results = list(populated_db.search({"city": "New York"}))

        assert len(results) == 2
        names = [doc["name"] for doc in results]
        assert "Alice" in names
        assert "Diana" in names

    def test_search_by_multiple_fields(self, populated_db: SagittaDB) -> None:
        """Test searching by multiple fields (AND condition)."""
        results = list(populated_db.search({"city": "New York", "active": True}))

        assert len(results) == 2
        for doc in results:
            assert doc["city"] == "New York"
            assert doc["active"] is True

    def test_search_no_results(self, populated_db: SagittaDB) -> None:
        """Test search that returns no results."""
        results = list(populated_db.search({"name": "NonExistent"}))

        assert len(results) == 0

    def test_search_with_limit(self, populated_db: SagittaDB) -> None:
        """Test search with limit parameter."""
        results = list(populated_db.search({"active": True}, limit=2))

        assert len(results) == 2
        for doc in results:
            assert doc["active"] is True

    def test_search_with_offset(self, populated_db: SagittaDB) -> None:
        """Test search with offset parameter."""
        all_active = list(populated_db.search({"active": True}))
        offset_results = list(populated_db.search({"active": True}, offset=1))

        assert len(offset_results) == len(all_active) - 1

    def test_search_with_limit_and_offset(self, populated_db: SagittaDB) -> None:
        """Test search with both limit and offset."""
        results = list(populated_db.search({"active": True}, limit=1, offset=1))

        assert len(results) == 1

    def test_search_empty_filter_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that empty filter dict raises ValueError."""
        with pytest.raises(ValueError, match="filter_dict must be a non-empty dict"):
            list(populated_db.search({}))

    def test_search_non_dict_filter_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that non-dict filter raises ValueError."""
        with pytest.raises(ValueError, match="filter_dict must be a non-empty dict"):
            list(populated_db.search("not a dict"))  # type: ignore

    def test_search_invalid_key_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that invalid keys in filter dict raise ValueError."""
        with pytest.raises(
            ValueError,
            match="All keys in filter_dict must be non-empty string identifiers",
        ):
            list(populated_db.search({"": "value"}))  # Empty key

        with pytest.raises(
            ValueError,
            match="All keys in filter_dict must be non-empty string identifiers",
        ):
            list(
                populated_db.search({"key with spaces": "value"})
            )  # Invalid identifier    def test_search_pattern_basic(self, populated_db: SagittaDB) -> None:
        """Test basic pattern search."""
        results = list(populated_db.search_pattern("name", "^A.*"))

        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_search_pattern_case_sensitive(self, populated_db: SagittaDB) -> None:
        """Test that pattern search is case sensitive."""
        results = list(populated_db.search_pattern("name", "^a.*"))

        assert (
            len(results) == 0
        )  # Should not match any names starting with lowercase 'a'

    def test_search_pattern_multiple_matches(self, populated_db: SagittaDB) -> None:
        """Test pattern search with multiple matches."""
        results = list(populated_db.search_pattern("city", ".*o.*"))

        # Should match "New York" (2 people), "Los Angeles" (1 person), and "Chicago" (1 person) = 4 total
        assert len(results) == 4
        cities = [doc["city"] for doc in results]
        assert "New York" in cities
        assert "Los Angeles" in cities
        assert "Chicago" in cities

    def test_search_pattern_with_limit_offset(self, populated_db: SagittaDB) -> None:
        """Test pattern search with limit and offset."""
        results = list(populated_db.search_pattern("name", ".*", limit=2, offset=1))

        assert len(results) == 2

    def test_search_pattern_empty_key_raises_error(
        self, populated_db: SagittaDB
    ) -> None:
        """Test that empty key raises ValueError."""
        with pytest.raises(ValueError, match="key must be a non-empty string"):
            list(populated_db.search_pattern("", "pattern"))

    def test_search_pattern_empty_pattern_raises_error(
        self, populated_db: SagittaDB
    ) -> None:
        """Test that empty pattern raises ValueError."""
        with pytest.raises(ValueError, match="pattern must be a non-empty string"):
            list(populated_db.search_pattern("name", ""))

    def test_find_any_basic(self, populated_db: SagittaDB) -> None:
        """Test basic find_any operation."""
        results = list(populated_db.find_any("name", ["Alice", "Bob"]))

        assert len(results) == 2
        names = [doc["name"] for doc in results]
        assert "Alice" in names
        assert "Bob" in names

    def test_find_any_single_value(self, populated_db: SagittaDB) -> None:
        """Test find_any with single value."""
        results = list(populated_db.find_any("name", ["Charlie"]))

        assert len(results) == 1
        assert results[0]["name"] == "Charlie"

    def test_find_any_no_matches(self, populated_db: SagittaDB) -> None:
        """Test find_any with no matches."""
        results = list(
            populated_db.find_any("name", ["NonExistent", "AlsoNonExistent"])
        )

        assert len(results) == 0

    def test_find_any_empty_values(self, populated_db: SagittaDB) -> None:
        """Test find_any with empty values list."""
        results = list(populated_db.find_any("name", []))

        assert len(results) == 0

    def test_find_any_invalid_key_raises_error(self, populated_db: SagittaDB) -> None:
        """Test that invalid key raises ValueError."""
        with pytest.raises(
            ValueError, match="key must be a valid non-empty string identifier"
        ):
            list(populated_db.find_any("", ["value"]))

        with pytest.raises(
            ValueError, match="key must be a valid non-empty string identifier"
        ):
            list(populated_db.find_any("key with spaces", ["value"]))

    def test_find_any_different_types(self, memory_db: SagittaDB) -> None:
        """Test find_any with different value types."""
        # Insert documents with different types
        memory_db.insert({"id": 1, "active": True})
        memory_db.insert({"id": "string_id", "active": False})
        memory_db.insert({"id": 3.14, "active": True})

        # Search for multiple types
        results = list(memory_db.find_any("id", [1, "string_id", 3.14]))

        assert len(results) == 3
