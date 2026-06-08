import unittest

from llm_metamorphic_testing.labels import LABELS, is_valid_label


class LabelsTest(unittest.TestCase):
    def test_labels_match_backlog(self) -> None:
        self.assertEqual(
            LABELS,
            (
                "refund_request",
                "cancel_order",
                "delivery_problem",
                "payment_issue",
                "product_information",
                "account_support",
                "other",
            ),
        )

    def test_is_valid_label(self) -> None:
        self.assertTrue(is_valid_label("refund_request"))
        self.assertFalse(is_valid_label("refund"))


if __name__ == "__main__":
    unittest.main()

