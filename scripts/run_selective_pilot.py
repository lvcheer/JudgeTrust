"""Demonstrate risk-controlled deferral using synthetic recorded responses."""

import json
from pathlib import Path

from judgetrust import RecordedJudge, audit_selective_judge, load_jsonl, run_judge


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    judge = RecordedJudge.from_jsonl(
        ROOT / "examples" / "recorded_synthetic_reliable.jsonl",
        name="recorded-synthetic-reliable",
    )
    records = run_judge(load_jsonl(ROOT / "examples" / "pilot.jsonl"), judge)
    report = audit_selective_judge(records, target_risk=0.05)
    output = ROOT / "results" / "selective-pilot"
    output.mkdir(parents=True, exist_ok=True)
    (output / "audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "status": report["status"],
        "target_risk": report["target_risk"],
        "selected_threshold": report["selected_threshold"],
        "test_result": report["test_result"],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

