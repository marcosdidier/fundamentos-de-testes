import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from llm_metamorphic_testing.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    load_dotenv,
    load_claude_config_from_env,
)


class ConfigTest(unittest.TestCase):
    def test_load_claude_config_uses_defaults(self) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
            config = load_claude_config_from_env()

        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.model_name, DEFAULT_MODEL_NAME)
        self.assertEqual(config.temperature, DEFAULT_TEMPERATURE)
        self.assertEqual(config.max_tokens, DEFAULT_MAX_TOKENS)

    def test_load_claude_config_allows_model_and_max_tokens_override(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "test-key",
                "ANTHROPIC_MODEL": "claude-custom",
                "ANTHROPIC_MAX_TOKENS": "32",
            },
            clear=True,
        ):
            config = load_claude_config_from_env()

        self.assertEqual(config.model_name, "claude-custom")
        self.assertEqual(config.max_tokens, 32)

    def test_load_claude_config_requires_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                load_claude_config_from_env()

    def test_load_dotenv_reads_key_value_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / ".env"
            path.write_text(
                "# comment\n"
                "ANTHROPIC_API_KEY='test-key'\n"
                "ANTHROPIC_MAX_TOKENS=32\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                load_dotenv(path)

                self.assertEqual(os.environ["ANTHROPIC_API_KEY"], "test-key")
                self.assertEqual(os.environ["ANTHROPIC_MAX_TOKENS"], "32")


if __name__ == "__main__":
    unittest.main()
