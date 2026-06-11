from __future__ import annotations

import argparse
from pathlib import Path

from llm_metamorphic_testing.claude_client import ClaudeClient
from llm_metamorphic_testing.config import load_dotenv
from llm_metamorphic_testing.datasets import load_original_cases, load_transformed_cases
from llm_metamorphic_testing.executor import run_cases
from llm_metamorphic_testing.prompts import PromptStrategy


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATASET = ROOT / "data" / "original" / "original_dataset.csv"

# Transformed datasets
TRANSFORMED_DATASET_V1 = ROOT / "data" / "transformed" / "transformed_dataset.csv"
TRANSFORMED_DATASET_V2 = ROOT / "data" / "transformed" / "transformed_dataset_v2.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the LLM metamorphic test experiment.")
    parser.add_argument(
        "--version",
        choices=("v1", "v2"),
        default="v2",
        help="Which version of the experiment to run (v1 or v2).",
    )
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
        default=None,
        help="Path for processed CSV results (defaults match version).",
    )
    parser.add_argument(
        "--jsonl-output",
        type=Path,
        default=None,
        help="Path for raw JSONL logs (defaults match version).",
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

    # Set up version defaults
    if args.version == "v1":
        transformed_path = TRANSFORMED_DATASET_V1
        csv_output = args.csv_output or ROOT / "results" / "processed" / "full_execution_results.csv"
        jsonl_output = args.jsonl_output or ROOT / "results" / "raw" / "full_execution_logs.jsonl"
        strategies = [PromptStrategy.FREE, PromptStrategy.STRICT, PromptStrategy.FEW_SHOT]
    else:
        transformed_path = TRANSFORMED_DATASET_V2
        csv_output = args.csv_output or ROOT / "results" / "processed" / "v2_execution_results.csv"
        jsonl_output = args.jsonl_output or ROOT / "results" / "raw" / "v2_execution_logs.jsonl"
        strategies = [PromptStrategy.STRICT, PromptStrategy.FEW_SHOT]

    cases = []
    if args.dataset in {"original", "all"}:
        cases.extend(load_original_cases(ORIGINAL_DATASET))
    if args.dataset in {"transformed", "all"}:
        cases.extend(load_transformed_cases(transformed_path))
    if args.limit is not None:
        cases = cases[: args.limit]

    client = ClaudeClient()
    records = run_cases(cases, client, strategies=strategies)
    
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    jsonl_output.parent.mkdir(parents=True, exist_ok=True)

    from llm_metamorphic_testing.storage import write_records_csv, write_records_jsonl
    write_records_csv(records, csv_output)
    write_records_jsonl(records, jsonl_output)

    print(f"version={args.version}")
    print(f"cases={len(cases)}")
    print(f"executions={len(records)}")
    print(f"csv={csv_output}")
    print(f"jsonl={jsonl_output}")


if __name__ == "__main__":
    main()
