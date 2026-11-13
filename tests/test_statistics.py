
import os
import tempfile
import unittest

from minidb.database import Database


class StatisticsTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        self.path = temp.name
        temp.close()

        self.db = Database(self.path)

        self.db.insert({"name": "Asha", "semester": 5})
        self.db.insert({"name": "Ravi", "semester": 6})
        self.db.insert({"name": "Neha", "semester": 5})

        self.db.create_index("semester")

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_index_scan_statistics(self):
        self.db.execute(
            "SELECT * FROM students WHERE semester = 5"
        )

        stats = self.db.last_query_stats

        self.assertEqual(stats["scan_type"], "INDEX SCAN")
        self.assertEqual(stats["records_examined"], 2)
        self.assertEqual(stats["records_returned"], 2)
        self.assertGreaterEqual(stats["execution_time_ms"], 0)

    def test_full_scan_statistics(self):
        self.db.execute(
            "SELECT * FROM students WHERE semester > 5"
        )

        stats = self.db.last_query_stats

        self.assertEqual(stats["scan_type"], "FULL SCAN")
        self.assertEqual(stats["records_examined"], 3)
        self.assertEqual(stats["records_returned"], 1)

    def test_statistics_for_unindexed_field(self):
        self.db.execute(
            "SELECT * FROM students WHERE name = 'Ravi'"
        )

        stats = self.db.last_query_stats

        self.assertEqual(stats["scan_type"], "FULL SCAN")
        self.assertEqual(stats["records_examined"], 3)
        self.assertEqual(stats["records_returned"], 1)


if __name__ == "__main__":
    unittest.main()
