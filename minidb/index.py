
class Index:
    """Simple in-memory index for faster record lookup."""

    def __init__(self, field):
        self.field = field
        self.entries = {}

    def add(self, value, record_id):
        """Add a record ID to the index."""
        try:
            self.entries.setdefault(value, set()).add(record_id)
        except TypeError:
            pass

    def remove(self, value, record_id):
        """Remove a record ID from the index."""
        try:
            if value in self.entries:
                self.entries[value].discard(record_id)

                if not self.entries[value]:
                    del self.entries[value]
        except TypeError:
            pass

    def search(self, value):
        """Find record IDs matching an exact value."""
        try:
            return set(self.entries.get(value, set()))
        except TypeError:
            return set()

    def clear(self):
        """Remove all index entries."""
        self.entries.clear()
