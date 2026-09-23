import json
import unittest

from judgetrust import JudgeRequest, build_judge_prompt, parse_judge_response


def valid_response(**changes: object) -> str:
    value = {
        "winner": "A",
        "score_a": 0.9,
        "score_b": 0.2,
        "confidence": 0.8,
        "reason_code": "factuality",
        "explanation": "A is supported by the context.",
    }
    value.update(changes)
    return json.dumps(value)


class PromptingTests(unittest.TestCase):
    def test_prompt_matches_request_language_and_contains_no_gold(self) -> None:
        request = JudgeRequest("x", "factual_qa", "zh", "问题", "甲", "乙", "材料")
        prompt = build_judge_prompt(request)
        self.assertIn("独立的回答质量评审员", prompt)
        self.assertIn('"answer_a": "甲"', prompt)
        self.assertNotIn("gold_winner", prompt)

    def test_valid_json_is_parsed(self) -> None:
        self.assertEqual(parse_judge_response(valid_response()).winner, "A")

    def test_markdown_wrapped_json_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            parse_judge_response(f"```json\n{valid_response()}\n```")

    def test_missing_and_extra_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "fields mismatch"):
            parse_judge_response(valid_response(explanation_removed="extra"))

    def test_invalid_winner_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid winner"):
            parse_judge_response(valid_response(winner="C"))

    def test_out_of_range_confidence_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "confidence"):
            parse_judge_response(valid_response(confidence=1.2))


if __name__ == "__main__":
    unittest.main()

