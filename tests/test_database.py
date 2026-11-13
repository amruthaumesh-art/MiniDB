import tempfile
import unittest
from pathlib import Path

from minidb import Database
from minidb.database import RecordNotFoundError


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = Path(self.temp_dir.name) / "test.log"
        self.db = Database(self.db_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_insert_and_get(self):
        record_id = self.db.insert({"name": "Asha"})
        self.assertEqual(self.db.get(record_id), {"name": "Asha"})

    def test_update(self):
        record_id = self.db.insert({"name": "Asha", "year": 2})
        self.db.update(record_id, {"year": 3})
        self.assertEqual(self.db.get(record_id)["year"], 3)

    def test_delete(self):
        record_id = self.db.insert({"name": "Asha"})
        self.db.delete(record_id)
        with self.assertRaises(RecordNotFoundError):
            self.db.get(record_id)

    def test_recovery_after_reopen(self):
        record_id = self.db.insert({"name": "Asha"})
        reopened = Database(self.db_file)
        self.assertEqual(reopened.get(record_id), {"name": "Asha"})


if __name__ == "__main__":
    unittest.main()
