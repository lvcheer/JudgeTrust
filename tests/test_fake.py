import unittest

from judgetrust import FixedWinnerJudge, JudgeRequest


class FixedWinnerJudgeTests(unittest.TestCase):
    def test_returns_same_reproducible_result(self) -> None:
        request = JudgeRequest(
            item_id="example",
            task="factual_qa",
            language="en",
            prompt="Question",
            answer_a="A",
            answer_b="B",
        )
        judge = FixedWinnerJudge(winner="A", confidence=0.8)

        self.assertEqual(judge.evaluate(request), judge.evaluate(request))
        self.assertEqual(judge.evaluate(request).winner, "A")


if __name__ == "__main__":
    unittest.main()

