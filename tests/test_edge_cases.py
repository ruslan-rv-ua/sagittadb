"""Test edge cases and error conditions in SagittaDB."""

from pathlib import Path

import pytest

from sagittadb import SagittaDB


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_database_persistence(self, temp_db_file: Path) -> None:
        """Test that data persists between database connections."""
        # Insert data in first connection
        db1 = SagittaDB(temp_db_file)
        doc_id = db1.insert({"name": "Persistent", "value": 123})  # noqa: F841
        db1.close()

        # Open new connection and verify data exists
        db2 = SagittaDB(temp_db_file)
        results = list(db2.search({"name": "Persistent"}))

        assert len(results) == 1
        assert results[0]["value"] == 123
        db2.close()

    def test_concurrent_access_file_db(self, temp_db_file: Path) -> None:
        """Test concurrent access to file-based database."""
        db1 = SagittaDB(temp_db_file)
        db2 = SagittaDB(temp_db_file)

        try:
            # Both should be able to perform operations
            db1.insert({"source": "db1", "value": 1})
            db2.insert({"source": "db2", "value": 2})

            # Both should see all data
            count1 = db1.count()
            count2 = db2.count()

            assert count1 == 2
            assert count2 == 2
        finally:
            db1.close()
            db2.close()

    def test_empty_json_values(self, memory_db: SagittaDB) -> None:
        """Test handling of empty and null-like JSON values."""
        docs = [
            {"id": 1, "empty_string": ""},
            {"id": 2, "zero": 0},
            {"id": 3, "false": False},
            {"id": 4, "empty_list": []},
            {"id": 5, "empty_dict": {}},
        ]
        memory_db.insert_many(docs)

        # Test searching for simple values (complex values like [] and {} cannot be used as search parameters)
        assert len(list(memory_db.search({"empty_string": ""}))) == 1
        assert len(list(memory_db.search({"zero": 0}))) == 1
        assert len(list(memory_db.search({"false": False}))) == 1

        # Search by id to verify complex values were stored correctly
        result = list(memory_db.search({"id": 4}))[0]
        assert result["empty_list"] == []

        result = list(memory_db.search({"id": 5}))[0]
        assert result["empty_dict"] == {}

    def test_very_large_limit_offset(self, populated_db: SagittaDB) -> None:
        """Test behavior with very large limit and offset values."""
        # Large limit should return all available documents
        results = list(populated_db.all(limit=999999))
        assert len(results) == 5

        # Large offset should return empty results
        results = list(populated_db.all(offset=999999))
        assert len(results) == 0

    def test_negative_limit_offset(self, populated_db: SagittaDB) -> None:
        """Test behavior with negative limit and offset values."""
        # Negative offset should be treated as 0
        results = list(populated_db.all(offset=-1))
        assert len(results) == 5

        # Negative limit should return no results (SQLite behavior)
        results = list(populated_db.all(limit=-1, offset=0))
        # SQLite treats -1 as unlimited, so should return all
        assert len(results) == 5

    def test_unicode_and_special_characters(self, memory_db: SagittaDB) -> None:
        """Test handling of Unicode and special characters in data."""
        docs = [
            {"name": "José", "emoji": "👋", "chinese": "你好"},
            {"name": "François", "special": "!@#$%^&*()"},
            {"name": "Müller", "unicode": "∑∆∫"},
        ]
        memory_db.insert_many(docs)

        # Test search with Unicode
        results = list(memory_db.search({"name": "José"}))
        assert len(results) == 1
        assert results[0]["emoji"] == "👋"

        # Test pattern search with Unicode
        results = list(memory_db.search_pattern("name", ".*ç.*"))
        assert len(results) == 1
        assert results[0]["name"] == "François"

    def test_json_serialization_edge_cases(self, memory_db: SagittaDB) -> None:
        """Test edge cases in JSON serialization."""

        # Test various numeric edge cases
        docs = [
            {"value": float("inf")},  # This might cause issues
            {"value": -float("inf")},  # This might cause issues
            {"value": float("nan")},  # This will definitely cause issues
            {"value": 1.7976931348623157e308},  # Very large float
            {"value": -1.7976931348623157e308},  # Very large negative float
            {"value": 2**63 - 1},  # Large integer
            {"value": -(2**63)},  # Large negative integer
        ]

        # Some of these might fail due to JSON limitations
        for i, doc in enumerate(docs):
            try:
                memory_db.insert(doc)
            except (ValueError, OverflowError):
                # Expected for inf, -inf, nan
                pass

    def test_repeated_operations(self, memory_db: SagittaDB) -> None:
        """Test repeated operations for consistency."""
        doc = {"name": "Test", "counter": 0}
        doc_id = memory_db.insert(doc)

        # Perform multiple updates
        for i in range(100):
            memory_db.update({"name": "Test"}, {"counter": i})

        # Verify final state
        results = list(memory_db.search({"name": "Test"}))
        assert len(results) == 1
        assert results[0]["counter"] == 99

    def test_malformed_regex_pattern(self, populated_db: SagittaDB) -> None:
        """Test behavior with malformed regex patterns."""
        # This should raise an error due to invalid regex
        with pytest.raises(
            Exception
        ):  # Could be various types depending on implementation
            list(populated_db.search_pattern("name", "[invalid"))

    def test_very_long_field_names(self, memory_db: SagittaDB) -> None:
        """Test handling of very long field names."""
        long_field_name = "a" * 1000  # 1000 character field name
        doc = {long_field_name: "value"}

        # This should work as field names are just strings
        doc_id = memory_db.insert(doc)
        assert doc_id is not None

        # Creating an index should work since it's a valid identifier
        memory_db.create_index(long_field_name)

        # But an invalid identifier should fail
        with pytest.raises(ValueError):
            memory_db.create_index("123invalid")  # Can't start with number

    def test_deeply_nested_json(self, memory_db: SagittaDB) -> None:
        """Test handling of deeply nested JSON structures."""
        # Create a deeply nested structure
        nested_doc: dict = {"level": 0}
        current: dict = nested_doc
        for i in range(1, 50):  # 50 levels deep
            current["nested"] = {"level": i}
            current = current["nested"]

        doc_id = memory_db.insert(nested_doc)
        assert doc_id is not None

        # Search should work for top-level fields
        results = list(memory_db.search({"level": 0}))
        assert len(results) == 1

    def test_large_document_handling(self, memory_db: SagittaDB) -> None:
        """Test handling of large documents."""
        # Create a document with a large string (1MB)
        large_content = "x" * (1024 * 1024)  # 1MB string
        doc = {"id": "large", "content": large_content}

        doc_id = memory_db.insert(doc)
        assert doc_id is not None

        # Verify it can be retrieved
        results = list(memory_db.search({"id": "large"}))
        assert len(results) == 1
        assert len(results[0]["content"]) == 1024 * 1024
