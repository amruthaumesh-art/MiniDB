import os
import tempfile
import unittest

from minidb.database import Database


class AggregationTests(unittest.TestCase):

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

    def test_count_all(self):
        result = self.db.execute("SELECT COUNT(*) FROM students")
        self.assertEqual(result, [{"COUNT(*)": 3}])
    def test_sum(self):
        result = self.db.execute(
            "SELECT SUM(semester) FROM students"
        )
        self.assertEqual(result, [{"SUM(semester)": 13}])

    def test_avg(self):
        result = self.db.execute(
            "SELECT AVG(semester) FROM students"
        )
        self.assertAlmostEqual(result[0]["AVG(semester)"], 13 / 3)

if __name__ == "__main__":
    unittest.main()