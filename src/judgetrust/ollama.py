"""Ollama adapter using only the Python standard library."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .interfaces import JudgeRequest, JudgeResult
from .prompting import build_judge_prompt, parse_judge_response


JUDGE_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "winner": {"type": "string", "enum": ["A", "B", "tie", "abstain"]},
        "score_a": {"type": "number", "minimum": 0, "maximum": 1},
        "score_b": {"type": "number", "minimum": 0, "maximum": 1},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reason_code": {
            "type": "string",
            "enum": [
                "factuality",
                "completeness",
                "citation",
                "instruction",
                "uncertain",
            ],
        },
        "explanation": {"type": "string", "minLength": 1},
    },
    "required": [
        "winner",
        "score_a",
        "score_b",
        "confidence",
        "reason_code",
        "explanation",
    ],
    "additionalProperties": False,
}


class OllamaConnectionError(RuntimeError):
    """Raised when the local Ollama service cannot complete a request."""


class OllamaResponseError(ValueError):
    """Raised when Ollama's response envelope is malformed."""


@dataclass(frozen=True)
class OllamaJudge:
    """Pairwise judge backed by Ollama's local generate endpoint."""

    model: str = "qwen2.5:14b"
    base_url: str = "http://127.0.0.1:11434"
    timeout: float = 120.0
    name: str = "ollama-qwen2.5-14b"

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    def evaluate(self, request: JudgeRequest) -> JudgeResult:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": build_judge_prompt(request),
                "stream": False,
                "format": JUDGE_RESULT_SCHEMA,
                "options": {"temperature": 0, "seed": 0},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        http_request = Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "JudgeTrust/0.1.0",
            },
            method="POST",
        )
        try:
            with urlopen(http_request, timeout=self.timeout) as response:
                raw_envelope = response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            raise OllamaConnectionError(
                f"Ollama request failed for model {self.model}: {error}"
            ) from error

        try:
            envelope = json.loads(raw_envelope)
        except json.JSONDecodeError as error:
            raise OllamaResponseError("Ollama returned an invalid JSON envelope") from error
        if not isinstance(envelope, dict) or not isinstance(envelope.get("response"), str):
            raise OllamaResponseError("Ollama envelope must contain a text response")
        return parse_judge_response(envelope["response"])
