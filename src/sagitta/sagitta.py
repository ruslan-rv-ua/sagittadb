import json
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import RLock


class Sagitta:
    def __init__(self, file_path: str | Path):
        if str(file_path) == ":memory:":
            self._db_path = ":memory:"
        else:
            self._db_path = Path(file_path).resolve()
        self._lock = RLock()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
        self._add_regexp_support(self._connection)
        self._initialize_db()

    @contextmanager
    def transaction(self):
        """A context manager for database transactions."""
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

    def _initialize_db(self):
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

    def create_index(self, key):
        """Creates an index on a JSON key for faster searching."""
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
    def _add_regexp_support(conn):
        def regexp(pattern, value):
            return re.search(pattern, value) is not None

        conn.create_function("REGEXP", 2, regexp)

    @staticmethod
    def _build_filter_clause(filter_dict):
        """Builds the WHERE clause and parameters for a query."""
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

    def insert(self, document):
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO documents (data) VALUES (?)", (json.dumps(document),)
            )
            return cursor.lastrowid

    def insert_many(self, document_iterable):
        with self.transaction() as conn:
            conn.executemany(
                "INSERT INTO documents (data) VALUES (?)",
                ((json.dumps(doc),) for doc in document_iterable),
            )

    def remove(self, filter_dict):
        # Remove by dict: all key-value pairs must match
        where_clause, params = self._build_filter_clause(filter_dict)
        query = f"DELETE FROM documents WHERE {where_clause}"
        with self.transaction() as conn:
            result = conn.execute(query, params)
            return result.rowcount

    def update(self, filter_dict, update_dict):
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

    def purge(self):
        with self.transaction() as conn:
            conn.execute("DELETE FROM documents")
        return True

    def _execute_query(self, query, params=()):
        with self.transaction() as conn:
            cursor = conn.execute(query, params)
            for row in cursor:
                # For count() and other non-json results, row[0] might not be json
                try:
                    yield json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    yield row[0]

    def _build_query_with_limit_offset(self, base_query, base_params, limit, offset):
        if limit is not None:
            base_query += " LIMIT ? OFFSET ?"
            base_params.extend([limit, offset])
        elif offset > 0:
            base_query += " LIMIT -1 OFFSET ?"
            base_params.append(offset)
        return base_query, base_params

    def all(self, limit=None, offset=0):
        query = "SELECT data FROM documents"
        params = []
        query, params = self._build_query_with_limit_offset(
            query, params, limit, offset
        )
        yield from self._execute_query(query, params)

    def search(self, filter_dict, limit=None, offset=0):
        where_clause, params = self._build_filter_clause(filter_dict)
        query = f"SELECT data FROM documents WHERE {where_clause}"
        query, params = self._build_query_with_limit_offset(
            query, params, limit, offset
        )
        yield from self._execute_query(query, params)

    def search_pattern(self, key, pattern, limit=100, offset=0):
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

    def find_any(self, key, values):
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

    def count(self, filter_dict=None):
        """Counts documents, optionally matching a filter."""
        if filter_dict is None:
            query = "SELECT COUNT(*) FROM documents"
            params = []
        else:
            conditions, params = self._build_filter_clause(filter_dict)
            query = f"SELECT COUNT(*) FROM documents WHERE {conditions}"

        # The result of _execute_query is a generator, get the first (and only) item.
        return next(self._execute_query(query, params), 0)

    def execute_async(self, func, *args, **kwargs):
        return self.executor.submit(func, *args, **kwargs)

    def close(self):
        self.executor.shutdown()
        with self._lock:
            self._connection.close()
