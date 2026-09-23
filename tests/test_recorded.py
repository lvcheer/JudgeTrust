import tempfile
import unittest
from pathlib import Path

from judgetrust import RecordedJudge, compute_metrics, load_jsonl, run_judge


ROOT = Path(__file__).resolve().parents[1]


class RecordedJudgeTests(unittest.TestCase):
    def test_full_fixture_replays_through_pipeline(self) -> None:
        judge = RecordedJudge.from_jsonl(
            ROOT / "examples" / "recorded_fake_a.jsonl", name="recorded-fake-a"
        )
        records = run_judge(load_jsonl(ROOT / "examples" / "pilot.jsonl"), judge)
        metrics = compute_metrics(records)
        self.assertEqual(len(records), 192)
        self.assertEqual(metrics["accuracy"], 0.25)
        self.assertEqual(metrics["position_a_rate"], 1.0)

    def test_missing_record_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.jsonl"
            path.write_text("", encoding="utf-8")
            judge = RecordedJudge.from_jsonl(path)
            request = load_jsonl(ROOT / "examples" / "pilot.jsonl")[0].to_request()
            with self.assertRaisesRegex(KeyError, "no recorded response"):
                judge.evaluate(request)


if __name__ == "__main__":
    unittest.main()

