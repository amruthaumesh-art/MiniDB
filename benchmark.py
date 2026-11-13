
import time
import tempfile
from pathlib import Path

from minidb import Database


def measure_query(db, query, repetitions=20):
    # Warm-up
    db.execute(query)

    total_time = 0

    for _ in range(repetitions):
        start = time.perf_counter()
        result = db.execute(query)
        total_time += time.perf_counter() - start

    return (total_time / repetitions) * 1000


def run_benchmark(size):
    with tempfile.TemporaryDirectory() as temp_dir:
        db = Database(Path(temp_dir) / "benchmark.log")

        for i in range(size):
            db.insert({
                "student_id": i,
                "name": f"Student_{i}",
                "department": "CSE" if i % 2 == 0 else "ECE",
                "marks": i % 100
            })

        query = f"SELECT * FROM records WHERE student_id = {size // 2}"

        # Measure without index
        scan_time = measure_query(db, query)

        # Create index and measure the same query
        db.create_index("student_id")
        indexed_time = measure_query(db, query)

        return scan_time, indexed_time


def main():
    print("\nMINIDB PERFORMANCE BENCHMARK")
    print("-" * 65)
    print(f"{'Records':<15}{'Full Scan (ms)':<22}{'Indexed Query (ms)':<22}")
    print("-" * 65)

    for size in [100, 1000, 5000]:
        scan, indexed = run_benchmark(size)

        print(
            f"{size:<15}{scan:<22.4f}{indexed:<22.4f}"
        )

    print("-" * 65)
    print("Benchmark completed.")


if __name__ == "__main__":
    main()
