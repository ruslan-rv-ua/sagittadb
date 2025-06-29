"""A lightweight, document-oriented database using SQLite."""

try:
    import orjson

    JSONDecodeError = orjson.JSONDecodeError
except ImportError:
    import json as orjson
    from json.decoder import JSONDecodeError

import re
import sqlite3
from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any


class SagittaDB:
    """A lightweight, document-oriented database using SQLite."""

    def __init__(self, file_path: str | Path) -> None:
        """Initializes the SagittaDB database.

        Args:
            file_path: The path to the database file, or ":memory:" for an in-memory database.
        """
        if str(file_path) == ":memory:":
            self._db_path = ":memory:"
        else:
            self._db_path = Path(file_path).resolve()
        self._lock = RLock()
        self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
        self._add_regexp_support(self._connection)
        self._initialize_db()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Cursor]:
        """A context manager for database transactions.

        Yields:
            A database cursor for the transaction.
        """
        conn = self._connection.cursor()
        with self._lock:
            try:
                yield conn
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise
            finally:
                conn.close()

    def _initialize_db(self) -> None:
        """Initializes the database schema."""
        with self.transaction() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_key
                ON documents (
                    json_extract(data, '$.key')
                )
            """
            )
            conn.execute("PRAGMA journal_mode=WAL;")

    def create_index(self, key: str) -> None:
        """Creates an index on a JSON key for faster searching.

        Args:
            key: The key to create an index on.
        """
        if not key or not isinstance(key, str) or not key.isidentifier():
            raise ValueError("key must be a valid non-empty string identifier")
        index_name = f"idx_json_{key}"
        query = f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON documents (json_extract(data, '$.{key}'))
        """
        with self.transaction() as conn:
            conn.execute(query)

    @staticmethod
    def _add_regexp_support(conn: sqlite3.Connection) -> None:
        """Adds REGEXP support to the SQLite connection.

        Args:
            conn: The SQLite connection object.
        """

        def regexp(pattern, value):
            return re.search(pattern, value) is not None

        conn.create_function("REGEXP", 2, regexp)

    @staticmethod
    def _build_filter_clause(filter_dict: dict[str, Any]) -> tuple[str, list[Any]]:
        """Builds the WHERE clause and parameters for a query.

        Args:
            filter_dict: A dictionary of key-value pairs to filter by.

        Returns:
            A tuple containing the WHERE clause and a list of parameters.
        """
        if not isinstance(filter_dict, dict) or not filter_dict:
            raise ValueError("filter_dict must be a non-empty dict")

        keys = list(filter_dict.keys())
        if any(not isinstance(k, str) or not k.isidentifier() for k in keys):
            raise ValueError(
                "All keys in filter_dict must be non-empty string identifiers"
            )

        conditions = " AND ".join(
            [f"json_extract(data, '$.{key}') = ?" for key in keys]
        )
        params = [filter_dict[key] for key in keys]
        return conditions, params

    def insert(self, document: dict[str, Any]) -> int | None:
        """Inserts a single document into the database.

        Args:
            document: The document to insert.

        Returns:
            The ID of the inserted document.
        """
        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary")
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO documents (data) VALUES (?)", (orjson.dumps(document),)
            )
            return cursor.lastrowid

    def insert_many(self, document_iterable: Iterable[dict[str, Any]]) -> None:
        """Inserts multiple documents into the database.

        Args:
            document_iterable: An iterable of documents to insert.
        """

        def checked_generator(docs):
            for doc in docs:
                if not isinstance(doc, dict):
                    raise TypeError(
                        "All documents in the iterable must be dictionaries"
                    )
                yield (orjson.dumps(doc),)

        with self.transaction() as conn:
            conn.executemany(
                "INSERT INTO documents (data) VALUES (?)",
                checked_generator(document_iterable),
            )

    def remove(self, filter_dict: dict[str, Any]) -> int:
        """Removes documents matching the filter.

        Args:
            filter_dict: A dictionary of key-value pairs to filter by.

        Returns:
            The number of documents removed.
        """
        # Remove by dict: all key-value pairs must match
        where_clause, params = self._build_filter_clause(filter_dict)
        query = f"DELETE FROM documents WHERE {where_clause}"
        with self.transaction() as conn:
            result = conn.execute(query, params)
            return result.rowcount

    def update(self, filter_dict: dict[str, Any], update_dict: dict[str, Any]) -> int:
        """Updates documents matching the filter.

        Args:
            filter_dict: A dictionary of key-value pairs to filter by.
            update_dict: A dictionary of key-value pairs to update.

        Returns:
            The number of documents updated.
        """
        # Update documents matching filter_dict with values from update_dict
        where_clause, where_params = self._build_filter_clause(filter_dict)

        if not isinstance(update_dict, dict) or not update_dict:
            raise ValueError("update_dict must be a non-empty dict")
        update_keys, update_values = zip(*update_dict.items())
        if any(not isinstance(k, str) or not k for k in update_keys):
            raise ValueError("All keys in update_dict must be non-empty strings")
        if any(v is None for v in update_values):
            raise ValueError("Values in update_dict cannot be None")
        # Build SET clause using one json_set for all updates
        json_set_args = []
        for k in update_keys:
            json_set_args.append(f"'$.{k}'")
            json_set_args.append("?")
        set_clause = f"data = json_set(data, {', '.join(json_set_args)})"
        set_params = list(update_values)
        query = f"UPDATE documents SET {set_clause} WHERE {where_clause}"
        with self.transaction() as conn:
            result = conn.execute(query, set_params + where_params)
            return result.rowcount

    def purge(self) -> bool:
        """Removes all documents from the database.

        Returns:
            True if the operation was successful.
        """
        with self.transaction() as conn:
            conn.execute("DELETE FROM documents")
        return True

    def _execute_query(self, query: str, params: Sequence[Any] = ()) -> Iterator[Any]:
        """Executes a query that returns multiple rows.

        Args:
            query: The SQL query to execute.
            params: The parameters to bind to the query.

        Yields:
            The rows from the query result.
        """
        with self.transaction() as conn:
            cursor = conn.execute(query, params)
            for row in cursor:
                # For count() and other non-json results, row[0] might not be json
                try:
                    yield orjson.loads(row[0])
                except (JSONDecodeError, TypeError):
                    yield row[0]

    def _build_query_with_limit_offset(
        self,
        base_query: str,
        base_params: list[Any],
        limit: int | None,
        offset: int,
    ) -> tuple[str, list[Any]]:
        """Adds LIMIT and OFFSET clauses to a query.

        Args:
            base_query: The base SQL query.
            base_params: The parameters for the base query.
            limit: The maximum number of rows to return.
            offset: The number of rows to skip.

        Returns:
            A tuple containing the modified query and parameters.
        """
        if limit is not None:
            base_query += " LIMIT ? OFFSET ?"
            base_params.extend([limit, offset])
        elif offset > 0:
            base_query += " LIMIT -1 OFFSET ?"
            base_params.append(offset)
        return base_query, base_params

    def all(self, limit: int | None = None, offset: int = 0) -> Iterator[Any]:
        """Retrieves all documents from the database.

        Args:
            limit: The maximum number of documents to return.
            offset: The number of documents to skip.

        Yields:
            The documents from the database.
        """
        query = "SELECT data FROM documents"
        params = []
        query, params = self._build_query_with_limit_offset(
            query, params, limit, offset
        )
        yield from self._execute_query(query, params)

    def search(
        self,
        filter_dict: dict[str, Any],
        limit: int | None = None,
        offset: int = 0,
    ) -> Iterator[Any]:
        """Searches for documents matching a filter.

        Args:
            filter_dict: A dictionary of key-value pairs to filter by.
            limit: The maximum number of documents to return.
            offset: The number of documents to skip.

        Yields:
            The documents matching the filter.
        """
        where_clause, params = self._build_filter_clause(filter_dict)
        query = f"SELECT data FROM documents WHERE {where_clause}"
        query, params = self._build_query_with_limit_offset(
            query, params, limit, offset
        )
        yield from self._execute_query(query, params)

    def search_pattern(
        self,
        key: str,
        pattern: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> Iterator[Any]:
        """Searches for documents where a key matches a regular expression.

        Args:
            key: The key to search on.
            pattern: The regular expression pattern to match.
            limit: The maximum number of documents to return.
            offset: The number of documents to skip.

        Yields:
            The documents matching the search.
        """
        if not key or not isinstance(key, str):
            raise ValueError("key must be a non-empty string")
        if not pattern or not isinstance(pattern, str):
            raise ValueError("pattern must be a non-empty string")

        query = """
            SELECT data FROM documents
            WHERE json_extract(data, '$.' || ?) REGEXP ?
        """
        params = [key, pattern]
        query, params = self._build_query_with_limit_offset(
            query, params, limit, offset
        )
        yield from self._execute_query(query, params)

    def find_any(self, key: str, values: Iterable[Any]) -> Iterator[Any]:
        """Finds documents where a key has any of the given values.

        Args:
            key: The key to search on.
            values: An iterable of values to match.

        Yields:
            The documents matching the search.
        """
        value_list = list(values)
        if not key or not isinstance(key, str) or not key.isidentifier():
            raise ValueError("key must be a valid non-empty string identifier")

        if not value_list:
            return

        placeholders = ", ".join(["?"] * len(value_list))
        query = f"""
            SELECT data
            FROM documents
            WHERE json_extract(data, '$.{key}') IN ({placeholders})
        """
        yield from self._execute_query(query, value_list)

    def _execute_scalar_query(
        self,
        query: str,
        params: Sequence[Any] = (),
    ) -> Any:
        """Execute a query that returns a single scalar value.

        Args:
            query: The SQL query to execute.
            params: The parameters to bind to the query.

        Returns:
            The scalar result of the query.
        """
        with self.transaction() as conn:
            cursor = conn.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else None

    def count(self, filter_dict: dict[str, Any] | None = None) -> int:
        """Counts documents, optionally matching a filter.

        Args:
            filter_dict: A dictionary of key-value pairs to filter by.

        Returns:
            The number of documents matching the filter.
        """
        if filter_dict is None:
            query = "SELECT COUNT(*) FROM documents"
            params = []
        else:
            conditions, params = self._build_filter_clause(filter_dict)
            query = f"SELECT COUNT(*) FROM documents WHERE {conditions}"

        return self._execute_scalar_query(query, params) or 0

    def close(self) -> None:
        """Closes the database connection."""
        with self._lock:
            self._connection.close()
