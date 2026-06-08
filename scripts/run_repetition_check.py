from __future__ import annotations

import argparse
from pathlib import Path

from llm_metamorphic_testing.claude_client import ClaudeClient
from llm_metamorphic_testing.config import load_dotenv
from llm_metamorphic_testing.datasets import load_original_cases, load_transformed_cases
from llm_metamorphic_testing.executor import run_cases
from llm_metamorphic_testing.repetition import (
    balanced_ten_percent_sample,
    build_repeated_cases,
    systematic_sample,
)
from llm_metamorphic_testing.storage import write_records_csv, write_records_jsonl


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATASET = ROOT / "data" / "original" / "original_dataset.csv"
TRANSFORMED_DATASET = ROOT / "data" / "transformed" / "transformed_dataset.csv"
DEFAULT_CSV_OUTPUT = ROOT / "results" / "processed" / "repetition_check_results.csv"
DEFAULT_JSONL_OUTPUT = ROOT / "results" / "raw" / "repetition_check_logs.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the 10% non-determinism repetition check.")
    parser.add_argument("--sample-size", type=int, default=42)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    parser.add_argument("--jsonl-output", type=Path, default=DEFAULT_JSONL_OUTPUT)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv(args.env_file)

    cases = load_original_cases(ORIGINAL_DATASET)
    cases.extend(load_transformed_cases(TRANSFORMED_DATASET))
    sample = (
        balanced_ten_percent_sample(cases)
        if args.sample_size == 42
        else systematic_sample(cases, args.sample_size)
    )
    repeated_cases = build_repeated_cases(sample, repetitions=args.repetitions)

    client = ClaudeClient()
    records = run_cases(repeated_cases, client)
    write_records_csv(records, args.csv_output)
    write_records_jsonl(records, args.jsonl_output)

    print(f"sample_cases={len(sample)}")
    print(f"repeated_cases={len(repeated_cases)}")
    print(f"executions={len(records)}")
    print(f"csv={args.csv_output}")
    print(f"jsonl={args.jsonl_output}")


if __name__ == "__main__":
    main()
