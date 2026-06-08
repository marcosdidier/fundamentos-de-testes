"""Classification labels defined by the experimental backlog."""

from __future__ import annotations

from enum import StrEnum


class IntentLabel(StrEnum):
    REFUND_REQUEST = "refund_request"
    CANCEL_ORDER = "cancel_order"
    DELIVERY_PROBLEM = "delivery_problem"
    PAYMENT_ISSUE = "payment_issue"
    PRODUCT_INFORMATION = "product_information"
    ACCOUNT_SUPPORT = "account_support"
    OTHER = "other"


LABELS: tuple[str, ...] = tuple(label.value for label in IntentLabel)


def is_valid_label(value: str) -> bool:
    return value in LABELS

