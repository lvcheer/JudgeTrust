"""Deterministic offline judges used to validate the evaluation pipeline."""

from dataclasses import dataclass
from typing import Literal

from .interfaces import JudgeRequest, JudgeResult


@dataclass(frozen=True)
class FixedWinnerJudge:
    """Always choose the same position to expose order-bias calculations."""

    winner: Literal["A", "B", "tie", "abstain"] = "A"
    confidence: float = 0.9
    name: str = "fixed-winner"

    def evaluate(self, request: JudgeRequest) -> JudgeResult:
        del request
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        scores = {
            "A": (1.0, 0.0),
            "B": (0.0, 1.0),
            "tie": (0.5, 0.5),
            "abstain": (0.5, 0.5),
        }
        score_a, score_b = scores[self.winner]
        return JudgeResult(
            winner=self.winner,
            score_a=score_a,
            score_b=score_b,
            confidence=self.confidence,
            reason_code="uncertain",
            explanation="Deterministic offline result for pipeline testing.",
        )

