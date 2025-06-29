"""Test insert operations in SagittaDB."""

import pytest

from sagittadb import SagittaDB


class TestInsertOperations:
    """Test document insertion operations."""

    def test_insert_single_document(self, memory_db: SagittaDB) -> None:
        """Test inserting a single document."""
        doc = {"name": "Alice", "age": 30, "city": "New York"}
        doc_id = memory_db.insert(doc)

        assert doc_id is not None
        assert isinstance(doc_id, int)
        assert doc_id > 0

    def test_insert_empty_document(self, memory_db: SagittaDB) -> None:
        """Test inserting an empty document."""
        doc = {}
        doc_id = memory_db.insert(doc)

        assert doc_id is not None
        assert isinstance(doc_id, int)

    def test_insert_complex_document(self, memory_db: SagittaDB) -> None:
        """Test inserting a document with complex data types."""
        doc = {
            "name": "Bob",
            "age": 25,
            "active": True,
            "scores": [95, 87, 92],
            "metadata": {"created": "2024-01-01", "updated": None},
            "tags": ["student", "developer"],
        }
        doc_id = memory_db.insert(doc)

        assert doc_id is not None
        assert isinstance(doc_id, int)

    def test_insert_non_dict_raises_error(self, memory_db: SagittaDB) -> None:
        """Test that inserting non-dict raises TypeError."""
        with pytest.raises(TypeError, match="Document must be a dictionary"):
            memory_db.insert("not a dict")  # type: ignore

        with pytest.raises(TypeError, match="Document must be a dictionary"):
            memory_db.insert(123)  # type: ignore

        with pytest.raises(TypeError, match="Document must be a dictionary"):
            memory_db.insert(["list", "item"])  # type: ignore

    def test_insert_many_documents(
        self, memory_db: SagittaDB, sample_documents: list[dict]
    ) -> None:
        """Test inserting multiple documents."""
        memory_db.insert_many(sample_documents)

        # Verify all documents were inserted
        count = memory_db.count()
        assert count == len(sample_documents)

    def test_insert_many_empty_iterable(self, memory_db: SagittaDB) -> None:
        """Test inserting from an empty iterable."""
        memory_db.insert_many([])

        count = memory_db.count()
        assert count == 0

    def test_insert_many_with_invalid_document(self, memory_db: SagittaDB) -> None:
        """Test that insert_many raises error for invalid documents."""
        docs = [
            {"name": "Alice", "age": 30},
            "invalid document",  # This should cause an error
            {"name": "Bob", "age": 25},
        ]

        with pytest.raises(
            TypeError, match="All documents in the iterable must be dictionaries"
        ):
            memory_db.insert_many(docs)

    def test_insert_many_generator(self, memory_db: SagittaDB) -> None:
        """Test inserting from a generator."""

        def doc_generator():
            for i in range(3):
                yield {"id": i, "value": f"item_{i}"}

        memory_db.insert_many(doc_generator())

        count = memory_db.count()
        assert count == 3

    def test_insert_with_special_characters(self, memory_db: SagittaDB) -> None:
        """Test inserting documents with special characters."""
        doc = {
            "name": "José María",
            "description": "Special chars: éñüç øæå",
            "symbols": "!@#$%^&*()_+-=[]{}|;:,.<>?",
            "unicode": "🚀 🌟 💾 🔍",
        }
        doc_id = memory_db.insert(doc)

        assert doc_id is not None

        # Verify document can be retrieved
        results = list(memory_db.search({"name": "José María"}))
        assert len(results) == 1
        assert results[0]["description"] == "Special chars: éñüç øæå"

    def test_insert_large_document(self, memory_db: SagittaDB) -> None:
        """Test inserting a large document."""
        large_text = "x" * 10000  # 10KB string
        doc = {
            "id": "large_doc",
            "content": large_text,
            "metadata": {"size": len(large_text)},
        }
        doc_id = memory_db.insert(doc)

        assert doc_id is not None

        # Verify document can be retrieved
        results = list(memory_db.search({"id": "large_doc"}))
        assert len(results) == 1
        assert len(results[0]["content"]) == 10000
