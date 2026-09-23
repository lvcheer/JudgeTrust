"""Run the deliberately position-biased fake judge on the pilot dataset."""

import json
from pathlib import Path

from judgetrust import FixedWinnerJudge, compute_metrics, load_jsonl, run_judge, write_run


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    dataset = ROOT / "examples" / "pilot.jsonl"
    output = ROOT / "results" / "fake-fixed-a"
    judge = FixedWinnerJudge(winner="A", confidence=0.9, name="fake-fixed-a")
    records = run_judge(load_jsonl(dataset), judge)
    write_run(
        records,
        output,
        dataset_path="examples/pilot.jsonl",
        judge_config={"winner": "A", "confidence": 0.9},
    )
    metrics = compute_metrics(records)
    (output / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

