"""Runtime configuration for the Claude experiment client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_MODEL_NAME = "claude-haiku-4-5"
DEFAULT_TEMPERATURE = 0
DEFAULT_MAX_TOKENS = 64
DEFAULT_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_API_VERSION = "2023-06-01"


@dataclass(frozen=True)
class ClaudeConfig:
    api_key: str
    model_name: str = DEFAULT_MODEL_NAME
    temperature: int = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    api_url: str = DEFAULT_API_URL
    api_version: str = DEFAULT_API_VERSION


def load_claude_config_from_env() -> ClaudeConfig:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is required")

    return ClaudeConfig(
        api_key=api_key,
        model_name=os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL_NAME).strip(),
        max_tokens=int(os.environ.get("ANTHROPIC_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
    )


def load_dotenv(path: str | Path = ".env", *, override: bool = False) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = _clean_env_value(value.strip())
        if override or key not in os.environ:
            os.environ[key] = value


def _clean_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value.startswith(("'", '"')):
        return value[1:-1]
    return value

