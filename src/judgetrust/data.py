"""Dataset records and JSONL loading for controlled pairwise comparisons."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from .interfaces import JudgeRequest

Split = Literal["calibration", "validation", "test"]
Task = Literal["factual_qa", "summarisation", "instruction_following"]
Language = Literal["en", "zh"]
GoldWinner = Literal["A", "B", "tie"]
Perturbation = Literal["correctness", "verbosity", "style", "unsupported_citation"]
PresentationOrder = Literal["original", "swapped"]


@dataclass(frozen=True)
class DatasetItem:
    """One validated comparison presented to a judge."""

    item_id: str
    base_item_id: str
    split: Split
    task: Task
    language: Language
    prompt: str
    context: str | None
    answer_a: str
    answer_b: str
    gold_winner: GoldWinner
    perturbation: Perturbation
    presentation_order: PresentationOrder

    def __post_init__(self) -> None:
        allowed = {
            "split": {"calibration", "validation", "test"},
            "task": {"factual_qa", "summarisation", "instruction_following"},
            "language": {"en", "zh"},
            "gold_winner": {"A", "B", "tie"},
            "perturbation": {
                "correctness",
                "verbosity",
                "style",
                "unsupported_citation",
            },
            "presentation_order": {"original", "swapped"},
        }
        for field_name, valid_values in allowed.items():
            if getattr(self, field_name) not in valid_values:
                raise ValueError(f"invalid {field_name}: {getattr(self, field_name)!r}")

        for field_name in ("item_id", "base_item_id", "prompt", "answer_a", "answer_b"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.answer_a == self.answer_b:
            raise ValueError("answer_a and answer_b must differ")

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> DatasetItem:
        """Create and validate an item from decoded JSON."""
        return cls(**value)

    def swapped(self) -> DatasetItem:
        """Return the paired presentation with answers and the gold label swapped."""
        opposite_order: PresentationOrder = (
            "swapped" if self.presentation_order == "original" else "original"
        )
        opposite_winner: GoldWinner = {
            "A": "B",
            "B": "A",
            "tie": "tie",
        }[self.gold_winner]
        return replace(
            self,
            item_id=f"{self.base_item_id}-{self.perturbation}-{opposite_order}",
            answer_a=self.answer_b,
            answer_b=self.answer_a,
            gold_winner=opposite_winner,
            presentation_order=opposite_order,
        )

    def to_request(self) -> JudgeRequest:
        """Remove gold metadata before presenting the comparison to a judge."""
        return JudgeRequest(
            item_id=self.item_id,
            task=self.task,
            language=self.language,
            prompt=self.prompt,
            answer_a=self.answer_a,
            answer_b=self.answer_b,
            context=self.context,
        )


def load_jsonl(path: str | Path) -> list[DatasetItem]:
    """Load dataset items and report the source line of malformed records."""
    items: list[DatasetItem] = []
    seen_ids: set[str] = set()
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = DatasetItem.from_dict(json.loads(line))
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                raise ValueError(f"invalid record at line {line_number}: {error}") from error
            if item.item_id in seen_ids:
                raise ValueError(f"duplicate item_id at line {line_number}: {item.item_id}")
            seen_ids.add(item.item_id)
            items.append(item)
    return items


def validate_paired_dataset(
    items: list[DatasetItem], *, expected_base_items: int | None = None
) -> None:
    """Validate complete perturbation and order coverage for every base item."""
    expected_perturbations = {
        "correctness",
        "verbosity",
        "style",
        "unsupported_citation",
    }
    by_base: dict[str, list[DatasetItem]] = {}
    for item in items:
        by_base.setdefault(item.base_item_id, []).append(item)

    if expected_base_items is not None and len(by_base) != expected_base_items:
        raise ValueError(
            f"expected {expected_base_items} base items, found {len(by_base)}"
        )

    for base_item_id, records in by_base.items():
        if len(records) != 8:
            raise ValueError(f"{base_item_id} must have 8 records, found {len(records)}")
        if {record.perturbation for record in records} != expected_perturbations:
            raise ValueError(f"{base_item_id} does not contain all perturbations")

        for perturbation in expected_perturbations:
            pair = [record for record in records if record.perturbation == perturbation]
            orders = {record.presentation_order: record for record in pair}
            if set(orders) != {"original", "swapped"}:
                raise ValueError(
                    f"{base_item_id}/{perturbation} must contain both orders"
                )
            original = orders["original"]
            swapped = orders["swapped"]
            if original.swapped() != swapped:
                raise ValueError(
                    f"{base_item_id}/{perturbation} has an inconsistent swap"
                )

            expected_gold = "tie" if perturbation in {"verbosity", "style"} else "A"
            if original.gold_winner != expected_gold:
                raise ValueError(
                    f"{base_item_id}/{perturbation} must use gold {expected_gold}"
                )

