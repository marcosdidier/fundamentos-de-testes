"""Prompt strategies fixed in the experimental backlog."""

from __future__ import annotations

from enum import StrEnum

from llm_metamorphic_testing.labels import LABELS


class PromptStrategy(StrEnum):
    FREE = "free"
    STRICT = "strict"
    FEW_SHOT = "few_shot"


_LABEL_LIST = ", ".join(LABELS)


PROMPT_TEMPLATES: dict[PromptStrategy, str] = {
    PromptStrategy.FREE: (
        'Leia a mensagem do cliente e identifique qual e a intencao principal.\n'
        "Mensagem:\n"
        '"{message}"'
    ),
    PromptStrategy.STRICT: (
        "Classifique a intencao da mensagem abaixo.\n"
        "Retorne apenas um JSON no seguinte formato:\n"
        '{{"label": "um_dos_rotulos"}}\n'
        "Rotulos possiveis:\n"
        f"{_LABEL_LIST}\n"
        "Mensagem:\n"
        '"{message}"'
    ),
    PromptStrategy.FEW_SHOT: (
        "Classifique a intencao da mensagem abaixo.\n"
        "Rotulos possiveis:\n"
        f"{_LABEL_LIST}\n"
        "Exemplos:\n"
        '"Quero meu dinheiro de volta." -> refund_request\n'
        '"Gostaria de cancelar meu pedido." -> cancel_order\n'
        '"Minha entrega ainda nao chegou." -> delivery_problem\n'
        '"Meu pagamento foi recusado." -> payment_issue\n'
        '"Esse produto tem garantia?" -> product_information\n'
        '"Nao consigo acessar minha conta." -> account_support\n'
        '"Obrigado pelo atendimento." -> other\n'
        "Retorne apenas um JSON no seguinte formato:\n"
        '{{"label": "um_dos_rotulos"}}\n'
        "Mensagem:\n"
        '"{message}"'
    ),
}


def render_prompt(strategy: PromptStrategy | str, message: str) -> str:
    prompt_strategy = PromptStrategy(strategy)
    return PROMPT_TEMPLATES[prompt_strategy].format(message=message)
