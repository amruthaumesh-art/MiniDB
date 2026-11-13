
"""Example of a custom plugin for MiniDB."""


class AuditPlugin:
    """Track database queries for a simple audit trail."""

    def __init__(self):
        self.database = None
        self.audit_records = []

    def activate(self, database):
        """Connect the plugin to a MiniDB database."""
        self.database = database

    def record_query(self, query):
        """Automatically record executed queries."""
        self.audit_records.append({
            "query": query,
            "status": "executed"
        })

    def get_audit_records(self):
        """Return all audit records."""
        return list(self.audit_records)
