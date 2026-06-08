import unittest

from llm_metamorphic_testing.labels import LABELS
from llm_metamorphic_testing.prompts import PromptStrategy, render_prompt


class PromptsTest(unittest.TestCase):
    def test_all_prompt_strategies_render_message(self) -> None:
        message = "Quero cancelar meu pedido."

        for strategy in PromptStrategy:
            prompt = render_prompt(strategy, message)

            self.assertIn(message, prompt)
            self.assertNotIn("{message}", prompt)

    def test_strict_prompt_lists_all_labels_and_json_contract(self) -> None:
        prompt = render_prompt(PromptStrategy.STRICT, "Minha entrega atrasou.")

        for label in LABELS:
            self.assertIn(label, prompt)
        self.assertIn('{"label": "um_dos_rotulos"}', prompt)
        self.assertIn("Retorne apenas um JSON", prompt)

    def test_few_shot_prompt_contains_examples(self) -> None:
        prompt = render_prompt(PromptStrategy.FEW_SHOT, "Meu boleto venceu.")

        self.assertIn('"Meu pagamento foi recusado." -> payment_issue', prompt)
        self.assertIn('"Obrigado pelo atendimento." -> other', prompt)


if __name__ == "__main__":
    unittest.main()

