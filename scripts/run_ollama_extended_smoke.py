"""Run six representative bilingual pairs against local Ollama."""

import json
from pathlib import Path
from time import perf_counter

from judgetrust import EvaluationRecord, OllamaJudge, compute_metrics, load_jsonl


ROOT = Path(__file__).resolve().parents[1]
PAIR_KEYS = {
    ("fqa-en-002", "unsupported_citation"),
    ("fqa-zh-002", "style"),
    ("sum-en-001", "verbosity"),
    ("sum-zh-001", "unsupported_citation"),
    ("if-en-001", "style"),
    ("if-zh-001", "correctness"),
}


def main() -> None:
    items = [
        item
        for item in load_jsonl(ROOT / "examples" / "pilot.jsonl")
        if (item.base_item_id, item.perturbation) in PAIR_KEYS
    ]
    if len(items) != 12:
        raise RuntimeError(f"expected 12 smoke-test records, found {len(items)}")

    output = ROOT / "results" / "ollama-extended-smoke"
    output.mkdir(parents=True, exist_ok=True)
    records: list[EvaluationRecord] = []
    timings: list[dict[str, float | str]] = []
    judge = OllamaJudge(model="qwen2.5:14b", timeout=180.0)

    with (output / "predictions.jsonl").open("w", encoding="utf-8") as handle:
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
            print(
                f"{item.item_id}: predicted={result.winner} "
                f"gold={item.gold_winner} ({elapsed:.2f}s)"
            )

    summary = {
        "model": judge.model,
        "comparison_count": len(records),
        "total_seconds": sum(float(t["elapsed_seconds"]) for t in timings),
        "timings": timings,
        "metrics": compute_metrics(records),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

