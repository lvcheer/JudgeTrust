"""Run exactly two bilingual original/swapped pairs against local Ollama."""

import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from judgetrust import EvaluationRecord, OllamaJudge, compute_metrics, load_jsonl


ROOT = Path(__file__).resolve().parents[1]
SMOKE_IDS = {
    "fqa-en-001-correctness-original",
    "fqa-en-001-correctness-swapped",
    "fqa-zh-001-correctness-original",
    "fqa-zh-001-correctness-swapped",
}


def main() -> None:
    items = [
        item
        for item in load_jsonl(ROOT / "examples" / "pilot.jsonl")
        if item.item_id in SMOKE_IDS
    ]
    if {item.item_id for item in items} != SMOKE_IDS:
        raise RuntimeError("smoke-test records are missing from the pilot dataset")

    output = ROOT / "results" / "ollama-smoke"
    output.mkdir(parents=True, exist_ok=True)
    predictions_path = output / "predictions.jsonl"
    records: list[EvaluationRecord] = []
    timings: list[dict[str, float | str]] = []

    judge = OllamaJudge(model="qwen2.5:14b", timeout=180.0)
    with predictions_path.open("w", encoding="utf-8") as handle:
        for item in items:
            started = perf_counter()
            result = judge.evaluate(item.to_request())
            elapsed = perf_counter() - started
            record = EvaluationRecord(item=item, result=result, judge_name=judge.name)
            records.append(record)
            timings.append({"item_id": item.item_id, "elapsed_seconds": elapsed})
            handle.write(
                json.dumps(
                    {**record.to_dict(), "elapsed_seconds": elapsed},
                    ensure_ascii=False,
                )
                + "\n"
            )
            handle.flush()
            print(f"{item.item_id}: {result.winner} ({elapsed:.2f}s)")

    metrics = compute_metrics(records)
    summary = {
        "model": judge.model,
        "comparison_count": len(records),
        "total_seconds": sum(float(t["elapsed_seconds"]) for t in timings),
        "timings": timings,
        "metrics": metrics,
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

