"""Risk-controlled automation with dual-order adjudication and human deferral."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from math import sqrt
from statistics import NormalDist
from typing import Any

from .runner import EvaluationRecord


@dataclass(frozen=True)
class PairDecision:
    """One underlying comparison after reconciling both answer orders."""

    base_item_id: str
    perturbation: str
    split: str
    language: str
    task: str
    decision: str
    confidence: float
    consistent: bool
    correct: bool | None


def _canonical_choice(record: EvaluationRecord) -> str:
    winner = record.result.winner
    if winner in {"tie", "abstain"}:
        return winner
    if record.item.presentation_order == "original":
        return "clean" if winner == "A" else "variant"
    return "variant" if winner == "A" else "clean"


def _canonical_gold(record: EvaluationRecord) -> str:
    winner = record.item.gold_winner
    if winner == "tie":
        return "tie"
    if record.item.presentation_order == "original":
        return "clean" if winner == "A" else "variant"
    return "variant" if winner == "A" else "clean"


def build_pair_decisions(records: list[EvaluationRecord]) -> list[PairDecision]:
    """Defer pairs whose two presentation orders do not agree."""
    grouped: dict[tuple[str, str], list[EvaluationRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.item.base_item_id, record.item.perturbation)].append(record)

    decisions: list[PairDecision] = []
    for key, pair in sorted(grouped.items()):
        if len(pair) != 2 or {record.item.presentation_order for record in pair} != {
            "original",
            "swapped",
        }:
            raise ValueError(f"incomplete order pair: {key[0]}/{key[1]}")
        original = next(r for r in pair if r.item.presentation_order == "original")
        swapped = next(r for r in pair if r.item.presentation_order == "swapped")
        choice_original = _canonical_choice(original)
        choice_swapped = _canonical_choice(swapped)
        consistent = choice_original == choice_swapped
        usable = consistent and choice_original != "abstain"
        decision = choice_original if usable else "human"
        gold = _canonical_gold(original)
        decisions.append(
            PairDecision(
                base_item_id=original.item.base_item_id,
                perturbation=original.item.perturbation,
                split=original.item.split,
                language=original.item.language,
                task=original.item.task,
                decision=decision,
                confidence=min(original.result.confidence, swapped.result.confidence),
                consistent=consistent,
                correct=(decision == gold) if usable else None,
            )
        )
    return decisions


def wilson_upper_bound(errors: int, decisions: int, confidence: float = 0.95) -> float:
    """Return the one-sided Wilson upper confidence bound for an error rate."""
    if decisions <= 0:
        return 1.0
    if not 0 <= errors <= decisions:
        raise ValueError("errors must be between zero and decisions")
    if not 0.5 < confidence < 1.0:
        raise ValueError("confidence must be between 0.5 and 1")
    z = NormalDist().inv_cdf(confidence)
    proportion = errors / decisions
    denominator = 1 + z * z / decisions
    centre = proportion + z * z / (2 * decisions)
    margin = z * sqrt(
        proportion * (1 - proportion) / decisions
        + z * z / (4 * decisions * decisions)
    )
    return min(1.0, (centre + margin) / denominator)


def evaluate_threshold(
    decisions: list[PairDecision], threshold: float
) -> dict[str, float | int | None]:
    """Evaluate one confidence threshold; inconsistent pairs remain deferred."""
    automated = [
        decision
        for decision in decisions
        if decision.correct is not None and decision.confidence >= threshold
    ]
    errors = sum(decision.correct is False for decision in automated)
    count = len(automated)
    return {
        "threshold": threshold,
        "total_pairs": len(decisions),
        "automated_pairs": count,
        "human_pairs": len(decisions) - count,
        "coverage": count / len(decisions) if decisions else 0.0,
        "selective_risk": errors / count if count else None,
        "risk_upper_95": wilson_upper_bound(errors, count),
        "errors": errors,
    }


def risk_coverage_curve(decisions: list[PairDecision]) -> list[dict[str, Any]]:
    """Evaluate every observed confidence as a possible automation threshold."""
    thresholds = sorted(
        {decision.confidence for decision in decisions if decision.correct is not None},
        reverse=True,
    )
    return [evaluate_threshold(decisions, threshold) for threshold in thresholds]


def audit_selective_judge(
    records: list[EvaluationRecord], *, target_risk: float = 0.05
) -> dict[str, Any]:
    """Select a threshold without test data, then evaluate it once on test data."""
    if not 0 < target_risk < 1:
        raise ValueError("target_risk must be between 0 and 1")
    decisions = build_pair_decisions(records)
    selection = [d for d in decisions if d.split == "validation"]
    test = [d for d in decisions if d.split == "test"]
    curve = risk_coverage_curve(selection)
    eligible = [
        point
        for point in curve
        if point["automated_pairs"] and point["risk_upper_95"] <= target_risk
    ]
    if not eligible:
        return {
            "status": "insufficient_evidence",
            "target_risk": target_risk,
            "selected_threshold": None,
            "selection_curve": curve,
            "test_result": None,
            "pair_decisions": [asdict(decision) for decision in decisions],
        }

    chosen = max(eligible, key=lambda point: (point["coverage"], -point["threshold"]))
    test_result = evaluate_threshold(test, float(chosen["threshold"]))
    status = (
        "passed"
        if test_result["automated_pairs"]
        and test_result["risk_upper_95"] <= target_risk
        else "failed_on_test"
    )
    return {
        "status": status,
        "target_risk": target_risk,
        "selected_threshold": chosen["threshold"],
        "selection_result": chosen,
        "selection_curve": curve,
        "test_result": test_result,
        "pair_decisions": [asdict(decision) for decision in decisions],
    }


def audit_calibrated_judge(
    records: list[EvaluationRecord], *, target_risk: float = 0.05
) -> dict[str, Any]:
    """Fit on calibration, select on validation, and evaluate once on test."""
    from .calibration import IsotonicCalibrator, calibration_metrics

    if not 0 < target_risk < 1:
        raise ValueError("target_risk must be between 0 and 1")
    raw_decisions = build_pair_decisions(records)
    calibration = [d for d in raw_decisions if d.split == "calibration"]
    calibrator = IsotonicCalibrator.fit(calibration)
    calibrated = [
        replace(decision, confidence=calibrator.predict(decision.confidence))
        if decision.correct is not None
        else decision
        for decision in raw_decisions
    ]
    calibrated_calibration = [d for d in calibrated if d.split == "calibration"]
    validation = [d for d in calibrated if d.split == "validation"]
    test = [d for d in calibrated if d.split == "test"]
    curve = risk_coverage_curve(validation)
    eligible = [
        point
        for point in curve
        if point["automated_pairs"] and point["risk_upper_95"] <= target_risk
    ]
    report: dict[str, Any] = {
        "target_risk": target_risk,
        "calibrator": calibrator.to_dict(),
        "calibration_metrics_before": calibration_metrics(calibration),
        "calibration_metrics_after": calibration_metrics(calibrated_calibration),
        "selection_curve": curve,
        "pair_decisions": [asdict(decision) for decision in calibrated],
    }
    if not eligible:
        report.update(
            {
                "status": "insufficient_evidence",
                "selected_threshold": None,
                "test_result": None,
            }
        )
        return report

    chosen = max(eligible, key=lambda point: (point["coverage"], -point["threshold"]))
    test_result = evaluate_threshold(test, float(chosen["threshold"]))
    report.update(
        {
            "status": (
                "passed"
                if test_result["automated_pairs"]
                and test_result["risk_upper_95"] <= target_risk
                else "failed_on_test"
            ),
            "selected_threshold": chosen["threshold"],
            "selection_result": chosen,
            "test_result": test_result,
        }
    )
    return report
