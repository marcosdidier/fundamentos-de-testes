"""Load experiment cases from the project CSV datasets."""

from __future__ import annotations

import csv
from pathlib import Path

from llm_metamorphic_testing.schemas import ExperimentCase


def load_original_cases(path: str | Path) -> list[ExperimentCase]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        rows = csv.DictReader(source)
        return [
            ExperimentCase(
                case_id=row["original_input_id"],
                original_input_id=row["original_input_id"],
                transformation_type="original",
                original_text=row["text"],
                transformed_text=row["text"],
                expected_label=row["expected_label"],
                manual_review_notes=row.get("manual_review_notes", ""),
            )
            for row in rows
        ]


def load_transformed_cases(path: str | Path) -> list[ExperimentCase]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        rows = csv.DictReader(source)
        return [
            ExperimentCase(
                case_id=row["case_id"],
                original_input_id=row["original_input_id"],
                transformation_type=row["transformation_type"],  # type: ignore[arg-type]
                original_text=row["original_text"],
                transformed_text=row["transformed_text"],
                expected_label=row["expected_label"],
                manual_review_notes=row.get("manual_review_notes", ""),
            )
            for row in rows
        ]

