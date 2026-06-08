"""Metrics for the LLM metamorphic testing experiment."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class MetricRow:
    metric: str
    group: str
    numerator: int
    denominator: int
    value: float | None


def load_execution_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def calculate_metric_rows(rows: list[dict[str, str]]) -> list[MetricRow]:
    metric_rows: list[MetricRow] = []

    metric_rows.extend(_rate_by_group(rows, "invalid_output_rate", "all", _is_invalid))
    metric_rows.extend(
        _rate_by_group(rows, "invalid_output_rate_by_prompt_strategy", "prompt_strategy", _is_invalid)
    )
    metric_rows.extend(
        _rate_by_group(
            _transformed_rows(rows),
            "metamorphic_violation_rate",
            "all",
            _is_violation,
        )
    )
    metric_rows.extend(
        _rate_by_group(
            _transformed_rows(rows),
            "violation_rate_by_transformation_type",
            "transformation_type",
            _is_violation,
        )
    )
    metric_rows.extend(
        _rate_by_group(
            _transformed_rows(rows),
            "violation_rate_by_prompt_strategy",
            "prompt_strategy",
            _is_violation,
        )
    )
    metric_rows.extend(_prediction_flip_rates(rows))
    metric_rows.extend(_average_response_time(rows))
    metric_rows.extend(_cost_per_detected_violation(rows))

    return metric_rows


def calculate_summary(rows: list[dict[str, str]]) -> dict[str, str]:
    total_cost = sum((_decimal(row["estimated_cost"]) for row in rows), Decimal("0"))
    total_violations = sum(1 for row in rows if _is_violation(row))
    total_invalid = sum(1 for row in rows if _is_invalid(row))

    return {
        "executions": str(len(rows)),
        "unique_cases": str(len({row["case_id"] for row in rows})),
        "total_api_cost": str(total_cost),
        "total_violations_expected_label": str(total_violations),
        "total_invalid_outputs": str(total_invalid),
        "average_response_time": _format_float(_average(_float(row["execution_time"]) for row in rows)),
    }


def write_metric_rows(metric_rows: Iterable[MetricRow], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=("metric", "group", "numerator", "denominator", "value"),
        )
        writer.writeheader()
        for row in metric_rows:
            writer.writerow(
                {
                    "metric": row.metric,
                    "group": row.group,
                    "numerator": row.numerator,
                    "denominator": row.denominator,
                    "value": "" if row.value is None else row.value,
                }
            )


def write_summary(summary: dict[str, str], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=("field", "value"))
        writer.writeheader()
        for field, value in summary.items():
            writer.writerow({"field": field, "value": value})


def _rate_by_group(
    rows: list[dict[str, str]],
    metric: str,
    group_field: str,
    predicate,
) -> list[MetricRow]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    if group_field == "all":
        grouped["all"] = rows
    else:
        for row in rows:
            grouped[row[group_field]].append(row)

    return [
        MetricRow(
            metric=metric,
            group=group,
            numerator=sum(1 for row in group_rows if predicate(row)),
            denominator=len(group_rows),
            value=_safe_rate(sum(1 for row in group_rows if predicate(row)), len(group_rows)),
        )
        for group, group_rows in sorted(grouped.items())
    ]


def _prediction_flip_rates(rows: list[dict[str, str]]) -> list[MetricRow]:
    comparable_rows = [row for row in rows if row["is_prediction_flip"] in {"True", "False"}]
    metric_rows = _rate_by_group(
        comparable_rows,
        "prediction_flip_rate",
        "all",
        lambda row: row["is_prediction_flip"] == "True",
    )
    metric_rows.extend(
        _rate_by_group(
            comparable_rows,
            "prediction_flip_rate_by_prompt_strategy",
            "prompt_strategy",
            lambda row: row["is_prediction_flip"] == "True",
        )
    )
    return metric_rows


def _average_response_time(rows: list[dict[str, str]]) -> list[MetricRow]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["prompt_strategy"]].append(row)

    metric_rows = [
        MetricRow(
            metric="average_response_time",
            group="all",
            numerator=len(rows),
            denominator=len(rows),
            value=_average(_float(row["execution_time"]) for row in rows),
        )
    ]
    metric_rows.extend(
        MetricRow(
            metric="average_response_time_by_prompt_strategy",
            group=group,
            numerator=len(group_rows),
            denominator=len(group_rows),
            value=_average(_float(row["execution_time"]) for row in group_rows),
        )
        for group, group_rows in sorted(grouped.items())
    )
    return metric_rows


def _cost_per_detected_violation(rows: list[dict[str, str]]) -> list[MetricRow]:
    total_cost = sum((_decimal(row["estimated_cost"]) for row in rows), Decimal("0"))
    total_violations = sum(1 for row in rows if _is_violation(row))
    metric_rows = [
        MetricRow(
            metric="cost_per_detected_violation",
            group="all",
            numerator=int(total_cost * Decimal("1000000")),
            denominator=total_violations,
            value=None if total_violations == 0 else float(total_cost / total_violations),
        )
    ]

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["prompt_strategy"]].append(row)

    for group, group_rows in sorted(grouped.items()):
        group_cost = sum((_decimal(row["estimated_cost"]) for row in group_rows), Decimal("0"))
        group_violations = sum(1 for row in group_rows if _is_violation(row))
        metric_rows.append(
            MetricRow(
                metric="cost_per_detected_violation_by_prompt_strategy",
                group=group,
                numerator=int(group_cost * Decimal("1000000")),
                denominator=group_violations,
                value=None if group_violations == 0 else float(group_cost / group_violations),
            )
        )

    return metric_rows


def _transformed_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["transformation_type"] != "original"]


def _is_invalid(row: dict[str, str]) -> bool:
    return row["is_valid_output"] != "True"


def _is_violation(row: dict[str, str]) -> bool:
    return row["is_violation_expected_label"] == "True"


def _safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _average(values: Iterable[float]) -> float | None:
    value_list = list(values)
    if not value_list:
        return None
    return sum(value_list) / len(value_list)


def _float(value: str) -> float:
    return float(value) if value else 0.0


def _decimal(value: str) -> Decimal:
    return Decimal(value) if value else Decimal("0")


def _format_float(value: float | None) -> str:
    return "" if value is None else str(value)

