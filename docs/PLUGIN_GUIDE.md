# MiniDB Plugin Development Guide

## 1. Introduction

MiniDB supports an extensible plugin architecture.
Developers can create custom plugins without modifying
the core database engine.

## 2. Plugin Requirements

Every plugin must implement:

    activate(database)

This method receives the MiniDB database instance.

## 3. Registering a Plugin

    from minidb import Database
    from minidb.plugins.query_logger import QueryLogger

    db = Database("data/example.log")

    logger = QueryLogger()

    db.register_plugin("logger", logger)
    db.activate_plugin("logger")

## 4. Creating a Custom Plugin

    class MyPlugin:

        def activate(self, database):
            self.database = database

        def record_query(self, query):
            print("Executed:", query)

Register and activate it:

    plugin = MyPlugin()

    db.register_plugin("my_plugin", plugin)
    db.activate_plugin("my_plugin")

Plugins implementing record_query are automatically
notified after successful query execution.

## 5. Built-in Plugins

- QueryLogger: records executed queries and timestamps.
- QueryStats: records execution time and success status.
- PluginManager: manages plugin registration and activation.

## 6. Running Tests

    python -m unittest discover -s tests -v

## 7. Current Limitations

- Plugins currently run within the database execution flow.
- Plugin persistence is not provided automatically.
- Plugin isolation and third-party plugin discovery are not implemented.
- MiniDB is an educational database engine, not a production database.
