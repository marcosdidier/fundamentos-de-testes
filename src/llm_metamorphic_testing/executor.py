"""Run experiment cases across all prompt strategies."""

from __future__ import annotations

from collections.abc import Iterable

from llm_metamorphic_testing.prompts import PromptStrategy
from llm_metamorphic_testing.runner import LLMClient, run_case
from llm_metamorphic_testing.schemas import ExecutionRecord, ExperimentCase


def run_cases(
    cases: Iterable[ExperimentCase],
    client: LLMClient,
    *,
    strategies: Iterable[PromptStrategy] = tuple(PromptStrategy),
) -> list[ExecutionRecord]:
    records: list[ExecutionRecord] = []
    original_predictions: dict[tuple[str, str], str | None] = {}

    for case in cases:
        for strategy in strategies:
            strategy_value = strategy.value
            original_prediction = original_predictions.get(
                (case.original_input_id, strategy_value)
            )
            record = run_case(
                case,
                strategy,
                client,
                original_prediction=(
                    None if case.transformation_type == "original" else original_prediction
                ),
            )
            records.append(record)

            if case.transformation_type == "original":
                original_predictions[(case.original_input_id, strategy_value)] = (
                    record.parsed_label
                )

    return records

