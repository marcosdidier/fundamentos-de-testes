import unittest

from llm_metamorphic_testing.parser import parse_label, parse_label_or_none


class ParserTest(unittest.TestCase):
    def test_parse_valid_json_label(self) -> None:
        result = parse_label('{"label": "cancel_order"}')

        self.assertTrue(result.is_valid_output)
        self.assertEqual(result.parsed_label, "cancel_order")
        self.assertIsNone(result.error)

    def test_parse_json_inside_extra_text(self) -> None:
        result = parse_label('Resultado: {"label": "delivery_problem"}')

        self.assertTrue(result.is_valid_output)
        self.assertEqual(result.parsed_label, "delivery_problem")

    def test_parse_invalid_json(self) -> None:
        result = parse_label("cancel_order")

        self.assertFalse(result.is_valid_output)
        self.assertIsNone(result.parsed_label)
        self.assertIsNotNone(result.error)

    def test_parse_unknown_label(self) -> None:
        result = parse_label('{"label": "refund"}')

        self.assertFalse(result.is_valid_output)
        self.assertEqual(result.parsed_label, "refund")
        self.assertEqual(result.error, "unknown_label")

    def test_parse_label_or_none(self) -> None:
        self.assertEqual(parse_label_or_none('{"label": "account_support"}'), "account_support")
        self.assertIsNone(parse_label_or_none('{"label": "unknown"}'))


if __name__ == "__main__":
    unittest.main()

