# SagittaDB Tests

This directory contains comprehensive test suites for SagittaDB using pytest.

## Test Structure

- `conftest.py` - Test configuration and shared fixtures
- `test_basic.py` - Basic functionality tests (database creation, initialization)
- `test_insert.py` - Document insertion tests
- `test_search.py` - Search operation tests
- `test_update_remove.py` - Update and remove operation tests
- `test_retrieval.py` - Document retrieval and counting tests
- `test_indexing.py` - Index creation and usage tests
- `test_edge_cases.py` - Edge cases and error condition tests
- `test_performance.py` - Performance and benchmark tests

## Running Tests

### Prerequisites

Install pytest and development dependencies:

```bash
# Using uv (recommended)
uv sync --extra dev

# Or using pip
pip install -e ".[dev]"
```

### Basic Test Execution

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_basic.py
```

Run specific test class or function:
```bash
pytest tests/test_insert.py::TestInsertOperations
pytest tests/test_insert.py::TestInsertOperations::test_insert_single_document
```

### Test Categories

Run only fast tests (exclude performance tests):
```bash
pytest -m "not slow"
```

Run only performance tests:
```bash
pytest -m slow
```

### Coverage Reports

Run tests with coverage:
```bash
pytest --cov=sagittadb --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/` directory.

## Test Fixtures

The test suite provides several useful fixtures:

- `temp_db_file` - Provides a temporary database file path
- `temp_db` - Provides a SagittaDB instance with temporary file
- `memory_db` - Provides an in-memory SagittaDB instance
- `sample_documents` - Provides sample test documents
- `populated_db` - Provides a database pre-populated with sample documents

## Test Data

Sample documents used in tests:
```python
[
    {"name": "Alice", "age": 30, "city": "New York", "active": True},
    {"name": "Bob", "age": 25, "city": "Los Angeles", "active": False},
    {"name": "Charlie", "age": 35, "city": "Chicago", "active": True},
    {"name": "Diana", "age": 28, "city": "New York", "active": True},
    {"name": "Eve", "age": 32, "city": "Seattle", "active": False},
]
```

## Performance Tests

Performance tests are marked with `@pytest.mark.slow` and test:

- Bulk insert performance (1000+ documents)
- Search performance with large datasets
- Pattern search performance
- Concurrent operations
- Memory usage patterns

These tests help ensure SagittaDB maintains good performance characteristics as the codebase evolves.

## Adding New Tests

When adding new tests:

1. Follow the naming convention `test_*.py` for files and `test_*` for functions
2. Use appropriate fixtures from `conftest.py`
3. Add performance tests for operations that might be slow
4. Include edge cases and error conditions
5. Use descriptive test names that explain what is being tested

## Continuous Integration

The test suite is designed to run in CI environments. All tests should:

- Be deterministic and repeatable
- Clean up after themselves (fixtures handle this)
- Not depend on external resources
- Complete in reasonable time (mark slow tests appropriately)
