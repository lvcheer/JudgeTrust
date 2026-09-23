import tempfile
import unittest
from pathlib import Path

from judgetrust import DatasetItem, load_jsonl


def make_item(**changes: object) -> DatasetItem:
    values = {
        "item_id": "qa-en-001-correctness-original",
        "base_item_id": "qa-en-001",
        "split": "calibration",
        "task": "factual_qa",
        "language": "en",
        "prompt": "Question",
        "context": "Reference",
        "answer_a": "Supported answer",
        "answer_b": "Incorrect answer",
        "gold_winner": "A",
        "perturbation": "correctness",
        "presentation_order": "original",
    }
    values.update(changes)
    return DatasetItem.from_dict(values)


class DatasetItemTests(unittest.TestCase):
    def test_swap_changes_answers_label_and_order(self) -> None:
        original = make_item()
        swapped = original.swapped()

        self.assertEqual(swapped.answer_a, original.answer_b)
        self.assertEqual(swapped.answer_b, original.answer_a)
        self.assertEqual(swapped.gold_winner, "B")
        self.assertEqual(swapped.presentation_order, "swapped")
        self.assertEqual(swapped.swapped().gold_winner, "A")

    def test_gold_metadata_is_not_sent_to_judge(self) -> None:
        request = make_item().to_request()
        self.assertFalse(hasattr(request, "gold_winner"))

    def test_invalid_language_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "language"):
            make_item(language="fr")

    def test_duplicate_item_ids_are_rejected(self) -> None:
        line = (
            '{"item_id":"x","base_item_id":"base","split":"test",'
            '"task":"factual_qa","language":"en","prompt":"p",'
            '"context":null,"answer_a":"a","answer_b":"b",'
            '"gold_winner":"A","perturbation":"correctness",'
            '"presentation_order":"original"}\n'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.jsonl"
            path.write_text(line + line, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate item_id"):
                load_jsonl(path)


class ExampleDataTests(unittest.TestCase):
    def test_seed_file_is_valid_and_bilingual(self) -> None:
        root = Path(__file__).resolve().parents[1]
        items = load_jsonl(root / "examples" / "pilot_seed.jsonl")

        self.assertEqual(len(items), 4)
        self.assertEqual({item.language for item in items}, {"en", "zh"})
        self.assertEqual(
            {item.presentation_order for item in items}, {"original", "swapped"}
        )


if __name__ == "__main__":
    unittest.main()

