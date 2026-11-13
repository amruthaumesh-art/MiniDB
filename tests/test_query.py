
import unittest

from minidb.query import tokenize, parse, QueryError


class QueryTests(unittest.TestCase):

    def test_tokenizer(self):
        tokens = tokenize(
            "SELECT * FROM students WHERE semester > 4"
        )
        self.assertEqual(
            tokens,
            ["SELECT", "*", "FROM", "students",
             "WHERE", "semester", ">", "4"]
        )

    def test_select_parser(self):
        result = parse(
            "SELECT * FROM students WHERE semester > 4"
        )

        self.assertEqual(result["type"], "SELECT")
        self.assertEqual(result["table"], "students")
        self.assertEqual(result["condition"]["field"], "semester")
        self.assertEqual(result["condition"]["operator"], ">")
        self.assertEqual(result["condition"]["value"], "4")

    def test_invalid_query(self):
        with self.assertRaises(QueryError):
            parse("INVALID QUERY")


if __name__ == "__main__":
    unittest.main()
