"""Persist execution records in the formats required by the backlog."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from llm_metamorphic_testing.schemas import ExecutionRecord


COLLECTED_FIELDS: tuple[str, ...] = (
    "case_id",
    "original_input_id",
    "transformation_type",
    "original_text",
    "transformed_text",
    "expected_label",
    "prompt_strategy",
    "prompt_text",
    "model_name",
    "parameters",
    "raw_output",
    "parsed_label",
    "is_valid_output",
    "is_violation_expected_label",
    "is_prediction_flip",
    "execution_time",
    "estimated_cost",
    "timestamp",
    "manual_review_notes",
)


def write_records_csv(records: Iterable[ExecutionRecord], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=COLLECTED_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow(_csv_row(record))


def write_records_jsonl(records: Iterable[ExecutionRecord], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True))
            output.write("\n")


def _csv_row(record: ExecutionRecord) -> dict[str, Any]:
    payload = asdict(record)
    row = {field: payload[field] for field in COLLECTED_FIELDS}
    row["parameters"] = json.dumps(row["parameters"], ensure_ascii=False, sort_keys=True)
    return row

