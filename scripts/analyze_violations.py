import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
V1_RESULTS_PATH = ROOT / "results" / "processed" / "full_execution_results.csv"
V2_RESULTS_PATH = ROOT / "results" / "processed" / "v2_execution_results.csv"

def load_rows(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_violations(rows, exclude_free=True):
    violations = []
    for r in rows:
        if r["transformation_type"] == "original":
            continue
        if exclude_free and r["prompt_strategy"] == "free":
            continue
        if r["is_violation_expected_label"] == "True":
            violations.append(r)
    return violations

def main():
    v1_rows = load_rows(V1_RESULTS_PATH)
    v2_rows = load_rows(V2_RESULTS_PATH)

    v1_viols = get_violations(v1_rows, exclude_free=True)
    v2_viols = get_violations(v2_rows, exclude_free=False) # v2 doesn't have free anyway

    print(f"=== Experimento v1: {len(v1_viols)} violações ===")
    v1_by_cat = Counter(v["expected_label"] for v in v1_viols)
    for cat, count in v1_by_cat.most_common():
        print(f"  - {cat}: {count}")
    
    print(f"\n=== Experimento v2: {len(v2_viols)} violações ===")
    v2_by_cat = Counter(v["expected_label"] for v in v2_viols)
    for cat, count in v2_by_cat.most_common():
        print(f"  - {cat}: {count}")

    # Print some examples of v1 violations
    print("\n--- Exemplos de Violações v1 ---")
    for v in v1_viols[:5]:
        print(f"ID: {v['case_id']} | Strat: {v['prompt_strategy']}")
        print(f"  Original ({v['expected_label']}): {v['original_text']}")
        print(f"  Transformed: {v['transformed_text']}")
        print(f"  Model output label: {v['parsed_label']}")

    # Print some examples of v2 violations
    print("\n--- Exemplos de Violações v2 ---")
    for v in v2_viols[:5]:
        print(f"ID: {v['case_id']} | Strat: {v['prompt_strategy']}")
        print(f"  Original ({v['expected_label']}): {v['original_text']}")
        print(f"  Transformed: {v['transformed_text']}")
        print(f"  Model output label: {v['parsed_label']}")

if __name__ == "__main__":
    main()
