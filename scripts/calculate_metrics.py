from __future__ import annotations

import argparse
from pathlib import Path

from llm_metamorphic_testing.metrics import (
    calculate_metric_rows,
    calculate_summary,
    load_execution_rows,
    write_metric_rows,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "processed" / "full_execution_results.csv"
DEFAULT_METRICS_OUTPUT = ROOT / "results" / "processed" / "metrics.csv"
DEFAULT_SUMMARY_OUTPUT = ROOT / "results" / "processed" / "summary.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate experiment metrics.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--metrics-output", type=Path, default=DEFAULT_METRICS_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_execution_rows(args.input)
    metric_rows = calculate_metric_rows(rows)
    summary = calculate_summary(rows)
    write_metric_rows(metric_rows, args.metrics_output)
    write_summary(summary, args.summary_output)

    print(f"input_rows={len(rows)}")
    print(f"metrics={args.metrics_output}")
    print(f"summary={args.summary_output}")


if __name__ == "__main__":
    main()

