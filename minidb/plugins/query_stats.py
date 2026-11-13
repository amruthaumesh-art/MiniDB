
"""Query statistics plugin for MiniDB."""

from datetime import datetime, timezone
from time import perf_counter


class QueryStats:
    """Collect execution statistics for MiniDB queries."""

    def __init__(self):
        self.database = None
        self.statistics = []

    def activate(self, database):
        """Activate the statistics plugin."""
        self.database = database

    def record_execution(self, query, execution_time_ms, success=True):
        """Record an automatically measured query execution."""
        if self.database is None:
            raise RuntimeError("Activate the plugin first.")

        self.statistics.append({
            "query": query,
            "execution_time_ms": round(execution_time_ms, 4),
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def measure(self, query, operation):
        """Measure the execution time of a supplied operation."""
        if self.database is None:
            raise RuntimeError("Activate the plugin first.")

        start = perf_counter()
        success = False

        try:
            result = operation()
            success = True
            return result
        finally:
            elapsed_ms = (perf_counter() - start) * 1000
            self.record_execution(query, elapsed_ms, success)

    def get_statistics(self):
        """Return collected query statistics."""
        return list(self.statistics)

    def clear_statistics(self):
        """Clear collected statistics."""
        self.statistics.clear()
