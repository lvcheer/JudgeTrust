"""Offline evaluation runner and reproducible result serialization."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .data import DatasetItem
from .interfaces import Judge, JudgeResult


@dataclass(frozen=True)
class EvaluationRecord:
    """A dataset item paired with one judge prediction."""

    item: DatasetItem
    result: JudgeResult
    judge_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self.item),
            "judge_name": self.judge_name,
            "prediction": asdict(self.result),
        }


def run_judge(items: list[DatasetItem], judge: Judge) -> list[EvaluationRecord]:
    """Evaluate items sequentially while keeping gold labels hidden."""
    return [
        EvaluationRecord(
            item=item,
            result=judge.evaluate(item.to_request()),
            judge_name=judge.name,
        )
        for item in items
    ]


def write_run(
    records: list[EvaluationRecord],
    output_dir: str | Path,
    *,
    dataset_path: str,
    judge_config: dict[str, Any],
) -> None:
    """Write predictions and the minimal metadata needed to identify a run."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    predictions_path = directory / "predictions.jsonl"
    with predictions_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    metadata = {
        "schema_version": 1,
        "dataset_path": dataset_path,
        "judge_name": records[0].judge_name if records else None,
        "judge_config": judge_config,
        "comparison_count": len(records),
    }
    (directory / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

