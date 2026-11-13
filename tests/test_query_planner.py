
import os
import tempfile
import unittest

from minidb.database import Database


class QueryPlannerTests(unittest.TestCase):

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

    def test_indexed_equality_query(self):
        result = self.db.execute(
            "SELECT * FROM students WHERE semester = 5"
        )

        self.assertEqual(len(result), 2)

        names = {record["name"] for record in result}
        self.assertEqual(names, {"Asha", "Neha"})

    def test_unindexed_query(self):
        result = self.db.execute(
            "SELECT * FROM students WHERE name = 'Ravi'"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Ravi")

    def test_range_query(self):
        result = self.db.execute(
            "SELECT * FROM students WHERE semester > 5"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Ravi")


if __name__ == "__main__":
    unittest.main()

