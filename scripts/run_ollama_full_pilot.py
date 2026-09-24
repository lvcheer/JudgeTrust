"""Run all 192 pilot comparisons with resumable, guarded checkpoints."""

import hashlib
import json
import random
from pathlib import Path
from time import perf_counter

from judgetrust import (
    DatasetItem,
    EvaluationRecord,
    JudgeResult,
    OllamaJudge,
    audit_calibrated_judge,
    compute_metrics,
    load_jsonl,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "examples" / "pilot.jsonl"
OUTPUT = ROOT / "results" / "ollama-full-pilot-v2"
MODEL = "qwen2.5:14b"
SHUFFLE_SEED = 20260923
PROMPT_VERSION = "v2-json-schema"


def dataset_hash() -> str:
    return hashlib.sha256(DATASET.read_bytes()).hexdigest()


def expected_metadata() -> dict[str, object]:
    return {
        "schema_version": 1,
        "dataset": "examples/pilot.jsonl",
        "dataset_sha256": dataset_hash(),
        "model": MODEL,
        "shuffle_seed": SHUFFLE_SEED,
        "prompt_version": PROMPT_VERSION,
        "comparison_count": 192,
    }


def load_completed(path: Path) -> list[EvaluationRecord]:
    if not path.exists():
        return []
    records: list[EvaluationRecord] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        row = json.loads(line)
        item_id = row.get("item_id")
        if item_id in seen:
            raise RuntimeError(f"duplicate checkpoint item at line {line_number}: {item_id}")
        seen.add(item_id)
        item_fields = {
            key: value
            for key, value in row.items()
            if key not in {"judge_name", "prediction", "elapsed_seconds"}
        }
        records.append(
            EvaluationRecord(
                item=DatasetItem.from_dict(item_fields),
                result=JudgeResult(**row["prediction"]),
                judge_name=row["judge_name"],
            )
        )
    return records


def main() -> None:
    items = load_jsonl(DATASET)
    if len(items) != 192:
        raise RuntimeError(f"expected 192 comparisons, found {len(items)}")
    random.Random(SHUFFLE_SEED).shuffle(items)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    metadata_path = OUTPUT / "metadata.json"
    metadata = expected_metadata()
    if metadata_path.exists():
        saved = json.loads(metadata_path.read_text(encoding="utf-8"))
        if saved != metadata:
            raise RuntimeError("saved run metadata does not match this experiment")
    else:
        metadata_path.write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )

    predictions_path = OUTPUT / "predictions.jsonl"
    records = load_completed(predictions_path)
    completed_ids = {record.item.item_id for record in records}
    dataset_ids = {item.item_id for item in items}
    if not completed_ids <= dataset_ids:
        raise RuntimeError("checkpoint contains item IDs outside the current dataset")

    remaining = [item for item in items if item.item_id not in completed_ids]
    print(
        f"Starting full pilot: completed={len(records)} remaining={len(remaining)}",
        flush=True,
    )
    judge = OllamaJudge(model=MODEL, timeout=180.0)
    run_started = perf_counter()
    error_path = OUTPUT / "error.json"
    with predictions_path.open("a", encoding="utf-8") as handle:
        for item in remaining:
            started = perf_counter()
            try:
                result = judge.evaluate(item.to_request())
            except Exception as error:
                error_path.write_text(
                    json.dumps(
                        {
                            "item_id": item.item_id,
                            "error_type": type(error).__name__,
                            "message": str(error),
                            "completed_count": len(records),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                raise
            elapsed = perf_counter() - started
            record = EvaluationRecord(item=item, result=result, judge_name=judge.name)
            records.append(record)
            handle.write(
                json.dumps(
                    {**record.to_dict(), "elapsed_seconds": elapsed},
                    ensure_ascii=False,
                )
                + "\n"
            )
            handle.flush()
            print(
                f"[{len(records):03d}/192] {item.item_id}: "
                f"predicted={result.winner} gold={item.gold_winner} "
                f"confidence={result.confidence:.2f} time={elapsed:.2f}s",
                flush=True,
            )

    if error_path.exists():
        error_path.unlink()
    metrics = compute_metrics(records)
    audit = audit_calibrated_judge(records, target_risk=0.05)
    summary = {
        **metadata,
        "run_seconds_this_invocation": perf_counter() - run_started,
        "metrics": metrics,
        "audit_status": audit["status"],
        "selected_threshold": audit["selected_threshold"],
        "test_result": audit["test_result"],
    }
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT / "audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
