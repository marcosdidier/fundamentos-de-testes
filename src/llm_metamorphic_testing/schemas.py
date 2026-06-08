"""Data structures for experiment cases and execution records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from llm_metamorphic_testing.labels import is_valid_label


TransformationType = Literal["original", "paraphrase", "punctuation", "capitalization"]


@dataclass(frozen=True)
class ExperimentCase:
    case_id: str
    original_input_id: str
    transformation_type: TransformationType
    original_text: str
    transformed_text: str
    expected_label: str
    manual_review_notes: str = ""

    def __post_init__(self) -> None:
        if not is_valid_label(self.expected_label):
            raise ValueError(f"Unknown expected_label: {self.expected_label}")


@dataclass(frozen=True)
class ExecutionRecord:
    case_id: str
    original_input_id: str
    transformation_type: TransformationType
    original_text: str
    transformed_text: str
    expected_label: str
    prompt_strategy: str
    prompt_text: str
    model_name: str
    parameters: dict[str, Any]
    raw_output: str
    parsed_label: str | None
    is_valid_output: bool
    is_violation_expected_label: bool
    is_prediction_flip: bool | None
    execution_time: float
    estimated_cost: float | None
    timestamp: str
    manual_review_notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

