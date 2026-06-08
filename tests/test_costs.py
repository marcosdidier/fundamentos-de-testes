import unittest

from llm_metamorphic_testing.costs import estimate_cost_usd


class CostsTest(unittest.TestCase):
    def test_estimate_cost_for_default_model(self) -> None:
        cost = estimate_cost_usd(
            "claude-haiku-4-5",
            input_tokens=1_000,
            output_tokens=100,
        )

        self.assertEqual(cost, 0.0015)

    def test_estimate_cost_returns_none_without_usage_or_pricing(self) -> None:
        self.assertIsNone(
            estimate_cost_usd("unknown-model", input_tokens=1_000, output_tokens=100)
        )
        self.assertIsNone(
            estimate_cost_usd("claude-haiku-4-5", input_tokens=None, output_tokens=100)
        )


if __name__ == "__main__":
    unittest.main()

