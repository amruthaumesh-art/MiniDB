
"""Query logging plugin for MiniDB."""

from datetime import datetime, timezone


class QueryLogger:
    """Record query activity for monitoring and debugging."""

    def __init__(self):
        self.database = None
        self.logs = []

    def activate(self, database):
        """Activate the plugin for a MiniDB database."""
        self.database = database

    def record_query(self, query):
        """Record a query with its execution timestamp."""
        if self.database is None:
            raise RuntimeError("Activate the plugin before recording queries.")

        entry = {
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.logs.append(entry)
        return entry

    def get_logs(self):
        """Return all recorded query entries."""
        return list(self.logs)

    def clear_logs(self):
        """Clear recorded query entries."""
        self.logs.clear()
