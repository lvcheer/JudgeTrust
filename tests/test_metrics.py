import json
import tempfile
import unittest
from pathlib import Path

from judgetrust import (
    FixedWinnerJudge,
    compute_metrics,
    load_jsonl,
    run_judge,
    write_run,
)


ROOT = Path(__file__).resolve().parents[1]


class EvaluationMetricsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = load_jsonl(ROOT / "examples" / "pilot.jsonl")
        cls.records = run_judge(
            cls.items,
            FixedWinnerJudge(winner="A", confidence=0.9, name="fake-fixed-a"),
        )
        cls.metrics = compute_metrics(cls.records)

    def test_fixed_a_judge_exposes_position_bias(self) -> None:
        self.assertEqual(self.metrics["comparison_count"], 192)
        self.assertEqual(self.metrics["accuracy"], 0.25)
        self.assertEqual(self.metrics["position_a_rate"], 1.0)
        self.assertEqual(self.metrics["order_consistency_rate"], 0.0)
        self.assertEqual(self.metrics["position_flip_rate"], 1.0)

    def test_group_metrics_have_expected_accuracy(self) -> None:
        groups = self.metrics["by_perturbation"]
        self.assertEqual(groups["correctness"], {"count": 48, "accuracy": 0.5})
        self.assertEqual(groups["style"], {"count": 48, "accuracy": 0.0})

    def test_run_artifacts_include_predictions_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            write_run(
                self.records,
                directory,
                dataset_path="examples/pilot.jsonl",
                judge_config={"winner": "A"},
            )
            predictions = Path(directory) / "predictions.jsonl"
            metadata = json.loads((Path(directory) / "metadata.json").read_text())
            self.assertEqual(len(predictions.read_text().splitlines()), 192)
            self.assertEqual(metadata["comparison_count"], 192)
            self.assertEqual(metadata["judge_name"], "fake-fixed-a")


if __name__ == "__main__":
    unittest.main()

