import os
import tempfile
import unittest

from minidb.database import Database


class SortingTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        self.path = temp.name
        temp.close()

        self.db = Database(self.path)

        self.db.insert({"name": "Asha", "semester": 3})
        self.db.insert({"name": "Ravi", "semester": 6})
        self.db.insert({"name": "Neha", "semester": 4})

    def tearDown(self):
        os.remove(self.path)

    def test_ascending_sort(self):
        result = self.db.execute(
            "SELECT * FROM students ORDER BY semester ASC"
        )
        semesters = [r["semester"] for r in result]
        self.assertEqual(semesters, [3, 4, 6])

    def test_descending_sort(self):
        result = self.db.execute(
            "SELECT * FROM students ORDER BY semester DESC"
        )
        semesters = [r["semester"] for r in result]
        self.assertEqual(semesters, [6, 4, 3])


if __name__ == "__main__":
    unittest.main()