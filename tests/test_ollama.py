import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from judgetrust import (
    JudgeRequest,
    OllamaConnectionError,
    OllamaJudge,
    OllamaResponseError,
)


class FakeHTTPResponse:
    def __init__(self, value: object) -> None:
        self.body = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def request() -> JudgeRequest:
    return JudgeRequest(
        item_id="qa-en-001",
        task="factual_qa",
        language="en",
        prompt="Question",
        answer_a="Answer A",
        answer_b="Answer B",
        context="Reference",
    )


def valid_inner_response() -> str:
    return json.dumps(
        {
            "winner": "A",
            "score_a": 0.9,
            "score_b": 0.1,
            "confidence": 0.8,
            "reason_code": "factuality",
            "explanation": "A is supported by the reference.",
        }
    )


class OllamaJudgeTests(unittest.TestCase):
    @patch("judgetrust.ollama.urlopen")
    def test_sends_non_streaming_deterministic_json_request(self, mocked_urlopen) -> None:
        mocked_urlopen.return_value = FakeHTTPResponse(
            {"response": valid_inner_response(), "done": True}
        )
        judge = OllamaJudge()

        result = judge.evaluate(request())

        self.assertEqual(result.winner, "A")
        http_request = mocked_urlopen.call_args.args[0]
        body = json.loads(http_request.data)
        self.assertEqual(body["model"], "qwen2.5:14b")
        self.assertFalse(body["stream"])
        self.assertEqual(body["format"]["type"], "object")
        self.assertEqual(
            body["format"]["properties"]["reason_code"]["enum"],
            ["factuality", "completeness", "citation", "instruction", "uncertain"],
        )
        self.assertFalse(body["format"]["additionalProperties"])
        self.assertEqual(body["options"], {"temperature": 0, "seed": 0})
        self.assertNotIn("gold_winner", body["prompt"])

    @patch("judgetrust.ollama.urlopen", side_effect=URLError("offline"))
    def test_connection_failure_is_explicit(self, mocked_urlopen) -> None:
        with self.assertRaisesRegex(OllamaConnectionError, "request failed"):
            OllamaJudge().evaluate(request())
        mocked_urlopen.assert_called_once()

    @patch("judgetrust.ollama.urlopen")
    def test_malformed_envelope_is_rejected(self, mocked_urlopen) -> None:
        mocked_urlopen.return_value = FakeHTTPResponse({"done": True})
        with self.assertRaisesRegex(OllamaResponseError, "text response"):
            OllamaJudge().evaluate(request())

    @patch("judgetrust.ollama.urlopen")
    def test_invalid_inner_judge_output_is_rejected(self, mocked_urlopen) -> None:
        mocked_urlopen.return_value = FakeHTTPResponse({"response": "not-json"})
        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            OllamaJudge().evaluate(request())


if __name__ == "__main__":
    unittest.main()
