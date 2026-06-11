from __future__ import annotations

import argparse
from pathlib import Path

from llm_metamorphic_testing.claude_client import ClaudeClient
from llm_metamorphic_testing.config import load_dotenv
from llm_metamorphic_testing.datasets import load_original_cases, load_transformed_cases
from llm_metamorphic_testing.executor import run_cases
from llm_metamorphic_testing.prompts import PromptStrategy
from llm_metamorphic_testing.storage import write_records_csv, write_records_jsonl


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATASET = ROOT / "data" / "original" / "original_dataset.csv"
TRANSFORMED_DATASET_V2 = ROOT / "data" / "transformed" / "transformed_dataset_v2.csv"
DEFAULT_CSV_OUTPUT = ROOT / "results" / "processed" / "v2_execution_results.csv"
DEFAULT_JSONL_OUTPUT = ROOT / "results" / "raw" / "v2_execution_logs.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the LLM metamorphic test experiment v2.")
    parser.add_argument(
        "--dataset",
        choices=("original", "transformed", "all"),
        default="all",
        help="Dataset subset to execute.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of cases to execute before applying prompt strategies.",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=DEFAULT_CSV_OUTPUT,
        help="Path for processed CSV results.",
    )
    parser.add_argument(
        "--jsonl-output",
        type=Path,
        default=DEFAULT_JSONL_OUTPUT,
        help="Path for raw JSONL logs.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=ROOT / ".env",
        help="Path to the local environment file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv(args.env_file)

    cases = []
    if args.dataset in {"original", "all"}:
        cases.extend(load_original_cases(ORIGINAL_DATASET))
    if args.dataset in {"transformed", "all"}:
        cases.extend(load_transformed_cases(TRANSFORMED_DATASET_V2))
    if args.limit is not None:
        cases = cases[: args.limit]

    client = ClaudeClient()
    # Run only STRICT and FEW_SHOT prompt strategies
    records = run_cases(
        cases,
        client,
        strategies=[PromptStrategy.STRICT, PromptStrategy.FEW_SHOT],
    )

    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    args.jsonl_output.parent.mkdir(parents=True, exist_ok=True)

    write_records_csv(records, args.csv_output)
    write_records_jsonl(records, args.jsonl_output)

    print(f"cases={len(cases)}")
    print(f"executions={len(records)}")
    print(f"csv={args.csv_output}")
    print(f"jsonl={args.jsonl_output}")


if __name__ == "__main__":
    main()
