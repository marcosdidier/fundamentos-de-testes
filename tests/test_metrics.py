import unittest

from llm_metamorphic_testing.metrics import calculate_metric_rows, calculate_summary


class MetricsTest(unittest.TestCase):
    def test_calculate_summary(self) -> None:
        summary = calculate_summary(self._rows())

        self.assertEqual(summary["executions"], "4")
        self.assertEqual(summary["unique_cases"], "4")
        self.assertEqual(summary["total_api_cost"], "0.04")
        self.assertEqual(summary["total_violations_expected_label"], "2")
        self.assertEqual(summary["total_invalid_outputs"], "1")
        self.assertEqual(summary["average_response_time"], "0.25")

    def test_calculate_metric_rows(self) -> None:
        metric_rows = calculate_metric_rows(self._rows())
        by_key = {(row.metric, row.group): row for row in metric_rows}

        self.assertEqual(by_key[("invalid_output_rate", "all")].value, 0.25)
        self.assertEqual(
            by_key[("metamorphic_violation_rate", "all")].value,
            0.5,
        )
        self.assertEqual(
            by_key[("prediction_flip_rate", "all")].value,
            0.5,
        )
        self.assertEqual(
            by_key[("cost_per_detected_violation", "all")].value,
            0.02,
        )

    @staticmethod
    def _rows() -> list[dict[str, str]]:
        return [
            {
                "case_id": "orig-1",
                "transformation_type": "original",
                "prompt_strategy": "strict",
                "is_valid_output": "True",
                "is_violation_expected_label": "False",
                "is_prediction_flip": "",
                "execution_time": "0.1",
                "estimated_cost": "0.01",
            },
            {
                "case_id": "trans-1",
                "transformation_type": "paraphrase",
                "prompt_strategy": "strict",
                "is_valid_output": "True",
                "is_violation_expected_label": "True",
                "is_prediction_flip": "True",
                "execution_time": "0.2",
                "estimated_cost": "0.01",
            },
            {
                "case_id": "orig-2",
                "transformation_type": "original",
                "prompt_strategy": "free",
                "is_valid_output": "False",
                "is_violation_expected_label": "True",
                "is_prediction_flip": "",
                "execution_time": "0.3",
                "estimated_cost": "0.01",
            },
            {
                "case_id": "trans-2",
                "transformation_type": "punctuation",
                "prompt_strategy": "free",
                "is_valid_output": "True",
                "is_violation_expected_label": "False",
                "is_prediction_flip": "False",
                "execution_time": "0.4",
                "estimated_cost": "0.01",
            },
        ]


if __name__ == "__main__":
    unittest.main()
