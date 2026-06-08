import unittest

from llm_metamorphic_testing.analysis import (
    build_report_tables,
    precategorize_representative_failures,
    select_representative_failures,
)


class AnalysisTest(unittest.TestCase):
    def test_build_report_tables_formats_selected_metrics(self) -> None:
        tables = build_report_tables(
            [
                {
                    "metric": "violation_rate_by_prompt_strategy",
                    "group": "strict",
                    "numerator": "1",
                    "denominator": "10",
                    "value": "0.1",
                },
                {
                    "metric": "invalid_output_rate_by_prompt_strategy",
                    "group": "free",
                    "numerator": "10",
                    "denominator": "10",
                    "value": "1.0",
                },
            ]
        )

        self.assertIn("Violation Rate by Prompt Strategy", tables)
        self.assertEqual(
            tables["Violation Rate by Prompt Strategy"][0],
            {
                "group": "strict",
                "numerator": "1",
                "denominator": "10",
                "value": "0.1000",
            },
        )
        self.assertEqual(
            tables["Invalid Output Rate by Prompt Strategy"][0]["value"],
            "1.0000",
        )

    def test_select_representative_failures_prioritizes_failures(self) -> None:
        rows = [
            self._row("case-1", "strict", "paraphrase", valid=True, violation=True),
            self._row("case-2", "free", "original", valid=False, violation=True),
            self._row("case-3", "few_shot", "punctuation", valid=True, violation=False),
        ]

        failures = select_representative_failures(rows, limit=10)

        self.assertEqual(len(failures), 2)
        self.assertEqual(failures[0]["failure_category"], "pending_manual_review")
        self.assertEqual(failures[1]["failure_category"], "formatting failure")

    def test_precategorize_representative_failures(self) -> None:
        rows = [
            self._row("case-1", "free", "original", valid=False, violation=True),
            self._row(
                "case-2",
                "strict",
                "original",
                valid=True,
                violation=True,
                expected_label="other",
                parsed_label="account_support",
                text="Onde encontro a politica de privacidade do site?",
            ),
        ]

        precategorized = precategorize_representative_failures(rows)

        self.assertEqual(precategorized[0]["failure_category"], "formatting failure")
        self.assertEqual(precategorized[1]["failure_category"], "ambiguous input")
        self.assertIn("requer revisao", precategorized[1]["pre_categorization_notes"])

    @staticmethod
    def _row(
        case_id: str,
        strategy: str,
        transformation_type: str,
        *,
        valid: bool,
        violation: bool,
        expected_label: str = "cancel_order",
        parsed_label: str = "refund_request",
        text: str = "Gostaria de cancelar a compra.",
    ) -> dict[str, str]:
        return {
            "case_id": case_id,
            "original_input_id": "orig-1",
            "transformation_type": transformation_type,
            "expected_label": expected_label,
            "prompt_strategy": strategy,
            "parsed_label": "" if not valid else parsed_label,
            "is_valid_output": "True" if valid else "False",
            "is_violation_expected_label": "True" if violation else "False",
            "is_prediction_flip": "",
            "original_text": "Quero cancelar meu pedido.",
            "transformed_text": text,
            "raw_output": "raw",
            "manual_review_notes": "",
        }


if __name__ == "__main__":
    unittest.main()
