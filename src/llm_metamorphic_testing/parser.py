"""Parse model outputs into known intent labels."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from llm_metamorphic_testing.labels import LABELS, is_valid_label


_JSON_OBJECT_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class ParseResult:
    raw_output: str
    parsed_label: str | None
    is_valid_output: bool
    error: str | None = None


def parse_label(raw_output: str) -> ParseResult:
    """Parse the expected short JSON output: {"label": "<known_label>"}."""
    candidate = raw_output.strip()
    json_match = _JSON_OBJECT_PATTERN.search(candidate)
    if json_match is not None:
        candidate = json_match.group(0)

    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as exc:
        return ParseResult(
            raw_output=raw_output,
            parsed_label=None,
            is_valid_output=False,
            error=f"invalid_json: {exc.msg}",
        )

    if not isinstance(payload, dict):
        return ParseResult(raw_output, None, False, "json_not_object")

    label = payload.get("label")
    if not isinstance(label, str):
        return ParseResult(raw_output, None, False, "missing_label")

    if not is_valid_label(label):
        return ParseResult(raw_output, label, False, "unknown_label")

    return ParseResult(raw_output, label, True)


def parse_label_or_none(raw_output: str) -> str | None:
    result = parse_label(raw_output)
    return result.parsed_label if result.is_valid_output else None


__all__ = ["LABELS", "ParseResult", "parse_label", "parse_label_or_none"]

