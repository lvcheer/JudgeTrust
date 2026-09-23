"""Replay the full offline response fixture through the evaluation pipeline."""

import json
from pathlib import Path

from judgetrust import RecordedJudge, compute_metrics, load_jsonl, run_judge, write_run


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    dataset_path = ROOT / "examples" / "pilot.jsonl"
    fixture_path = ROOT / "examples" / "recorded_fake_a.jsonl"
    output = ROOT / "results" / "recorded-fake-a"
    judge = RecordedJudge.from_jsonl(fixture_path, name="recorded-fake-a")
    records = run_judge(load_jsonl(dataset_path), judge)
    write_run(
        records,
        output,
        dataset_path="examples/pilot.jsonl",
        judge_config={"fixture": "examples/recorded_fake_a.jsonl"},
    )
    metrics = compute_metrics(records)
    (output / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Replayed {len(records)} responses; accuracy={metrics['accuracy']:.3f}")


if __name__ == "__main__":
    main()

