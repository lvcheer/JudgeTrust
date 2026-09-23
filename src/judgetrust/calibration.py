"""Dependency-free confidence calibration and diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .selective import PairDecision


@dataclass(frozen=True)
class IsotonicBlock:
    lower: float
    upper: float
    probability: float
    count: int


class IsotonicCalibrator:
    """Monotonic correctness-probability calibrator fitted with PAVA."""

    def __init__(self, blocks: list[IsotonicBlock]) -> None:
        if not blocks:
            raise ValueError("calibrator requires at least one block")
        self.blocks = blocks

    @classmethod
    def fit(cls, decisions: list[PairDecision]) -> IsotonicCalibrator:
        observations = sorted(
            (decision.confidence, float(decision.correct))
            for decision in decisions
            if decision.correct is not None
        )
        if not observations:
            raise ValueError("no decided calibration pairs")

        grouped: list[dict[str, float | int]] = []
        for confidence, label in observations:
            if grouped and grouped[-1]["upper"] == confidence:
                grouped[-1]["sum"] = float(grouped[-1]["sum"]) + label
                grouped[-1]["count"] = int(grouped[-1]["count"]) + 1
            else:
                grouped.append(
                    {
                        "lower": confidence,
                        "upper": confidence,
                        "sum": label,
                        "count": 1,
                    }
                )

        index = 0
        while index < len(grouped) - 1:
            left = float(grouped[index]["sum"]) / int(grouped[index]["count"])
            right = float(grouped[index + 1]["sum"]) / int(
                grouped[index + 1]["count"]
            )
            if left <= right:
                index += 1
                continue
            grouped[index : index + 2] = [
                {
                    "lower": grouped[index]["lower"],
                    "upper": grouped[index + 1]["upper"],
                    "sum": float(grouped[index]["sum"])
                    + float(grouped[index + 1]["sum"]),
                    "count": int(grouped[index]["count"])
                    + int(grouped[index + 1]["count"]),
                }
            ]
            index = max(0, index - 1)

        return cls(
            [
                IsotonicBlock(
                    lower=float(block["lower"]),
                    upper=float(block["upper"]),
                    probability=float(block["sum"]) / int(block["count"]),
                    count=int(block["count"]),
                )
                for block in grouped
            ]
        )

    def predict(self, confidence: float) -> float:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        chosen = self.blocks[0]
        for block in self.blocks:
            if confidence < block.lower:
                break
            chosen = block
        return chosen.probability

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": "isotonic_pava",
            "blocks": [
                {
                    "lower": block.lower,
                    "upper": block.upper,
                    "probability": block.probability,
                    "count": block.count,
                }
                for block in self.blocks
            ],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> IsotonicCalibrator:
        if value.get("method") != "isotonic_pava" or not isinstance(
            value.get("blocks"), list
        ):
            raise ValueError("invalid isotonic calibrator data")
        return cls([IsotonicBlock(**block) for block in value["blocks"]])


def calibration_metrics(
    decisions: list[PairDecision], *, bins: int = 10
) -> dict[str, Any]:
    """Compute Brier score, ECE, and equal-width reliability bins."""
    if bins <= 0:
        raise ValueError("bins must be positive")
    usable = [decision for decision in decisions if decision.correct is not None]
    if not usable:
        raise ValueError("no decided pairs for calibration metrics")
    brier = sum(
        (decision.confidence - float(decision.correct)) ** 2 for decision in usable
    ) / len(usable)

    reliability: list[dict[str, float | int]] = []
    ece = 0.0
    for bin_index in range(bins):
        lower = bin_index / bins
        upper = (bin_index + 1) / bins
        members = [
            decision
            for decision in usable
            if lower <= decision.confidence < upper
            or (bin_index == bins - 1 and decision.confidence == 1.0)
        ]
        if not members:
            continue
        average_confidence = sum(d.confidence for d in members) / len(members)
        accuracy = sum(bool(d.correct) for d in members) / len(members)
        ece += len(members) / len(usable) * abs(average_confidence - accuracy)
        reliability.append(
            {
                "lower": lower,
                "upper": upper,
                "count": len(members),
                "average_confidence": average_confidence,
                "accuracy": accuracy,
            }
        )
    return {
        "count": len(usable),
        "brier_score": brier,
        "ece": ece,
        "reliability_bins": reliability,
    }

