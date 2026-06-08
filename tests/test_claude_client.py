import json
import unittest
from unittest.mock import patch

from llm_metamorphic_testing.claude_client import ClaudeClient, ClaudeClientError
from llm_metamorphic_testing.config import ClaudeConfig


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class ClaudeClientTest(unittest.TestCase):
    def test_complete_posts_message_and_extracts_text_and_usage(self) -> None:
        payload = {
            "content": [{"type": "text", "text": '{"label": "other"}'}],
            "usage": {"input_tokens": 12, "output_tokens": 4},
        }
        config = ClaudeConfig(api_key="test-key")
        client = ClaudeClient(config=config, timeout=1)

        with patch("urllib.request.urlopen", return_value=FakeResponse(payload)) as urlopen:
            result = client.complete("Classifique isso")

        request = urlopen.call_args.args[0]
        request_body = json.loads(request.data.decode("utf-8"))

        self.assertEqual(request_body["model"], "claude-haiku-4-5")
        self.assertEqual(request_body["max_tokens"], 64)
        self.assertEqual(request_body["temperature"], 0)
        self.assertEqual(result.raw_output, '{"label": "other"}')
        self.assertEqual(
            result.usage,
            {"input_tokens": 12, "output_tokens": 4, "total_tokens": 16},
        )

    def test_complete_raises_after_retry(self) -> None:
        config = ClaudeConfig(api_key="test-key")
        client = ClaudeClient(config=config, timeout=1)

        with patch("urllib.request.urlopen", side_effect=OSError("network down")):
            with self.assertRaises(ClaudeClientError):
                client.complete("prompt")


if __name__ == "__main__":
    unittest.main()

