"""Cost estimation based on token usage returned by the API."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    input_per_million: float
    output_per_million: float


MODEL_PRICING_USD: dict[str, ModelPricing] = {
    "claude-haiku-4-5": ModelPricing(input_per_million=1.00, output_per_million=5.00),
}


def estimate_cost_usd(
    model_name: str,
    *,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    pricing = MODEL_PRICING_USD.get(model_name)
    if pricing is None or input_tokens is None or output_tokens is None:
        return None

    input_cost = (input_tokens / 1_000_000) * pricing.input_per_million
    output_cost = (output_tokens / 1_000_000) * pricing.output_per_million
    return input_cost + output_cost

