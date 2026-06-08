from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATASET = ROOT / "data" / "original" / "original_dataset.csv"
TRANSFORMED_DATASET = ROOT / "data" / "transformed" / "transformed_dataset.csv"


FIELDNAMES = [
    "case_id",
    "original_input_id",
    "transformation_type",
    "original_text",
    "transformed_text",
    "expected_label",
    "manual_review_status",
    "manual_review_notes",
]


PARAPHRASE_PREFIXES = {
    "refund_request": [
        "Preciso que a loja providencie a devolucao do valor, pois ",
        "Estou pedindo reembolso porque ",
        "Quero receber de volta o dinheiro pago, ja que ",
    ],
    "cancel_order": [
        "Preciso encerrar a compra, pois ",
        "Gostaria que o pedido fosse cancelado, ja que ",
        "Nao quero seguir com a compra, porque ",
    ],
    "delivery_problem": [
        "Estou com um problema de entrega: ",
        "Preciso de ajuda com o recebimento do pedido, pois ",
        "Ha uma falha no envio do meu pedido: ",
    ],
    "payment_issue": [
        "Estou enfrentando um problema no pagamento, pois ",
        "Preciso de suporte com a cobranca porque ",
        "A compra teve uma falha relacionada ao pagamento: ",
    ],
    "product_information": [
        "Quero confirmar uma informacao sobre o produto: ",
        "Tenho uma duvida sobre as caracteristicas do item: ",
        "Preciso saber um detalhe antes de comprar: ",
    ],
    "account_support": [
        "Preciso de ajuda com minha conta, pois ",
        "Estou com dificuldade no cadastro ou acesso: ",
        "Quero suporte para resolver um problema de conta: ",
    ],
    "other": [
        "Minha mensagem para a loja e a seguinte: ",
        "Entro em contato apenas para dizer que ",
        "Gostaria de registrar esta mensagem: ",
    ],
}


def normalize_sentence(text: str) -> str:
    normalized = text.strip()
    while normalized.endswith((".", "?", "!")):
        normalized = normalized[:-1].strip()
    if not normalized:
        return text.strip()
    return normalized[0].lower() + normalized[1:]


def punctuation_variant(text: str) -> str:
    base = normalize_sentence(text)
    if text.strip().endswith("?"):
        return f"{base}?"
    return f"{base}..."


def capitalization_variant(text: str, row_index: int) -> str:
    if row_index % 3 == 0:
        return text.upper()
    if row_index % 3 == 1:
        return text.lower()
    words = text.split()
    return " ".join(word.upper() if index % 2 == 0 else word.lower() for index, word in enumerate(words))


def paraphrase_variants(text: str, expected_label: str) -> list[str]:
    base = normalize_sentence(text)
    return [f"{prefix}{base}." for prefix in PARAPHRASE_PREFIXES[expected_label]]


def build_rows() -> list[dict[str, str]]:
    with ORIGINAL_DATASET.open(newline="", encoding="utf-8") as source:
        original_rows = list(csv.DictReader(source))

    transformed_rows: list[dict[str, str]] = []

    for index, original in enumerate(original_rows):
        original_input_id = original["original_input_id"]
        expected_label = original["expected_label"]
        original_text = original["text"]

        for paraphrase_index, transformed_text in enumerate(
            paraphrase_variants(original_text, expected_label),
            start=1,
        ):
            transformed_rows.append(
                {
                    "case_id": f"{original_input_id}_paraphrase_{paraphrase_index:02d}",
                    "original_input_id": original_input_id,
                    "transformation_type": "paraphrase",
                    "original_text": original_text,
                    "transformed_text": transformed_text,
                    "expected_label": expected_label,
                    "manual_review_status": "pending",
                    "manual_review_notes": "",
                }
            )

        transformed_rows.append(
            {
                "case_id": f"{original_input_id}_punctuation_01",
                "original_input_id": original_input_id,
                "transformation_type": "punctuation",
                "original_text": original_text,
                "transformed_text": punctuation_variant(original_text),
                "expected_label": expected_label,
                "manual_review_status": "pending",
                "manual_review_notes": "",
            }
        )

        transformed_rows.append(
            {
                "case_id": f"{original_input_id}_capitalization_01",
                "original_input_id": original_input_id,
                "transformation_type": "capitalization",
                "original_text": original_text,
                "transformed_text": capitalization_variant(original_text, index),
                "expected_label": expected_label,
                "manual_review_status": "pending",
                "manual_review_notes": "",
            }
        )

    return transformed_rows


def main() -> None:
    transformed_rows = build_rows()
    TRANSFORMED_DATASET.parent.mkdir(parents=True, exist_ok=True)

    with TRANSFORMED_DATASET.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(transformed_rows)

    print(f"wrote={TRANSFORMED_DATASET}")
    print(f"rows={len(transformed_rows)}")


if __name__ == "__main__":
    main()

