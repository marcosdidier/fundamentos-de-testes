import csv
import json
import tempfile
import unittest
from pathlib import Path

from llm_metamorphic_testing.schemas import ExecutionRecord
from llm_metamorphic_testing.storage import COLLECTED_FIELDS, write_records_csv, write_records_jsonl


class StorageTest(unittest.TestCase):
    def test_write_records_csv_uses_collected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "results" / "processed" / "records.csv"

            write_records_csv([self._record()], path)

            with path.open(newline="", encoding="utf-8") as source:
                reader = csv.DictReader(source)
                rows = list(reader)

        self.assertEqual(tuple(reader.fieldnames or ()), COLLECTED_FIELDS)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["case_id"], "case-001")
        self.assertEqual(json.loads(rows[0]["parameters"]), {"temperature": 0})

    def test_write_records_jsonl_preserves_full_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "results" / "raw" / "records.jsonl"

            write_records_jsonl([self._record()], path)

            lines = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(len(lines), 1)
        payload = json.loads(lines[0])
        self.assertEqual(payload["case_id"], "case-001")
        self.assertEqual(payload["metadata"], {"parse_error": None})

    @staticmethod
    def _record() -> ExecutionRecord:
        return ExecutionRecord(
            case_id="case-001",
            original_input_id="orig-001",
            transformation_type="original",
            original_text="Quero cancelar meu pedido.",
            transformed_text="Quero cancelar meu pedido.",
            expected_label="cancel_order",
            prompt_strategy="strict",
            prompt_text="prompt",
            model_name="fake-claude",
            parameters={"temperature": 0},
            raw_output='{"label": "cancel_order"}',
            parsed_label="cancel_order",
            is_valid_output=True,
            is_violation_expected_label=False,
            is_prediction_flip=None,
            execution_time=0.1,
            estimated_cost=None,
            timestamp="2026-06-07T20:00:00+00:00",
            manual_review_notes="",
            metadata={"parse_error": None},
        )


if __name__ == "__main__":
    unittest.main()

