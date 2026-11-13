
"""Public MiniDB API with storage, indexing, schema validation and transactions."""

from pathlib import Path
from typing import Any
from uuid import uuid4
from copy import deepcopy
from threading import RLock
from functools import wraps
from time import perf_counter

from .index import Index
from .executor import execute_query
from .storage import StorageEngine
from .plugins import PluginManager


def synchronized(method):
    """Serialize database operations using a re-entrant lock."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


class DatabaseError(Exception):
    """Base exception for database errors."""


class RecordNotFoundError(DatabaseError):
    """Raised when a requested record does not exist."""


class Database:

    def __init__(self, file_path: str | Path = "data/minidb.log"):
        self.storage = StorageEngine(file_path)
        self._lock = RLock()

        self.records: dict[str, dict[str, Any]] = {}
        self.indexes = {}
        self.schema = None
        self.plugins = PluginManager()

        self._transaction_snapshot = None
        self._transaction_operations = None

        self._recover()

    def register_plugin(self, name: str, plugin: Any) -> None:
        """Register a plugin with this database."""
        self.plugins.register(name, plugin)

    def activate_plugin(self, name: str) -> None:
        """Activate a registered plugin for this database."""
        self.plugins.activate(name, self)

    def list_plugins(self) -> list[str]:
        """List all registered plugins."""
        return self.plugins.list_plugins()

    def _recover(self):
        """Rebuild records by replaying committed operations."""

        def apply_operation(operation):
            action = operation.get("action")
            record_id = operation.get("id")

            if not isinstance(record_id, str):
                raise DatabaseError("Corrupt log: missing record id")

            if action in ("insert", "update"):
                document = operation.get("document")

                if not isinstance(document, dict):
                    raise DatabaseError("Corrupt log: invalid document")

                self.records[record_id] = document

            elif action == "delete":
                self.records.pop(record_id, None)

            else:
                raise DatabaseError(
                    f"Corrupt log: unknown action {action!r}"
                )

        for entry in self.storage.read_all():
            action = entry.get("action")

            if action == "transaction":
                operations = entry.get("operations")

                if not isinstance(operations, list):
                    raise DatabaseError("Corrupt transaction log")

                for operation in operations:
                    if not isinstance(operation, dict):
                        raise DatabaseError("Invalid transaction operation")

                for operation in operations:
                    apply_operation(operation)
            else:
                apply_operation(entry)

        self._rebuild_indexes()

    @synchronized
    def set_schema(self, schema: dict[str, type]):
        """Define allowed fields and their expected data types."""
        if not isinstance(schema, dict) or not schema:
            raise DatabaseError("Schema must be a non-empty dictionary")

        for field, expected_type in schema.items():
            if not isinstance(field, str) or not isinstance(expected_type, type):
                raise DatabaseError("Invalid schema definition")

        for document in self.records.values():
            self._validate_document(document, schema)

        self.schema = schema

    def _validate_document(self, document, schema=None):
        """Validate document fields and data types against the schema."""
        schema = schema if schema is not None else self.schema

        if schema is None:
            return

        unknown_fields = set(document) - set(schema)

        if unknown_fields:
            raise DatabaseError(
                f"Unknown fields: {', '.join(sorted(unknown_fields))}"
            )

        for field, value in document.items():
            expected_type = schema[field]

            if not isinstance(value, expected_type):
                raise DatabaseError(
                    f"Field '{field}' must be of type {expected_type.__name__}"
                )

    def _rebuild_indexes(self):
        """Rebuild all indexes from current records."""
        for field, index in self.indexes.items():
            index.clear()

            for record_id, document in self.records.items():
                if field in document:
                    index.add(document[field], record_id)

    def _write_operation(self, operation):
        """Buffer operations during a transaction."""
        if self._transaction_operations is not None:
            self._transaction_operations.append(operation)
        else:
            self.storage.append(operation)

    @synchronized
    def begin(self):
        """Start a thread-owned transaction."""
        if self._transaction_snapshot is not None:
            raise DatabaseError("Transaction already active")

        self._lock.acquire()

        try:
            self._transaction_snapshot = deepcopy(self.records)
            self._transaction_operations = []
            return "Transaction started"

        except Exception:
            self._lock.release()
            raise

    @synchronized
    def commit(self):
        """Atomically commit a transaction and release its lock."""
        if self._transaction_snapshot is None:
            raise DatabaseError("No active transaction")

        transaction = {
            "action": "transaction",
            "operations": self._transaction_operations
        }

        try:
            if self._transaction_operations:
                self.storage.append(transaction)

        except Exception:
            self.records = self._transaction_snapshot
            self._transaction_snapshot = None
            self._transaction_operations = None
            self._rebuild_indexes()
            raise

        else:
            self._transaction_snapshot = None
            self._transaction_operations = None
            return "Transaction committed"

        finally:
            self._lock.release()

    @synchronized
    def rollback(self):
        """Restore previous records and release the transaction lock."""
        if self._transaction_snapshot is None:
            raise DatabaseError("No active transaction")

        try:
            self.records = self._transaction_snapshot
            self._rebuild_indexes()
            return "Transaction rolled back"

        finally:
            self._transaction_snapshot = None
            self._transaction_operations = None
            self._lock.release()

    @synchronized
    def insert(self, document: dict[str, Any]) -> str:
        if not isinstance(document, dict):
            raise TypeError("document must be a dictionary")

        self._validate_document(document)

        record_id = str(uuid4())
        stored_document = dict(document)

        self._write_operation({
            "action": "insert",
            "id": record_id,
            "document": stored_document,
        })

        self.records[record_id] = stored_document

        for field, index in self.indexes.items():
            if field in stored_document:
                index.add(stored_document[field], record_id)

        return record_id

    @synchronized
    def get(self, record_id: str) -> dict[str, Any]:
        try:
            return dict(self.records[record_id])
        except KeyError as exc:
            raise RecordNotFoundError(
                f"No record found with id {record_id}"
            ) from exc

    @synchronized
    def all(self):
        return [
            {"_id": key, **dict(value)}
            for key, value in self.records.items()
        ]

    @synchronized
    def update(self, record_id: str, changes: dict[str, Any]):
        if record_id not in self.records:
            raise RecordNotFoundError(
                f"No record found with id {record_id}"
            )

        if not isinstance(changes, dict):
            raise TypeError("changes must be a dictionary")

        old_document = self.records[record_id]
        updated = {**old_document, **changes}

        self._validate_document(updated)

        self._write_operation({
            "action": "update",
            "id": record_id,
            "document": updated,
        })

        for field, index in self.indexes.items():
            if field in old_document:
                index.remove(old_document[field], record_id)

        self.records[record_id] = updated

        for field, index in self.indexes.items():
            if field in updated:
                index.add(updated[field], record_id)

    @synchronized
    def delete(self, record_id: str):
        if record_id not in self.records:
            raise RecordNotFoundError(
                f"No record found with id {record_id}"
            )

        old_document = self.records[record_id]

        self._write_operation({
            "action": "delete",
            "id": record_id,
        })

        for field, index in self.indexes.items():
            if field in old_document:
                index.remove(old_document[field], record_id)

        del self.records[record_id]

    @synchronized
    def create_index(self, field):
        """Create an index for a field."""
        if field in self.indexes:
            return "Index already exists"

        index = Index(field)

        for record_id, document in self.records.items():
            if field in document:
                index.add(document[field], record_id)

        self.indexes[field] = index

        return f"Index created for {field}"

    @synchronized
    def find_by_index(self, field, value):
        """Find records using an existing index."""
        if field not in self.indexes:
            raise DatabaseError(f"No index found for {field}")

        record_ids = self.indexes[field].search(value)

        return [
            {"_id": record_id, **dict(self.records[record_id])}
            for record_id in record_ids
            if record_id in self.records
        ]

    @synchronized
    
    
   
    @synchronized
    def execute(self, query: str):
        """Execute queries and notify registered plugins."""
        command = query.strip().upper()

        if command == "BEGIN":
            return self.begin()

        if command == "COMMIT":
            return self.commit()

        if command == "ROLLBACK":
            return self.rollback()

        start = perf_counter()

        try:
            result = execute_query(self, query)
        except Exception:
            elapsed_ms = (perf_counter() - start) * 1000

            for name in self.plugins.list_plugins():
                plugin = self.plugins.get(name)

                if hasattr(plugin, "record_execution"):
                    plugin.record_execution(query, elapsed_ms, False)

            raise

        elapsed_ms = (perf_counter() - start) * 1000

        for name in self.plugins.list_plugins():
            plugin = self.plugins.get(name)

            if hasattr(plugin, "record_query"):
                plugin.record_query(query)

            if hasattr(plugin, "record_execution"):
                plugin.record_execution(query, elapsed_ms, True)

        return result

