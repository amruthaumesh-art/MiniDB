
import time

from .query import parse, QueryError


def convert_value(value):
    """Convert query values into Python data types."""
    value = value.strip()

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]

    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def matches(record, condition):
    """Check whether a record satisfies a WHERE condition."""
    if condition is None:
        return True

    field = condition["field"]
    operator = condition["operator"]
    expected = convert_value(condition["value"])
    actual = record.get(field)

    if actual is None:
        return False

    try:
        if operator == "=":
            return actual == expected
        if operator == "!=":
            return actual != expected
        if operator == ">":
            return actual > expected
        if operator == "<":
            return actual < expected
        if operator == ">=":
            return actual >= expected
        if operator == "<=":
            return actual <= expected
    except TypeError:
        return False

    raise QueryError(f"Unsupported operator: {operator}")


def save_statistics(database, scan_type, examined, returned, start):
    """Save statistics about the latest SELECT query."""
    database.last_query_stats = {
        "scan_type": scan_type,
        "records_examined": examined,
        "records_returned": returned,
        "execution_time_ms": round(
            (time.perf_counter() - start) * 1000, 4
        )
    }


def execute_select(database, query):
    """Execute SELECT and collect query statistics."""
    start = time.perf_counter()
    parsed = parse(query)
    condition = parsed["condition"]

    # Basic query planner.
    if (
        condition is not None
        and condition["operator"] == "="
        and condition["field"] in database.indexes
    ):
        value = convert_value(condition["value"])

        candidates = database.find_by_index(
            condition["field"], value
        )

        scan_type = "INDEX SCAN"
        examined = len(candidates)

    else:
        candidates = database.all()
        scan_type = "FULL SCAN"
        examined = len(candidates)

    filtered = [
        record for record in candidates
        if matches(record, condition)
    ]

    # Handle COUNT.
    aggregate = parsed["fields"][0]

    if aggregate == "COUNT(*)":
        result = [{"COUNT(*)": len(filtered)}]

    elif aggregate.startswith("SUM("):
        field = aggregate[4:-1]

        values = [
            record[field] for record in filtered
            if isinstance(record.get(field), (int, float))
            and not isinstance(record.get(field), bool)
        ]

        result = [{aggregate: sum(values)}]

    elif aggregate.startswith("AVG("):
        field = aggregate[4:-1]

        values = [
            record[field] for record in filtered
            if isinstance(record.get(field), (int, float))
            and not isinstance(record.get(field), bool)
        ]

        average = sum(values) / len(values) if values else 0
        result = [{aggregate: average}]

    else:
        # Apply ORDER BY.
        order_by = parsed.get("order_by")
        direction = parsed.get("direction", "ASC")

        if order_by:
            filtered.sort(
                key=lambda record: (
                    record.get(order_by) is None,
                    record.get(order_by)
                ),
                reverse=(direction == "DESC")
            )

        # Apply field projection.
        fields = parsed["fields"]

        if fields == ["*"]:
            result = filtered
        else:
            result = [
                {
                    "_id": record["_id"],
                    **{
                        field: record[field]
                        for field in fields
                        if field in record
                    }
                }
                for record in filtered
            ]

    save_statistics(
        database,
        scan_type,
        examined,
        len(result),
        start
    )

    return result


def execute_query(database, query):
    """Execute SELECT, INSERT, UPDATE and DELETE."""
    parsed = parse(query)
    command = parsed["type"]

    if command == "SELECT":
        return execute_select(database, query)

    if command == "INSERT":
        document = {
            field: convert_value(value)
            for field, value in parsed["document"].items()
        }

        return database.insert(document)

    if command == "UPDATE":
        changes = {
            field: convert_value(value)
            for field, value in parsed["changes"].items()
        }

        count = 0

        for record in database.all():
            if matches(record, parsed["condition"]):
                database.update(record["_id"], changes)
                count += 1

        return count

    if command == "DELETE":
        count = 0

        for record in database.all():
            if matches(record, parsed["condition"]):
                database.delete(record["_id"])
                count += 1

        return count

    raise QueryError("Unsupported query")
