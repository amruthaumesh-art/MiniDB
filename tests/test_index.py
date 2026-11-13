
import os
import tempfile
import unittest

from minidb.database import Database, DatabaseError


class IndexTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        self.path = temp.name
        temp.close()

        self.db = Database(self.path)

        self.id1 = self.db.insert({
            "name": "Asha",
            "semester": 5
        })

        self.id2 = self.db.insert({
            "name": "Ravi",
            "semester": 6
        })

        self.id3 = self.db.insert({
            "name": "Neha",
            "semester": 5
        })

        self.db.create_index("semester")

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_index_search(self):
        results = self.db.find_by_index("semester", 5)

        self.assertEqual(
            {record["_id"] for record in results},
            {self.id1, self.id3}
        )

    def test_index_after_insert(self):
        new_id = self.db.insert({
            "name": "Kiran",
            "semester": 5
        })

        results = self.db.find_by_index("semester", 5)

        self.assertIn(new_id, {r["_id"] for r in results})

    def test_index_after_update(self):
        self.db.update(self.id1, {"semester": 7})

        self.assertEqual(
            self.db.find_by_index("semester", 5),
            [
                {
                    "_id": self.id3,
                    "name": "Neha",
                    "semester": 5
                }
            ]
        )

        results = self.db.find_by_index("semester", 7)
        self.assertEqual(results[0]["_id"], self.id1)

    def test_index_after_delete(self):
        self.db.delete(self.id1)

        results = self.db.find_by_index("semester", 5)

        self.assertEqual(
            {record["_id"] for record in results},
            {self.id3}
        )

    def test_index_after_rollback(self):
        self.db.execute("BEGIN")
        self.db.update(self.id1, {"semester": 8})
        self.db.execute("ROLLBACK")

        results = self.db.find_by_index("semester", 5)

        self.assertEqual(
            {record["_id"] for record in results},
            {self.id1, self.id3}
        )

    def test_missing_index(self):
        with self.assertRaises(DatabaseError):
            self.db.find_by_index("name", "Asha")


if __name__ == "__main__":
    unittest.main()
