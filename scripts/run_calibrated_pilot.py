"""Run the three-way calibration, threshold selection, and test workflow."""

import json
from pathlib import Path

from judgetrust import RecordedJudge, audit_calibrated_judge, load_jsonl, run_judge


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    judge = RecordedJudge.from_jsonl(
        ROOT / "examples" / "recorded_synthetic_overconfident.jsonl",
        name="recorded-synthetic-overconfident",
    )
    records = run_judge(load_jsonl(ROOT / "examples" / "pilot.jsonl"), judge)
    report = audit_calibrated_judge(records, target_risk=0.05)
    output = ROOT / "results" / "calibrated-pilot"
    output.mkdir(parents=True, exist_ok=True)
    (output / "audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "before": report["calibration_metrics_before"],
                "after": report["calibration_metrics_after"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

