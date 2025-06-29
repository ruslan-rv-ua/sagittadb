"""Test configuration and fixtures for SagittaDB tests."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from sagittadb import SagittaDB


@pytest.fixture
def temp_db_file() -> Generator[Path, None, None]:
    """Fixture that provides a temporary database file path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    try:
        yield tmp_path
    finally:
        # Clean up - remove the database file and any WAL/SHM files
        for ext in ["", "-wal", "-shm"]:
            file_path = tmp_path.with_suffix(f"{tmp_path.suffix}{ext}")
            if file_path.exists():
                file_path.unlink()


@pytest.fixture
def temp_db(temp_db_file: Path) -> Generator[SagittaDB, None, None]:
    """Fixture that provides a SagittaDB instance with a temporary database file."""
    db = SagittaDB(temp_db_file)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def memory_db() -> Generator[SagittaDB, None, None]:
    """Fixture that provides an in-memory SagittaDB instance."""
    db = SagittaDB(":memory:")
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_documents() -> list[dict]:
    """Fixture that provides sample documents for testing."""
    return [
        {"name": "Alice", "age": 30, "city": "New York", "active": True},
        {"name": "Bob", "age": 25, "city": "Los Angeles", "active": False},
        {"name": "Charlie", "age": 35, "city": "Chicago", "active": True},
        {"name": "Diana", "age": 28, "city": "New York", "active": True},
        {"name": "Eve", "age": 32, "city": "Seattle", "active": False},
    ]


@pytest.fixture
def populated_db(memory_db: SagittaDB, sample_documents: list[dict]) -> SagittaDB:
    """Fixture that provides a database pre-populated with sample documents."""
    memory_db.insert_many(sample_documents)
    return memory_db
