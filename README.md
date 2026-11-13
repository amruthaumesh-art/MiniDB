# MiniDB – Custom Database and Query Execution Engine

A lightweight, extensible database engine built from scratch using Python.

## 1. Project Overview

MiniDB is an educational database management system that implements its own SQL-like query processing engine without using SQLite, DuckDB, or another full database engine as its core.

It demonstrates fundamental database internals, including custom query parsing, execution, persistent storage, indexing, query planning, transaction management, recovery, concurrency control, and extensible plugins.

 ## Installation from PyPI

MiniDB is publicly available on the Python Package Index (PyPI).

Install it using:

```bash
pip install minidb-engine
```

Import the database engine:

```python
from minidb import Database

db = Database("students.log")
```

**PyPI:** https://pypi.org/project/minidb-engine/

**Version:** 0.1.0

## 2. Project Objectives

- Build a custom tokenizer and query parser.
- Implement an internal query execution engine.
- Develop a persistent storage layer.
- Support CRUD operations and query filtering.
- Implement projection, sorting, and aggregation.
- Build indexing and basic query planning.
- Support transaction commit and rollback.
- Implement recovery of committed operations.
- Define thread-level concurrency behavior.
- Collect query execution statistics.
- Provide a reusable Python package with plugin support.

## 3. Technologies Used

- Python 3
- JSON-based persistent storage
- Python unittest
- Streamlit dashboard
- setuptools packaging
- Visual Studio Code

## 4. Architecture

MiniDB is organized into modular components:

| Module | Responsibility |
|---|---|
| `query.py` | Custom tokenization and query parsing |
| `executor.py` | Query execution |
| `database.py` | Public database API and transaction management |
| `storage.py` | Persistent JSON operation log |
| `index.py` | In-memory indexing |
| `plugins/manager.py` | Plugin registration and activation |
| `plugins/query_logger.py` | Automatic query logging |
| `plugins/query_stats.py` | Execution statistics |

### Query Processing Workflow

User Query → Tokenizer → Parser → Query Executor → Query Planner → Storage / Index → Query Result

### Plugin Workflow

Plugin Creation → Registration → Activation → Database Query Execution → Plugin Hooks

## 5. Implemented Features

### Query Processing
- Custom tokenizer and parser.
- INSERT, SELECT, UPDATE, and DELETE.
- WHERE-based filtering.
- Projection and sorting.
- COUNT, SUM, and AVG aggregations.

### Storage and Data Management
- Custom persistent JSON operation log.
- Record insertion, retrieval, updating, and deletion.
- Recovery by replaying committed operations.
- Optional schema and data-type validation.

### Indexing and Query Planning
- In-memory indexing.
- Index-based record retrieval.
- Basic rule-based query planning.
- Indexed and non-indexed query execution.
- Query execution statistics.

### Transactions and Reliability
- BEGIN, COMMIT, and ROLLBACK.
- Buffered transaction operations.
- Transaction batches written as a single log entry.
- Recovery that ignores incomplete final log entries.
- Thread-level synchronization using a re-entrant lock.
- Transaction isolation between threads.

### Plugin Architecture
- Plugin registration and activation.
- Plugin manager.
- Automatic query logging.
- Automatic execution-time measurement.
- Query success and failure statistics.
- Support for custom developer-created plugins.

## 6. Installation

Clone or download the project.

Navigate to the project directory:

```bash
cd minidb_starter
```

Install MiniDB in editable mode:

```bash
python -m pip install -e .
```

Import the database:

```python
from minidb import Database

db = Database("data/example.log")
```

## 7. Basic Usage

```python
from minidb import Database

db = Database("data/example.log")

db.execute(
    'INSERT INTO students (name, semester) VALUES ("Ananya", 5)'
)

result = db.execute("SELECT * FROM students")

print(result)
```

MiniDB supports INSERT, SELECT, UPDATE, and DELETE query operations.

## 8. Using Built-in Plugins

### Query Logger

```python
from minidb import Database
from minidb.plugins.query_logger import QueryLogger

db = Database("data/example.log")

logger = QueryLogger()

db.register_plugin("logger", logger)
db.activate_plugin("logger")

db.execute(
    'INSERT INTO students (name, semester) VALUES ("Ananya", 5)'
)

print(logger.get_logs())
```

### Query Statistics

```python
from minidb.plugins.query_stats import QueryStats

stats = QueryStats()

db.register_plugin("stats", stats)
db.activate_plugin("stats")

db.execute("SELECT * FROM students")

print(stats.get_statistics())
```

Statistics include execution time, success status, and timestamp.

## 9. Creating a Custom Plugin

Developers can extend MiniDB without modifying the core engine.

Example:

```python
class AuditPlugin:

    def activate(self, database):
        self.database = database
        self.records = []

    def record_query(self, query):
        self.records.append(query)
```

Register and activate the plugin:

```python
audit = AuditPlugin()

db.register_plugin("audit", audit)
db.activate_plugin("audit")
```

Plugins implementing `record_query()` are automatically notified after successful query execution.

See [Plugin Development Guide](docs/PLUGIN_GUIDE.md) for more details.

## 10. Running the Dashboard

Install Streamlit if it is not already installed:

```bash
python -m pip install streamlit
```

Start the dashboard:

```bash
streamlit run app.py
```

## 11. Running Automated Tests

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

The project currently contains 47 passing automated tests covering database functionality and plugin integration.

## 12. Benchmarking

Run the benchmark script:

```bash
python benchmark.py
```

An example benchmark run produced the following results:

| Dataset Size | Full Scan (ms) | Indexed Query (ms) |
|---:|---:|---:|
| 100 | 0.2376 | 0.0929 |
| 1,000 | 1.2538 | 0.0637 |
| 5,000 | 6.0168 | 0.0635 |

These are example measurements from one run. Actual performance depends on the hardware, dataset, and execution conditions.

## 13. Project Structure

```text
minidb_starter/
│
├── minidb/
│   ├── __init__.py
│   ├── database.py
│   ├── executor.py
│   ├── index.py
│   ├── query.py
│   ├── storage.py
│   └── plugins/
│       ├── __init__.py
│       ├── manager.py
│       ├── query_logger.py
│       └── query_stats.py
│
├── tests/
├── examples/
│   └── custom_plugin.py
├── docs/
│   └── PLUGIN_GUIDE.md
├── data/
├── app.py
├── demo.py
├── benchmark.py
├── pyproject.toml
└── README.md
```

## 14. Current Limitations

- MiniDB is an educational database engine, not a production-grade database.
- Indexes are maintained in memory and rebuilt when the database is reopened.
- The query planner uses basic rules rather than a cost-based optimization model.
- Concurrency protection is thread-level within a database instance; multi-process coordination is not implemented.
- The recovery mechanism is a simplified operation-log approach, not a full production-grade WAL.
- Plugin isolation and automatic third-party plugin discovery are not implemented.
- Supported SQL-like syntax is intentionally limited.

## 15. Future Improvements

- More SQL operations and query capabilities.
- Advanced query optimization.
- Improved crash recovery.
- More indexing strategies.
- Plugin discovery and distribution.
- Better concurrency and multi-process support.
- Expanded benchmarking and performance analysis.

## 16. Project Purpose

MiniDB is designed to demonstrate how database engines work internally while providing a reusable Python library and an extensible plugin architecture.

It is intended for learning, experimentation, and further development.
