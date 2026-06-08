import tempfile
import unittest
from pathlib import Path

from llm_metamorphic_testing.datasets import load_original_cases, load_transformed_cases


class DatasetLoaderTest(unittest.TestCase):
    def test_load_original_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "original.csv"
            path.write_text(
                "original_input_id,text,expected_label,manual_review_status,manual_review_notes\n"
                "orig-001,Quero cancelar meu pedido.,cancel_order,pending,\n",
                encoding="utf-8",
            )

            cases = load_original_cases(path)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].case_id, "orig-001")
        self.assertEqual(cases[0].transformation_type, "original")
        self.assertEqual(cases[0].transformed_text, "Quero cancelar meu pedido.")

    def test_load_transformed_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "transformed.csv"
            path.write_text(
                "case_id,original_input_id,transformation_type,original_text,"
                "transformed_text,expected_label,manual_review_status,manual_review_notes\n"
                "case-001,orig-001,paraphrase,Quero cancelar meu pedido.,"
                "Gostaria de cancelar a compra.,cancel_order,pending,\n",
                encoding="utf-8",
            )

            cases = load_transformed_cases(path)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].case_id, "case-001")
        self.assertEqual(cases[0].original_input_id, "orig-001")
        self.assertEqual(cases[0].transformation_type, "paraphrase")


if __name__ == "__main__":
    unittest.main()

