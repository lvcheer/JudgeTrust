import unittest
from pathlib import Path

from judgetrust import (
    FixedWinnerJudge,
    RecordedJudge,
    audit_selective_judge,
    build_pair_decisions,
    load_jsonl,
    run_judge,
    wilson_upper_bound,
)


ROOT = Path(__file__).resolve().parents[1]


class SelectiveAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = load_jsonl(ROOT / "examples" / "pilot.jsonl")

    def test_fixed_position_judge_defers_every_pair(self) -> None:
        records = run_judge(self.items, FixedWinnerJudge(winner="A"))
        decisions = build_pair_decisions(records)
        self.assertEqual(len(decisions), 96)
        self.assertTrue(all(decision.decision == "human" for decision in decisions))

    def test_pilot_cannot_certify_five_percent_even_with_zero_errors(self) -> None:
        judge = RecordedJudge.from_jsonl(
            ROOT / "examples" / "recorded_synthetic_reliable.jsonl"
        )
        report = audit_selective_judge(run_judge(self.items, judge), target_risk=0.05)
        self.assertEqual(report["status"], "insufficient_evidence")
        self.assertIsNone(report["selected_threshold"])

    def test_less_strict_target_can_be_selected_and_tested(self) -> None:
        judge = RecordedJudge.from_jsonl(
            ROOT / "examples" / "recorded_synthetic_reliable.jsonl"
        )
        report = audit_selective_judge(run_judge(self.items, judge), target_risk=0.11)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["selected_threshold"], 0.9)
        self.assertEqual(report["test_result"]["coverage"], 1.0)
        self.assertEqual(report["test_result"]["errors"], 0)

    def test_wilson_bound_is_nonzero_after_zero_observed_errors(self) -> None:
        self.assertGreater(wilson_upper_bound(0, 24), 0.10)
        self.assertLess(wilson_upper_bound(0, 24), 0.11)


if __name__ == "__main__":
    unittest.main()
