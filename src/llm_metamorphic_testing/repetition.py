"""Helpers for the 10% non-determinism repetition check."""

from __future__ import annotations

from dataclasses import replace
from collections import defaultdict
from typing import Iterable

from llm_metamorphic_testing.labels import LABELS
from llm_metamorphic_testing.schemas import ExperimentCase


def systematic_sample(cases: list[ExperimentCase], sample_size: int) -> list[ExperimentCase]:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if sample_size > len(cases):
        raise ValueError("sample_size cannot be greater than the number of cases")

    step = len(cases) / sample_size
    indexes = [int(index * step) for index in range(sample_size)]
    return [cases[index] for index in indexes]


def balanced_ten_percent_sample(cases: Iterable[ExperimentCase]) -> list[ExperimentCase]:
    by_label_and_type: dict[tuple[str, str], list[ExperimentCase]] = defaultdict(list)
    for case in cases:
        by_label_and_type[(case.expected_label, case.transformation_type)].append(case)

    sample: list[ExperimentCase] = []
    for label in LABELS:
        sample.extend(_take(by_label_and_type[(label, "original")], 1))
        sample.extend(_take(by_label_and_type[(label, "paraphrase")], 3))
        sample.extend(_take(by_label_and_type[(label, "punctuation")], 1))
        sample.extend(_take(by_label_and_type[(label, "capitalization")], 1))

    return sample


def build_repeated_cases(
    cases: Iterable[ExperimentCase],
    *,
    repetitions: int,
) -> list[ExperimentCase]:
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")

    repeated_cases: list[ExperimentCase] = []
    for repetition in range(1, repetitions + 1):
        for case in cases:
            repeated_cases.append(
                replace(
                    case,
                    case_id=f"{case.case_id}_repeat_{repetition:02d}",
                    manual_review_notes=_append_repetition_note(
                        case.manual_review_notes,
                        repetition,
                    ),
                )
            )
    return repeated_cases


def _append_repetition_note(existing_notes: str, repetition: int) -> str:
    repetition_note = f"repetition={repetition}"
    if not existing_notes:
        return repetition_note
    return f"{existing_notes}; {repetition_note}"


def _take(cases: list[ExperimentCase], count: int) -> list[ExperimentCase]:
    if len(cases) < count:
        raise ValueError("not enough cases for balanced sample")
    return cases[:count]
