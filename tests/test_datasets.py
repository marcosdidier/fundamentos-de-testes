import csv
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from llm_metamorphic_testing.labels import LABELS


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATASET = ROOT / "data" / "original" / "original_dataset.csv"
TRANSFORMED_DATASET = ROOT / "data" / "transformed" / "transformed_dataset.csv"


class DatasetTest(unittest.TestCase):
    def test_original_dataset_is_balanced(self) -> None:
        rows = self._read_csv(ORIGINAL_DATASET)

        self.assertEqual(len(rows), 70)
        self.assertEqual(len({row["original_input_id"] for row in rows}), 70)
        self.assertEqual(Counter(row["expected_label"] for row in rows), Counter({label: 10 for label in LABELS}))
        self.assertFalse([row for row in rows if not row["text"].strip()])

    def test_transformed_dataset_matches_backlog_counts(self) -> None:
        rows = self._read_csv(TRANSFORMED_DATASET)

        self.assertEqual(len(rows), 350)
        self.assertEqual(len({row["case_id"] for row in rows}), 350)
        self.assertEqual(
            Counter(row["transformation_type"] for row in rows),
            Counter({"paraphrase": 210, "punctuation": 70, "capitalization": 70}),
        )

    def test_each_original_has_five_transformations(self) -> None:
        rows = self._read_csv(TRANSFORMED_DATASET)
        by_original: dict[str, list[dict[str, str]]] = defaultdict(list)

        for row in rows:
            by_original[row["original_input_id"]].append(row)

        self.assertEqual(len(by_original), 70)
        for transformed_rows in by_original.values():
            self.assertEqual(len(transformed_rows), 5)
            self.assertEqual(
                Counter(row["transformation_type"] for row in transformed_rows),
                Counter({"paraphrase": 3, "punctuation": 1, "capitalization": 1}),
            )

    def test_transformed_labels_are_valid_and_pending_review(self) -> None:
        rows = self._read_csv(TRANSFORMED_DATASET)

        self.assertFalse([row for row in rows if row["expected_label"] not in LABELS])
        self.assertFalse([row for row in rows if row["manual_review_status"] != "pending"])
        self.assertFalse([row for row in rows if not row["transformed_text"].strip()])

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open(newline="", encoding="utf-8") as source:
            return list(csv.DictReader(source))


if __name__ == "__main__":
    unittest.main()

