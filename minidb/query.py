
import re


class QueryError(Exception):
    """Raised when a query is invalid."""


TOKEN_PATTERN = re.compile(
    r'''\s*(?:"([^"]*)"|'([^']*)'|(>=|<=|!=|=|>|<|\*|,|\(|\))|(-?\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z0-9_]*))'''
)


def tokenize(query):
    """Convert a query into tokens."""
    tokens = []
    position = 0

    while position < len(query):
        if query[position:].strip() == "":
            break

        match = TOKEN_PATTERN.match(query, position)

        if not match:
            raise QueryError(f"Invalid query near: {query[position:]}")

        if match.group(1) is not None:
            tokens.append('"' + match.group(1) + '"')
        elif match.group(2) is not None:
            tokens.append("'" + match.group(2) + "'")
        else:
            token = next(
                group for group in match.groups()[2:]
                if group is not None
            )
            tokens.append(token)

        position = match.end()

    return tokens


def parse(query):
    """Parse SELECT, INSERT, UPDATE and DELETE queries."""
    tokens = tokenize(query)

    if not tokens:
        raise QueryError("Empty query")

    command = tokens[0].upper()

    if command == "SELECT":
        upper = [t.upper() for t in tokens]

        if "FROM" not in upper:
            raise QueryError("Expected FROM")

        from_index = upper.index("FROM")
        fields = tokens[1:from_index]

        if from_index + 1 >= len(tokens):
            raise QueryError("Missing table name")

        table = tokens[from_index + 1]

               # Aggregate function support
        if (
            len(fields) == 4
            and fields[1] == "("
            and fields[3] == ")"
            and fields[0].upper() in ("COUNT", "SUM", "AVG")
        ):
            function = fields[0].upper()
            field = fields[2]

            if function == "COUNT" and field != "*":
                raise QueryError("Only COUNT(*) is supported")

            if function in ("SUM", "AVG") and field == "*":
                raise QueryError("SUM and AVG require a field")

            remaining = tokens[from_index + 2:]
            condition = None

            if remaining:
                if len(remaining) != 4 or remaining[0].upper() != "WHERE":
                    raise QueryError("Invalid WHERE clause")

                condition = {
                    "field": remaining[1],
                    "operator": remaining[2],
                    "value": remaining[3]
                }

            return {
                "type": "SELECT",
                "table": table,
                "fields": [f"{function}({field})"],
                "condition": condition,
                "order_by": None,
                "direction": "ASC"
            }

        if not fields or len(fields) % 2 == 0:
            raise QueryError("Invalid field list")

        if any(fields[i] != "," for i in range(1, len(fields), 2)):
            raise QueryError("Invalid field list")

        remaining = tokens[from_index + 2:]

        condition = None
        order_by = None
        direction = "ASC"

        order_index = next(
            (i for i, token in enumerate(remaining)
             if token.upper() == "ORDER"),
            len(remaining)
        )

        where_part = remaining[:order_index]
        order_part = remaining[order_index:]

        if where_part:
            if len(where_part) != 4 or where_part[0].upper() != "WHERE":
                raise QueryError("Invalid WHERE clause")

            condition = {
                "field": where_part[1],
                "operator": where_part[2],
                "value": where_part[3]
            }

        if order_part:
            if (
                len(order_part) not in (3, 4)
                or order_part[0].upper() != "ORDER"
                or order_part[1].upper() != "BY"
            ):
                raise QueryError("Invalid ORDER BY clause")

            order_by = order_part[2]

            if len(order_part) == 4:
                direction = order_part[3].upper()

                if direction not in ("ASC", "DESC"):
                    raise QueryError("Invalid sort direction")

        return {
            "type": "SELECT",
            "table": table,
            "fields": fields[::2],
            "condition": condition,
            "order_by": order_by,
            "direction": direction
        }

    if command == "INSERT":
        try:
            if tokens[1].upper() != "INTO" or tokens[3] != "(":
                raise QueryError("Invalid INSERT query")

            table = tokens[2]
            close_fields = tokens.index(")", 4)
            fields = tokens[4:close_fields]

            if tokens[close_fields + 1].upper() != "VALUES":
                raise QueryError("Expected VALUES")

            if tokens[close_fields + 2] != "(":
                raise QueryError("Expected values list")

            close_values = tokens.index(")", close_fields + 3)
            values = tokens[close_fields + 3:close_values]

            if close_values != len(tokens) - 1:
                raise QueryError("Unexpected tokens after INSERT")

            field_list = fields[::2]
            value_list = values[::2]

            if (
                len(field_list) != len(value_list)
                or not field_list
                or any(fields[i] != "," for i in range(1, len(fields), 2))
                or any(values[i] != "," for i in range(1, len(values), 2))
            ):
                raise QueryError("Invalid INSERT fields or values")

            return {
                "type": "INSERT",
                "table": table,
                "document": dict(zip(field_list, value_list))
            }

        except (IndexError, ValueError):
            raise QueryError("Invalid INSERT query")

    if command == "UPDATE":
        try:
            table = tokens[1]

            if tokens[2].upper() != "SET":
                raise QueryError("Expected SET")

            where_index = next(
                (i for i, token in enumerate(tokens)
                 if token.upper() == "WHERE"),
                len(tokens)
            )

            assignments = tokens[3:where_index]

            if len(assignments) < 3 or (len(assignments) + 1) % 4 != 0:
                raise QueryError("Invalid SET clause")

            changes = {}

            for i in range(0, len(assignments), 4):
                if assignments[i + 1] != "=":
                    raise QueryError("Expected = in SET")

                changes[assignments[i]] = assignments[i + 2]

                if i + 3 < len(assignments) and assignments[i + 3] != ",":
                    raise QueryError("Expected comma in SET")

            condition = None

            if where_index < len(tokens):
                remaining = tokens[where_index + 1:]

                if len(remaining) != 3:
                    raise QueryError("Invalid WHERE clause")

                condition = {
                    "field": remaining[0],
                    "operator": remaining[1],
                    "value": remaining[2]
                }

            return {
                "type": "UPDATE",
                "table": table,
                "changes": changes,
                "condition": condition
            }

        except IndexError:
            raise QueryError("Invalid UPDATE query")

    if command == "DELETE":
        try:
            if tokens[1].upper() != "FROM":
                raise QueryError("Expected FROM")

            table = tokens[2]
            condition = None

            if len(tokens) > 3:
                remaining = tokens[4:]

                if tokens[3].upper() != "WHERE" or len(remaining) != 3:
                    raise QueryError("Invalid DELETE WHERE clause")

                condition = {
                    "field": remaining[0],
                    "operator": remaining[1],
                    "value": remaining[2]
                }

            return {
                "type": "DELETE",
                "table": table,
                "condition": condition
            }

        except IndexError:
            raise QueryError("Invalid DELETE query")

    raise QueryError(f"Unsupported command: {command}")
