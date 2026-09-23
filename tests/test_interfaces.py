import unittest

from judgetrust import JudgeRequest, JudgeResult


class InterfaceTests(unittest.TestCase):
    def test_request_supports_bilingual_pairwise_evaluation(self) -> None:
        request = JudgeRequest(
            item_id="qa-zh-001",
            task="factual_qa",
            language="zh",
            prompt="问题",
            answer_a="回答 A",
            answer_b="回答 B",
            context="参考材料",
        )

        self.assertEqual(request.language, "zh")
        self.assertEqual(request.context, "参考材料")

    def test_result_rejects_invalid_confidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "confidence"):
            JudgeResult(
                winner="A",
                score_a=0.8,
                score_b=0.2,
                confidence=1.1,
                reason_code="factuality",
                explanation="A is supported by the context.",
            )


if __name__ == "__main__":
    unittest.main()
