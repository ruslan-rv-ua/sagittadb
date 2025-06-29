"""Test basic functionality of SagittaDB."""

from pathlib import Path

import pytest

from sagittadb import SagittaDB


class TestSagittaDBBasic:
    """Test basic SagittaDB functionality."""

    def test_create_database_with_file_path(self, temp_db_file: Path) -> None:
        """Test creating a database with a file path."""
        db = SagittaDB(temp_db_file)
        assert db._db_path == temp_db_file
        db.close()

    def test_create_database_with_string_path(self, temp_db_file: Path) -> None:
        """Test creating a database with a string path."""
        db = SagittaDB(str(temp_db_file))
        assert db._db_path == temp_db_file
        db.close()

    def test_create_in_memory_database(self) -> None:
        """Test creating an in-memory database."""
        db = SagittaDB(":memory:")
        assert db._db_path == ":memory:"
        db.close()

    def test_database_initialization(self, memory_db: SagittaDB) -> None:
        """Test that database is properly initialized with tables and indexes."""
        # Test that we can perform basic operations without errors
        doc = {"test": "value"}
        doc_id = memory_db.insert(doc)
        assert doc_id is not None
        assert isinstance(doc_id, int)

    def test_close_database(self, temp_db_file: Path) -> None:
        """Test closing the database connection."""
        db = SagittaDB(temp_db_file)
        db.close()

        # After closing, operations should fail
        with pytest.raises(Exception):
            db.insert({"test": "value"})

    def test_context_manager_behavior(self, memory_db: SagittaDB) -> None:
        """Test that transactions work properly."""
        # Insert a document to verify transaction behavior
        doc = {"name": "test", "value": 123}
        doc_id = memory_db.insert(doc)
        assert doc_id is not None

        # Verify the document was inserted
        results = list(memory_db.search({"name": "test"}))
        assert len(results) == 1
        assert results[0]["value"] == 123
