import unittest
from collections.abc import Mapping
from typing import Any

from llm_metamorphic_testing.executor import run_cases
from llm_metamorphic_testing.prompts import PromptStrategy
from llm_metamorphic_testing.schemas import ExperimentCase


class EchoCancelClient:
    model_name = "fake-claude"
    parameters: Mapping[str, Any] = {"temperature": 0}

    def complete(self, _prompt: str) -> str:
        return '{"label": "cancel_order"}'


class ExecutorTest(unittest.TestCase):
    def test_run_cases_applies_all_strategies(self) -> None:
        cases = [
            ExperimentCase(
                case_id="orig-001",
                original_input_id="orig-001",
                transformation_type="original",
                original_text="Quero cancelar meu pedido.",
                transformed_text="Quero cancelar meu pedido.",
                expected_label="cancel_order",
            )
        ]

        records = run_cases(cases, EchoCancelClient())

        self.assertEqual(len(records), 3)
        self.assertEqual(
            {record.prompt_strategy for record in records},
            {"free", "strict", "few_shot"},
        )

    def test_run_cases_compares_transformed_with_original_prediction(self) -> None:
        cases = [
            ExperimentCase(
                case_id="orig-001",
                original_input_id="orig-001",
                transformation_type="original",
                original_text="Quero cancelar meu pedido.",
                transformed_text="Quero cancelar meu pedido.",
                expected_label="cancel_order",
            ),
            ExperimentCase(
                case_id="case-001",
                original_input_id="orig-001",
                transformation_type="paraphrase",
                original_text="Quero cancelar meu pedido.",
                transformed_text="Gostaria de cancelar a compra.",
                expected_label="cancel_order",
            ),
        ]

        records = run_cases(cases, EchoCancelClient(), strategies=(PromptStrategy.STRICT,))

        self.assertEqual(len(records), 2)
        self.assertIsNone(records[0].is_prediction_flip)
        self.assertFalse(records[1].is_prediction_flip)


if __name__ == "__main__":
    unittest.main()

