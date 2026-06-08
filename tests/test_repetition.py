import unittest
from collections import Counter

from llm_metamorphic_testing.labels import LABELS
from llm_metamorphic_testing.repetition import (
    balanced_ten_percent_sample,
    build_repeated_cases,
    systematic_sample,
)
from llm_metamorphic_testing.schemas import ExperimentCase


class RepetitionTest(unittest.TestCase):
    def test_systematic_sample_selects_requested_number_of_cases(self) -> None:
        cases = [self._case(index) for index in range(10)]

        sample = systematic_sample(cases, 5)

        self.assertEqual([case.case_id for case in sample], ["case-0", "case-2", "case-4", "case-6", "case-8"])

    def test_build_repeated_cases_suffixes_case_id(self) -> None:
        repeated = build_repeated_cases([self._case(1)], repetitions=3)

        self.assertEqual(
            [case.case_id for case in repeated],
            ["case-1_repeat_01", "case-1_repeat_02", "case-1_repeat_03"],
        )
        self.assertEqual(repeated[0].original_input_id, "orig-1")
        self.assertEqual(repeated[0].manual_review_notes, "repetition=1")

    def test_invalid_sample_size_fails(self) -> None:
        with self.assertRaises(ValueError):
            systematic_sample([self._case(1)], 0)
        with self.assertRaises(ValueError):
            systematic_sample([self._case(1)], 2)

    def test_balanced_ten_percent_sample_covers_labels_and_transformations(self) -> None:
        cases = []
        for label in LABELS:
            cases.extend(self._cases_for(label, "original", 10))
            cases.extend(self._cases_for(label, "paraphrase", 30))
            cases.extend(self._cases_for(label, "punctuation", 10))
            cases.extend(self._cases_for(label, "capitalization", 10))

        sample = balanced_ten_percent_sample(cases)

        self.assertEqual(len(sample), 42)
        self.assertEqual(Counter(case.expected_label for case in sample), Counter({label: 6 for label in LABELS}))
        self.assertEqual(
            Counter(case.transformation_type for case in sample),
            Counter({"original": 7, "paraphrase": 21, "punctuation": 7, "capitalization": 7}),
        )

    @staticmethod
    def _case(index: int) -> ExperimentCase:
        return ExperimentCase(
            case_id=f"case-{index}",
            original_input_id=f"orig-{index}",
            transformation_type="original",
            original_text="Quero cancelar meu pedido.",
            transformed_text="Quero cancelar meu pedido.",
            expected_label="cancel_order",
        )

    @staticmethod
    def _cases_for(label: str, transformation_type: str, count: int) -> list[ExperimentCase]:
        return [
            ExperimentCase(
                case_id=f"{label}-{transformation_type}-{index}",
                original_input_id=f"orig-{label}-{index}",
                transformation_type=transformation_type,  # type: ignore[arg-type]
                original_text="Quero cancelar meu pedido.",
                transformed_text="Quero cancelar meu pedido.",
                expected_label=label,
            )
            for index in range(count)
        ]


if __name__ == "__main__":
    unittest.main()
