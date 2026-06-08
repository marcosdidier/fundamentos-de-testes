"""Minimal Anthropic Claude Messages API client."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from llm_metamorphic_testing.config import ClaudeConfig, load_claude_config_from_env


class ClaudeClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompletionResult:
    raw_output: str
    usage: dict[str, int | None]


class ClaudeClient:
    def __init__(self, config: ClaudeConfig | None = None, *, timeout: float = 60.0) -> None:
        self.config = config if config is not None else load_claude_config_from_env()
        self.timeout = timeout
        self.model_name = self.config.model_name
        self.parameters = {
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

    def complete(self, prompt: str) -> CompletionResult:
        last_error: Exception | None = None
        for _attempt in range(2):
            try:
                return self._complete_once(prompt)
            except (OSError, ClaudeClientError) as exc:
                last_error = exc

        raise ClaudeClientError(f"Claude API request failed after retry: {last_error}")

    def _complete_once(self, prompt: str) -> CompletionResult:
        payload = {
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        request = urllib.request.Request(
            self.config.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": self.config.api_key,
                "anthropic-version": self.config.api_version,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ClaudeClientError(f"Claude API HTTP {exc.code}: {detail}") from exc
        except json.JSONDecodeError as exc:
            raise ClaudeClientError("Claude API returned invalid JSON") from exc

        return CompletionResult(
            raw_output=_extract_text(response_payload),
            usage=_extract_usage(response_payload),
        )


def _extract_text(response_payload: dict[str, Any]) -> str:
    content = response_payload.get("content")
    if not isinstance(content, list):
        raise ClaudeClientError("Claude API response missing content")

    text_parts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str):
                text_parts.append(text)

    if not text_parts:
        raise ClaudeClientError("Claude API response did not contain text")

    return "".join(text_parts)


def _extract_usage(response_payload: dict[str, Any]) -> dict[str, int | None]:
    usage = response_payload.get("usage")
    if not isinstance(usage, dict):
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}

    input_tokens = _optional_int(usage.get("input_tokens"))
    output_tokens = _optional_int(usage.get("output_tokens"))
    total_tokens = (
        None if input_tokens is None or output_tokens is None else input_tokens + output_tokens
    )

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None

