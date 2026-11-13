
import unittest
import os
import tempfile

from minidb.database import Database
from minidb.executor import execute_select


class ExecutorTests(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

        self.db = Database(self.temp_file.name)

        self.db.insert({
            "name": "Ananya",
            "semester": 6
        })

        self.db.insert({
            "name": "Rahul",
            "semester": 4
        })

    def tearDown(self):
        os.remove(self.temp_file.name)

    def test_select_all(self):
        result = execute_select(
            self.db,
            "SELECT * FROM students"
        )
        self.assertEqual(len(result), 2)

    def test_where_condition(self):
        result = execute_select(
            self.db,
            "SELECT * FROM students WHERE semester > 4"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Ananya")

    def test_projection(self):
        result = execute_select(
            self.db,
            "SELECT name FROM students"
        )
        self.assertEqual(result[0]["name"], "Ananya")
        self.assertNotIn("semester", result[0])


if __name__ == "__main__":
    unittest.main()
