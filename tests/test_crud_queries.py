
import unittest
import os
import tempfile

from minidb.database import Database


class CRUDQueryTests(unittest.TestCase):

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(delete=False)
        self.file.close()
        self.db = Database(self.file.name)

    def tearDown(self):
        os.remove(self.file.name)

    def test_insert_query(self):
        self.db.execute(
            'INSERT INTO students (name, semester) '
            'VALUES ("Ananya", 5)'
        )
        self.assertEqual(len(self.db.all()), 1)
        self.assertEqual(self.db.all()[0]["name"], "Ananya")

    def test_update_query(self):
        self.db.insert({"name": "Ananya", "semester": 5})

        count = self.db.execute(
            'UPDATE students SET semester=6 WHERE name="Ananya"'
        )

        self.assertEqual(count, 1)
        self.assertEqual(self.db.all()[0]["semester"], 6)

    def test_delete_query(self):
        self.db.insert({"name": "Ananya", "semester": 5})

        count = self.db.execute(
            'DELETE FROM students WHERE name="Ananya"'
        )

        self.assertEqual(count, 1)
        self.assertEqual(len(self.db.all()), 0)


if __name__ == "__main__":
    unittest.main()
