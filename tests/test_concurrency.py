import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

from minidb.database import Database


class ConcurrencyTests(unittest.TestCase):

    def test_multiple_threads_insert_records(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Database(f"{folder}/concurrency.log")

            def insert_records(thread_number):
                for i in range(20):
                    db.insert({
                        "thread": thread_number,
                        "number": i
                    })

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(insert_records, thread_number)
                    for thread_number in range(5)
                ]

                for future in futures:
                    future.result()

            records = db.all()

            self.assertEqual(len(records), 100)

            record_ids = [record["_id"] for record in records]
            self.assertEqual(len(record_ids), len(set(record_ids)))


if __name__ == "__main__":
    unittest.main()