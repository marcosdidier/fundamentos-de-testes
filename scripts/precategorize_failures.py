from __future__ import annotations

import argparse
from pathlib import Path

from llm_metamorphic_testing.analysis import (
    load_csv,
    precategorize_representative_failures,
    write_precategorized_failures,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "processed" / "representative_failures.csv"
DEFAULT_OUTPUT = ROOT / "results" / "processed" / "representative_failures_precategorized.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pre-categorize representative failures.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_csv(args.input)
    precategorized = precategorize_representative_failures(rows)
    write_precategorized_failures(precategorized, args.output)
    print(f"input_rows={len(rows)}")
    print(f"output_rows={len(precategorized)}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()

