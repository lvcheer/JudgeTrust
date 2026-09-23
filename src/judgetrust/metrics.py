"""Core reliability and order-bias metrics for pairwise judge runs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .runner import EvaluationRecord


def _accuracy(records: list[EvaluationRecord]) -> float:
    if not records:
        return 0.0
    correct = sum(record.result.winner == record.item.gold_winner for record in records)
    return correct / len(records)


def _canonical_choice(record: EvaluationRecord) -> str:
    winner = record.result.winner
    if winner in {"tie", "abstain"}:
        return winner
    if record.item.presentation_order == "original":
        return "clean" if winner == "A" else "variant"
    return "variant" if winner == "A" else "clean"


def _group_accuracy(
    records: list[EvaluationRecord], field_name: str
) -> dict[str, dict[str, float | int]]:
    groups: dict[str, list[EvaluationRecord]] = defaultdict(list)
    for record in records:
        groups[str(getattr(record.item, field_name))].append(record)
    return {
        name: {"count": len(group), "accuracy": _accuracy(group)}
        for name, group in sorted(groups.items())
    }


def compute_metrics(records: list[EvaluationRecord]) -> dict[str, Any]:
    """Compute accuracy, positional preference, and paired order consistency."""
    if not records:
        raise ValueError("cannot compute metrics for an empty run")

    by_pair: dict[tuple[str, str], list[EvaluationRecord]] = defaultdict(list)
    for record in records:
        key = (record.item.base_item_id, record.item.perturbation)
        by_pair[key].append(record)

    consistent = 0
    positional_flips = 0
    positional_pairs = 0
    for key, pair in by_pair.items():
        if len(pair) != 2 or {r.item.presentation_order for r in pair} != {
            "original",
            "swapped",
        }:
            raise ValueError(f"incomplete order pair: {key[0]}/{key[1]}")
        choices = [_canonical_choice(record) for record in pair]
        consistent += choices[0] == choices[1]
        if all(record.result.winner in {"A", "B"} for record in pair):
            positional_pairs += 1
            positional_flips += choices[0] != choices[1]

    positional_decisions = [
        record for record in records if record.result.winner in {"A", "B"}
    ]
    covered = [record for record in records if record.result.winner != "abstain"]
    pair_count = len(by_pair)

    return {
        "comparison_count": len(records),
        "pair_count": pair_count,
        "accuracy": _accuracy(records),
        "decision_coverage": len(covered) / len(records),
        "position_a_rate": (
            sum(r.result.winner == "A" for r in positional_decisions)
            / len(positional_decisions)
            if positional_decisions
            else 0.0
        ),
        "order_consistency_rate": consistent / pair_count,
        "position_flip_rate": (
            positional_flips / positional_pairs if positional_pairs else 0.0
        ),
        "by_language": _group_accuracy(records, "language"),
        "by_task": _group_accuracy(records, "task"),
        "by_perturbation": _group_accuracy(records, "perturbation"),
    }

