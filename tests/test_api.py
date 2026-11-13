import unittest
import os
import tempfile

from minidb.database import Database


class APITests(unittest.TestCase):

    def test_execute_select(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name

        try:
            db = Database(path)
            db.insert({"name": "Ananya", "semester": 6})

            result = db.execute(
                "SELECT * FROM students WHERE semester > 4"
            )

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["name"], "Ananya")
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()