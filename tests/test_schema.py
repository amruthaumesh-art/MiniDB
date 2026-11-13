import os
import tempfile
import unittest

from minidb.database import Database, DatabaseError


class SchemaTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        self.path = temp.name
        temp.close()

        self.db = Database(self.path)

        self.db.set_schema({
            "name": str,
            "semester": int,
            "cgpa": float
        })

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_valid_insert(self):
        record_id = self.db.insert({
            "name": "Asha",
            "semester": 5,
            "cgpa": 8.5
        })

        self.assertEqual(self.db.get(record_id)["name"], "Asha")

    def test_invalid_data_type_rejected(self):
        with self.assertRaises(DatabaseError):
            self.db.insert({
                "name": "Asha",
                "semester": "five",
                "cgpa": 8.5
            })

    def test_unknown_field_rejected(self):
        with self.assertRaises(DatabaseError):
            self.db.insert({
                "name": "Asha",
                "semester": 5,
                "cgpa": 8.5,
                "age": 21
            })

    def test_invalid_update_rejected(self):
        record_id = self.db.insert({
            "name": "Asha",
            "semester": 5,
            "cgpa": 8.5
        })

        with self.assertRaises(DatabaseError):
            self.db.update(record_id, {"semester": "six"})

        self.assertEqual(self.db.get(record_id)["semester"], 5)

    def test_valid_update(self):
        record_id = self.db.insert({
            "name": "Asha",
            "semester": 5,
            "cgpa": 8.5
        })

        self.db.update(record_id, {"semester": 6})

        self.assertEqual(self.db.get(record_id)["semester"], 6)


if __name__ == "__main__":
    unittest.main()