"""Append-only file storage for MiniDB.

Each line is one JSON operation. The database rebuilds its current state by
replaying this log when it opens. This is an educational first storage layer,
not yet a full WAL/transaction implementation.
"""
import json
import os
from pathlib import Path
from typing import Any


class StorageError(Exception):
    """Raised when MiniDB cannot safely read or write its storage file."""


class StorageEngine:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def append(self, operation: dict[str, Any]) -> None:
        try:
            encoded = json.dumps(operation, separators=(",", ":"), ensure_ascii=False)
            with self.file_path.open("a", encoding="utf-8") as file:
                file.write(encoded + "\n")
                file.flush()
                os.fsync(file.fileno())
        except (OSError, TypeError, ValueError) as exc:
            raise StorageError(f"Could not append operation: {exc}") from exc

    def read_all(self) -> list[dict[str, Any]]:
        operations = []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                lines = file.readlines()

            for index, line in enumerate(lines):
                line_number = index + 1

                # An entry without a final newline is not committed.
                if index == len(lines) - 1 and not line.endswith("\n"):
                    break

                if not line.strip():
                    continue

                try:
                    item = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise StorageError(
                        f"Invalid log entry at line {line_number}: {exc}"
                    ) from exc

                if not isinstance(item, dict):
                    raise StorageError(
                        f"Log entry at line {line_number} is not an object"
                    )

                operations.append(item)

        except OSError as exc:
            raise StorageError(
                f"Could not read storage file: {exc}"
            ) from exc

        return operations
        return operations
        return operations
