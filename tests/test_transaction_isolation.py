
import tempfile
import unittest
from pathlib import Path
from threading import Thread, Event

from minidb import Database


class TransactionIsolationTests(unittest.TestCase):

    def test_other_thread_waits_until_transaction_commits(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db = Database(Path(temp_dir) / "test.log")

            transaction_started = Event()
            allow_commit = Event()
            second_insert_done = Event()
            errors = []

            def first_thread():
                try:
                    db.begin()
                    db.insert({"name": "Transaction A"})
                    transaction_started.set()

                    if not allow_commit.wait(3):
                        raise TimeoutError("Commit permission timed out")

                    db.commit()
                except Exception as exc:
                    errors.append(exc)
                    transaction_started.set()

            def second_thread():
                try:
                    if not transaction_started.wait(3):
                        raise TimeoutError("Transaction did not start")

                    db.insert({"name": "Transaction B"})
                    second_insert_done.set()
                except Exception as exc:
                    errors.append(exc)

            thread_a = Thread(target=first_thread)
            thread_b = Thread(target=second_thread)

            thread_a.start()
            thread_b.start()

            try:
                self.assertTrue(transaction_started.wait(3))

                # Thread B should remain blocked before commit.
                blocked = not second_insert_done.wait(0.2)

            finally:
                allow_commit.set()
                thread_a.join(3)
                thread_b.join(3)

            self.assertFalse(thread_a.is_alive())
            self.assertFalse(thread_b.is_alive())
            self.assertTrue(blocked)
            self.assertEqual(errors, [])
            self.assertEqual(len(db.all()), 2)


if __name__ == "__main__":
    unittest.main()
