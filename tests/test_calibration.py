import json
import unittest
from dataclasses import replace
from pathlib import Path

from judgetrust import (
    IsotonicCalibrator,
    RecordedJudge,
    audit_calibrated_judge,
    build_pair_decisions,
    calibration_metrics,
    load_jsonl,
    run_judge,
)


ROOT = Path(__file__).resolve().parents[1]


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        items = load_jsonl(ROOT / "examples" / "pilot.jsonl")
        judge = RecordedJudge.from_jsonl(
            ROOT / "examples" / "recorded_synthetic_overconfident.jsonl"
        )
        cls.records = run_judge(items, judge)
        cls.calibration = [
            decision
            for decision in build_pair_decisions(cls.records)
            if decision.split == "calibration"
        ]

    def test_isotonic_calibration_improves_overconfident_fixture(self) -> None:
        before = calibration_metrics(self.calibration)
        calibrator = IsotonicCalibrator.fit(self.calibration)
        calibrated = [
            replace(decision, confidence=calibrator.predict(decision.confidence))
            for decision in self.calibration
        ]
        after = calibration_metrics(calibrated)
        self.assertAlmostEqual(before["brier_score"], 0.41)
        self.assertAlmostEqual(after["brier_score"], 0.25)
        self.assertAlmostEqual(before["ece"], 0.4)
        self.assertAlmostEqual(after["ece"], 0.0)

    def test_calibrator_round_trips_through_json(self) -> None:
        calibrator = IsotonicCalibrator.fit(self.calibration)
        restored = IsotonicCalibrator.from_dict(
            json.loads(json.dumps(calibrator.to_dict()))
        )
        self.assertEqual(restored.predict(0.9), calibrator.predict(0.9))

    def test_audit_keeps_calibration_validation_and_test_separate(self) -> None:
        report = audit_calibrated_judge(self.records, target_risk=0.05)
        self.assertEqual(report["status"], "insufficient_evidence")
        self.assertIsNone(report["test_result"])
        self.assertEqual(report["calibration_metrics_before"]["count"], 24)
        self.assertTrue(
            all(point["total_pairs"] == 24 for point in report["selection_curve"])
        )


if __name__ == "__main__":
    unittest.main()

