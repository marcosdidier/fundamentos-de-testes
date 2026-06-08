"""Quantitative and qualitative analysis artifacts for the report."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable


REPORT_METRICS: tuple[tuple[str, str], ...] = (
    ("violation_rate_by_prompt_strategy", "Violation Rate by Prompt Strategy"),
    ("violation_rate_by_transformation_type", "Violation Rate by Transformation Type"),
    ("invalid_output_rate_by_prompt_strategy", "Invalid Output Rate by Prompt Strategy"),
    (
        "cost_per_detected_violation_by_prompt_strategy",
        "Cost per Detected Violation by Prompt Strategy",
    ),
)


REPRESENTATIVE_FAILURE_FIELDS: tuple[str, ...] = (
    "case_id",
    "original_input_id",
    "transformation_type",
    "expected_label",
    "prompt_strategy",
    "parsed_label",
    "is_valid_output",
    "is_violation_expected_label",
    "is_prediction_flip",
    "failure_category",
    "original_text",
    "transformed_text",
    "raw_output",
    "manual_review_notes",
)

PRECATEGORIZED_FAILURE_FIELDS: tuple[str, ...] = (
    *REPRESENTATIVE_FAILURE_FIELDS,
    "pre_categorization_notes",
)


def load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def build_report_tables(metric_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    for metric_name, title in REPORT_METRICS:
        rows = [row for row in metric_rows if row["metric"] == metric_name]
        tables[title] = [
            {
                "group": row["group"],
                "numerator": row["numerator"],
                "denominator": row["denominator"],
                "value": _format_metric_value(row["value"]),
            }
            for row in rows
        ]
    return tables


def write_report_tables_markdown(
    tables: dict[str, list[dict[str, str]]],
    path: str | Path,
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sections: list[str] = ["# Quantitative Analysis Tables", ""]
    for title, rows in tables.items():
        sections.extend([f"## {title}", ""])
        sections.append("| Group | Numerator | Denominator | Value |")
        sections.append("| --- | ---: | ---: | ---: |")
        for row in rows:
            sections.append(
                f"| {row['group']} | {row['numerator']} | {row['denominator']} | {row['value']} |"
            )
        sections.append("")

    output_path.write_text("\n".join(sections), encoding="utf-8")


def write_report_tables_csv(
    tables: dict[str, list[dict[str, str]]],
    path: str | Path,
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=("table", "group", "numerator", "denominator", "value"),
        )
        writer.writeheader()
        for table, rows in tables.items():
            for row in rows:
                writer.writerow({"table": table, **row})


def select_representative_failures(
    execution_rows: list[dict[str, str]],
    *,
    limit: int = 20,
) -> list[dict[str, str]]:
    failures = [
        row
        for row in execution_rows
        if row["is_violation_expected_label"] == "True" or row["is_valid_output"] != "True"
    ]

    selected: list[dict[str, str]] = []
    selected.extend(_take_by_strategy(failures, strategy="strict", limit=6))
    selected.extend(_take_by_strategy(failures, strategy="few_shot", limit=6))
    selected.extend(_take_by_strategy(failures, strategy="free", limit=8))

    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in selected:
        key = (row["case_id"], row["prompt_strategy"])
        if key not in seen:
            deduped.append(_representative_failure_row(row))
            seen.add(key)
        if len(deduped) == limit:
            break

    return deduped


def write_representative_failures(rows: Iterable[dict[str, str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=REPRESENTATIVE_FAILURE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def precategorize_representative_failures(
    rows: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    return [_precategorized_failure_row(row) for row in rows]


def write_precategorized_failures(rows: Iterable[dict[str, str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=PRECATEGORIZED_FAILURE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _take_by_strategy(
    failures: list[dict[str, str]],
    *,
    strategy: str,
    limit: int,
) -> list[dict[str, str]]:
    by_type: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in failures:
        if row["prompt_strategy"] == strategy:
            by_type[row["transformation_type"]].append(row)

    selected: list[dict[str, str]] = []
    for transformation_type in ("original", "paraphrase", "punctuation", "capitalization"):
        selected.extend(by_type[transformation_type][:2])
        if len(selected) >= limit:
            return selected[:limit]

    return selected[:limit]


def _representative_failure_row(row: dict[str, str]) -> dict[str, str]:
    return {
        field: row.get(field, "")
        for field in REPRESENTATIVE_FAILURE_FIELDS
        if field != "failure_category"
    } | {"failure_category": _initial_failure_category(row)}


def _initial_failure_category(row: dict[str, str]) -> str:
    if row["is_valid_output"] != "True":
        return "formatting failure"
    return "pending_manual_review"


def _precategorized_failure_row(row: dict[str, str]) -> dict[str, str]:
    category, notes = _precategorize_failure(row)
    return {
        field: row.get(field, "")
        for field in REPRESENTATIVE_FAILURE_FIELDS
        if field != "failure_category"
    } | {
        "failure_category": category,
        "pre_categorization_notes": notes,
    }


def _precategorize_failure(row: dict[str, str]) -> tuple[str, str]:
    if row["is_valid_output"] != "True":
        return (
            "formatting failure",
            "Saida nao seguiu o contrato esperado de JSON com label valido.",
        )

    expected_label = row["expected_label"]
    parsed_label = row["parsed_label"]
    text = row["transformed_text"].lower()

    if expected_label == "other" and parsed_label in {
        "account_support",
        "product_information",
    }:
        if any(term in text for term in ("politica de privacidade", "area comercial", "lojas parceiras")):
            return (
                "ambiguous input",
                "Mensagem rotulada como other pode ser interpretada como pedido de suporte/informacao pela taxonomia do modelo; requer revisao do rotulo esperado.",
            )
        return (
            "label confusion",
            "Modelo confundiu other com uma categoria especifica sem violar formato de saida.",
        )

    if row["transformation_type"] == "paraphrase":
        return (
            "paraphrase quality issue",
            "Falha ocorreu em parafrase; revisar se a transformacao preservou a intencao sem introduzir pista semantica nova.",
        )

    if row["is_prediction_flip"] == "True":
        return (
            "over-sensitivity to wording",
            "Predicao mudou em relacao ao caso original parseavel para a mesma estrategia.",
        )

    return (
        "semantic misunderstanding",
        "Saida valida com rotulo diferente do esperado; revisar entendimento semantico do caso.",
    )


def _format_metric_value(value: str) -> str:
    if not value:
        return ""
    numeric = float(value)
    return f"{numeric:.4f}"
