
import os
import tempfile
import unittest

from minidb import Database
from minidb.plugins.query_logger import QueryLogger
from minidb.plugins.query_stats import QueryStats


class PluginTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = temp.name
        temp.close()

        self.db = Database(self.db_path)

        self.logger = QueryLogger()
        self.stats = QueryStats()

        self.db.register_plugin("logger", self.logger)
        self.db.register_plugin("stats", self.stats)

        self.db.activate_plugin("logger")
        self.db.activate_plugin("stats")

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_plugin_registration(self):
        self.assertEqual(
            self.db.list_plugins(),
            ["logger", "stats"]
        )

    def test_automatic_query_logging(self):
        query = 'INSERT INTO students (name, semester) VALUES ("Ananya", 5)'
        self.db.execute(query)

        logs = self.logger.get_logs()

        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["query"], query)
        self.assertIn("timestamp", logs[0])

    def test_automatic_execution_statistics(self):
        query = 'INSERT INTO students (name, semester) VALUES ("Ananya", 5)'
        self.db.execute(query)

        statistics = self.stats.get_statistics()

        self.assertEqual(len(statistics), 1)
        self.assertEqual(statistics[0]["query"], query)
        self.assertGreaterEqual(
            statistics[0]["execution_time_ms"], 0
        )
        self.assertTrue(statistics[0]["success"])
        self.assertIn("timestamp", statistics[0])


if __name__ == "__main__":
    unittest.main()
