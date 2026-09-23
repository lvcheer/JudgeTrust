"""Build the comparison-level pilot dataset from reviewed base items."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .data import DatasetItem, validate_paired_dataset

PERTURBATIONS = ("correctness", "verbosity", "style", "unsupported_citation")


def load_base_items(path: str | Path) -> list[dict[str, Any]]:
    """Load authoring records and reject malformed or duplicate base items."""
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    required = {
        "base_item_id",
        "split",
        "task",
        "language",
        "prompt",
        "context",
        "clean_answer",
        "variants",
    }
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid base item at line {line_number}: {error}") from error
            if set(record) != required:
                raise ValueError(f"invalid fields in base item at line {line_number}")
            if set(record["variants"]) != set(PERTURBATIONS):
                raise ValueError(f"invalid variants in base item at line {line_number}")
            if record["base_item_id"] in seen_ids:
                raise ValueError(f"duplicate base_item_id at line {line_number}")
            if any(not str(record["variants"][key]).strip() for key in PERTURBATIONS):
                raise ValueError(f"empty variant in base item at line {line_number}")
            seen_ids.add(record["base_item_id"])
            records.append(record)
    return records


def expand_base_items(records: list[dict[str, Any]]) -> list[DatasetItem]:
    """Expand each base item into four perturbations in both answer orders."""
    items: list[DatasetItem] = []
    for record in records:
        for perturbation in PERTURBATIONS:
            original = DatasetItem(
                item_id=(
                    f"{record['base_item_id']}-{perturbation}-original"
                ),
                base_item_id=record["base_item_id"],
                split=record["split"],
                task=record["task"],
                language=record["language"],
                prompt=record["prompt"],
                context=record["context"],
                answer_a=record["clean_answer"],
                answer_b=record["variants"][perturbation],
                gold_winner=(
                    "tie" if perturbation in {"verbosity", "style"} else "A"
                ),
                perturbation=perturbation,
                presentation_order="original",
            )
            items.extend((original, original.swapped()))
    validate_paired_dataset(items, expected_base_items=len(records))
    return items


def write_jsonl(items: list[DatasetItem], path: str | Path) -> None:
    """Write generated comparisons in stable UTF-8 JSONL form."""
    with Path(path).open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")

