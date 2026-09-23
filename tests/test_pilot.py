import unittest
from collections import Counter
from pathlib import Path

from judgetrust import load_jsonl, validate_paired_dataset
from judgetrust.pilot import expand_base_items, load_base_items


ROOT = Path(__file__).resolve().parents[1]


class PilotDatasetTests(unittest.TestCase):
    def test_authoring_data_expands_to_balanced_pilot(self) -> None:
        records = load_base_items(ROOT / "examples" / "pilot_base_items.jsonl")
        items = expand_base_items(records)

        self.assertEqual(len(records), 24)
        self.assertEqual(len(items), 192)
        self.assertEqual(Counter(record["language"] for record in records), {"en": 12, "zh": 12})
        self.assertEqual(
            Counter(record["task"] for record in records),
            {"factual_qa": 8, "summarisation": 8, "instruction_following": 8},
        )

    def test_generated_pilot_is_complete_and_consistent(self) -> None:
        items = load_jsonl(ROOT / "examples" / "pilot.jsonl")
        validate_paired_dataset(items, expected_base_items=24)
        self.assertEqual(len(items), 192)


if __name__ == "__main__":
    unittest.main()

