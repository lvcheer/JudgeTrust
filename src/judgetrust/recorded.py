"""Replay previously captured raw judge responses without model access."""

from __future__ import annotations

import json
from pathlib import Path

from .interfaces import JudgeRequest, JudgeResult
from .prompting import parse_judge_response


class RecordedJudge:
    """Judge adapter backed by an item-id-to-response mapping."""

    def __init__(self, responses: dict[str, str], *, name: str = "recorded") -> None:
        self._responses = responses
        self.name = name

    @classmethod
    def from_jsonl(
        cls, path: str | Path, *, name: str = "recorded"
    ) -> RecordedJudge:
        responses: dict[str, str] = {}
        with Path(path).open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"invalid recorded response at line {line_number}: {error.msg}"
                    ) from error
                if set(value) != {"item_id", "response"}:
                    raise ValueError(f"invalid fields at recorded line {line_number}")
                if value["item_id"] in responses:
                    raise ValueError(f"duplicate recorded item_id: {value['item_id']}")
                if not isinstance(value["response"], str):
                    raise ValueError(f"response must be text at recorded line {line_number}")
                responses[value["item_id"]] = value["response"]
        return cls(responses, name=name)

    def evaluate(self, request: JudgeRequest) -> JudgeResult:
        try:
            raw_response = self._responses[request.item_id]
        except KeyError as error:
            raise KeyError(f"no recorded response for {request.item_id}") from error
        return parse_judge_response(raw_response)

