"""Minimal contracts shared by JudgeTrust judge adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

Winner = Literal["A", "B", "tie", "abstain"]
ReasonCode = Literal[
    "factuality",
    "completeness",
    "citation",
    "instruction",
    "uncertain",
]


@dataclass(frozen=True)
class JudgeRequest:
    """One pairwise evaluation request."""

    item_id: str
    task: str
    language: Literal["en", "zh"]
    prompt: str
    answer_a: str
    answer_b: str
    context: str | None = None


@dataclass(frozen=True)
class JudgeResult:
    """Structured output returned by every judge adapter."""

    winner: Winner
    score_a: float
    score_b: float
    confidence: float
    reason_code: ReasonCode
    explanation: str

    def __post_init__(self) -> None:
        if self.winner not in {"A", "B", "tie", "abstain"}:
            raise ValueError(f"invalid winner: {self.winner!r}")
        if self.reason_code not in {
            "factuality",
            "completeness",
            "citation",
            "instruction",
            "uncertain",
        }:
            raise ValueError(f"invalid reason_code: {self.reason_code!r}")
        for field_name in ("score_a", "score_b", "confidence"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{field_name} must be numeric")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
        if not isinstance(self.explanation, str) or not self.explanation.strip():
            raise ValueError("explanation must not be empty")


class Judge(Protocol):
    """Interface implemented by local, recorded, fake, or API judges."""

    name: str

    def evaluate(self, request: JudgeRequest) -> JudgeResult:
        """Evaluate a pair of candidate answers."""
        ...
