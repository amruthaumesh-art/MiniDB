
import os
import tempfile
import unittest

from minidb.database import Database, DatabaseError


class TransactionTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        self.path = temp.name
        temp.close()

        self.db = Database(self.path)
        self.record_id = self.db.insert({
            "name": "Asha",
            "semester": 5
        })

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_rollback(self):
        self.db.execute("BEGIN")
        self.db.update(self.record_id, {"semester": 6})
        self.db.execute("ROLLBACK")

        self.assertEqual(
            self.db.get(self.record_id)["semester"], 5
        )

    def test_commit(self):
        self.db.execute("BEGIN")
        self.db.update(self.record_id, {"semester": 6})
        self.db.execute("COMMIT")

        self.assertEqual(
            self.db.get(self.record_id)["semester"], 6
        )

    def test_nested_begin_rejected(self):
        self.db.execute("BEGIN")

        with self.assertRaises(DatabaseError):
            self.db.execute("BEGIN")

    def test_rollback_survives_restart(self):
        self.db.execute("BEGIN")
        self.db.update(self.record_id, {"semester": 8})
        self.db.execute("ROLLBACK")

        reopened_db = Database(self.path)

        self.assertEqual(
            reopened_db.get(self.record_id)["semester"], 5
        )

    def test_commit_survives_restart(self):
        self.db.execute("BEGIN")
        self.db.update(self.record_id, {"semester": 7})
        self.db.execute("COMMIT")

        reopened_db = Database(self.path)

        self.assertEqual(
            reopened_db.get(self.record_id)["semester"], 7
        )

    def test_recovery_ignores_incomplete_transaction(self):
        with open(self.path, "a", encoding="utf-8") as file:
            file.write(
                '{"action":"transaction","operations":['
                '{"action":"update","id":"'
                + self.record_id
                + '","document":{"name":"Asha","semester":99}}'
            )

        reopened_db = Database(self.path)

        self.assertEqual(
            reopened_db.get(self.record_id)["semester"], 5
        )

        with open(self.path, "a", encoding="utf-8") as file:
            file.write(
                '{"action":"transaction","operations":['
            )

        reopened_db = Database(self.path)

        self.assertEqual(
            reopened_db.get(self.record_id)["semester"], 5
        )
if __name__ == "__main__":
    unittest.main()
