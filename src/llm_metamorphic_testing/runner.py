"""Execution helpers that keep API access behind a small interface."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from time import perf_counter
from typing import Any, Protocol

from llm_metamorphic_testing.claude_client import CompletionResult
from llm_metamorphic_testing.costs import estimate_cost_usd
from llm_metamorphic_testing.parser import parse_label
from llm_metamorphic_testing.prompts import PromptStrategy, render_prompt
from llm_metamorphic_testing.schemas import ExecutionRecord, ExperimentCase


class LLMClient(Protocol):
    model_name: str
    parameters: Mapping[str, Any]

    def complete(self, prompt: str) -> str | CompletionResult:
        """Return the raw model output, optionally with usage metadata."""


def run_case(
    case: ExperimentCase,
    prompt_strategy: PromptStrategy | str,
    client: LLMClient,
    *,
    original_prediction: str | None = None,
) -> ExecutionRecord:
    prompt_text = render_prompt(prompt_strategy, case.transformed_text)

    started_at = perf_counter()
    try:
        completion = client.complete(prompt_text)
        api_error = None
    except Exception as exc:  # noqa: BLE001 - failures are recorded as experiment data.
        completion = ""
        api_error = f"{type(exc).__name__}: {exc}"
    execution_time = perf_counter() - started_at

    if isinstance(completion, CompletionResult):
        raw_output = completion.raw_output
        usage = completion.usage
    else:
        raw_output = completion
        usage = {"input_tokens": None, "output_tokens": None, "total_tokens": None}

    parse_result = parse_label(raw_output)
    parsed_label = parse_result.parsed_label if parse_result.is_valid_output else None
    estimated_cost = estimate_cost_usd(
        client.model_name,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
    )

    return ExecutionRecord(
        case_id=case.case_id,
        original_input_id=case.original_input_id,
        transformation_type=case.transformation_type,
        original_text=case.original_text,
        transformed_text=case.transformed_text,
        expected_label=case.expected_label,
        prompt_strategy=str(PromptStrategy(prompt_strategy).value),
        prompt_text=prompt_text,
        model_name=client.model_name,
        parameters=dict(client.parameters),
        raw_output=raw_output,
        parsed_label=parsed_label,
        is_valid_output=parse_result.is_valid_output,
        is_violation_expected_label=parsed_label != case.expected_label,
        is_prediction_flip=(
            None if original_prediction is None else parsed_label != original_prediction
        ),
        execution_time=execution_time,
        estimated_cost=estimated_cost,
        timestamp=datetime.now(UTC).isoformat(),
        manual_review_notes=case.manual_review_notes,
        metadata={
            "parse_error": parse_result.error,
            "api_error": api_error,
            "usage": usage,
        },
    )
