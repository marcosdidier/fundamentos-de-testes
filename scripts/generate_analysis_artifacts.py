from __future__ import annotations

import argparse
from pathlib import Path

from llm_metamorphic_testing.analysis import (
    build_report_tables,
    load_csv,
    select_representative_failures,
    write_report_tables_csv,
    write_report_tables_markdown,
    write_representative_failures,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METRICS = ROOT / "results" / "processed" / "metrics.csv"
DEFAULT_EXECUTIONS = ROOT / "results" / "processed" / "full_execution_results.csv"
DEFAULT_TABLES_MD = ROOT / "results" / "processed" / "analysis_tables.md"
DEFAULT_TABLES_CSV = ROOT / "results" / "processed" / "analysis_tables.csv"
DEFAULT_FAILURES = ROOT / "results" / "processed" / "representative_failures.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate phase 7 analysis artifacts.")
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--executions", type=Path, default=DEFAULT_EXECUTIONS)
    parser.add_argument("--tables-md", type=Path, default=DEFAULT_TABLES_MD)
    parser.add_argument("--tables-csv", type=Path, default=DEFAULT_TABLES_CSV)
    parser.add_argument("--failures-output", type=Path, default=DEFAULT_FAILURES)
    parser.add_argument("--failure-limit", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metric_rows = load_csv(args.metrics)
    execution_rows = load_csv(args.executions)

    tables = build_report_tables(metric_rows)
    failures = select_representative_failures(
        execution_rows,
        limit=args.failure_limit,
    )

    write_report_tables_markdown(tables, args.tables_md)
    write_report_tables_csv(tables, args.tables_csv)
    write_representative_failures(failures, args.failures_output)

    print(f"tables_md={args.tables_md}")
    print(f"tables_csv={args.tables_csv}")
    print(f"representative_failures={args.failures_output}")
    print(f"failure_rows={len(failures)}")


if __name__ == "__main__":
    main()

