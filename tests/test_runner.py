import unittest
from collections.abc import Mapping
from typing import Any

from llm_metamorphic_testing.claude_client import CompletionResult
from llm_metamorphic_testing.prompts import PromptStrategy
from llm_metamorphic_testing.runner import run_case
from llm_metamorphic_testing.schemas import ExperimentCase


class FakeClient:
    model_name = "fake-claude"
    parameters: Mapping[str, Any] = {"temperature": 0}

    def complete(self, prompt: str) -> str:
        if "Quero cancelar meu pedido." not in prompt:
            raise AssertionError("Prompt did not include transformed text")
        return '{"label": "cancel_order"}'


class FakeClientWithUsage:
    model_name = "claude-haiku-4-5"
    parameters: Mapping[str, Any] = {"temperature": 0, "max_tokens": 64}

    def complete(self, _prompt: str) -> CompletionResult:
        return CompletionResult(
            raw_output='{"label": "cancel_order"}',
            usage={"input_tokens": 1_000, "output_tokens": 100, "total_tokens": 1_100},
        )


class FailingClient:
    model_name = "claude-haiku-4-5"
    parameters: Mapping[str, Any] = {"temperature": 0, "max_tokens": 64}

    def complete(self, _prompt: str) -> str:
        raise RuntimeError("api unavailable")


class RunnerTest(unittest.TestCase):
    def test_run_case_builds_execution_record(self) -> None:
        case = ExperimentCase(
            case_id="case-001",
            original_input_id="orig-001",
            transformation_type="original",
            original_text="Quero cancelar meu pedido.",
            transformed_text="Quero cancelar meu pedido.",
            expected_label="cancel_order",
        )

        record = run_case(case, PromptStrategy.STRICT, FakeClient())

        self.assertEqual(record.case_id, "case-001")
        self.assertEqual(record.prompt_strategy, "strict")
        self.assertEqual(record.parsed_label, "cancel_order")
        self.assertTrue(record.is_valid_output)
        self.assertFalse(record.is_violation_expected_label)
        self.assertIsNone(record.is_prediction_flip)
        self.assertIsNone(record.estimated_cost)

    def test_run_case_marks_prediction_flip(self) -> None:
        case = ExperimentCase(
            case_id="case-002",
            original_input_id="orig-001",
            transformation_type="paraphrase",
            original_text="Quero cancelar meu pedido.",
            transformed_text="Quero cancelar meu pedido.",
            expected_label="cancel_order",
        )

        record = run_case(
            case,
            PromptStrategy.STRICT,
            FakeClient(),
            original_prediction="refund_request",
        )

        self.assertTrue(record.is_prediction_flip)

    def test_run_case_records_usage_and_estimated_cost(self) -> None:
        case = ExperimentCase(
            case_id="case-003",
            original_input_id="orig-001",
            transformation_type="original",
            original_text="Quero cancelar meu pedido.",
            transformed_text="Quero cancelar meu pedido.",
            expected_label="cancel_order",
        )

        record = run_case(case, PromptStrategy.STRICT, FakeClientWithUsage())

        self.assertEqual(record.metadata["usage"]["total_tokens"], 1_100)
        self.assertEqual(record.estimated_cost, 0.0015)

    def test_run_case_records_api_error_as_invalid_output(self) -> None:
        case = ExperimentCase(
            case_id="case-004",
            original_input_id="orig-001",
            transformation_type="original",
            original_text="Quero cancelar meu pedido.",
            transformed_text="Quero cancelar meu pedido.",
            expected_label="cancel_order",
        )

        record = run_case(case, PromptStrategy.STRICT, FailingClient())

        self.assertFalse(record.is_valid_output)
        self.assertIsNone(record.parsed_label)
        self.assertIn("RuntimeError", record.metadata["api_error"])


if __name__ == "__main__":
    unittest.main()
