"""Create consistent but overconfident synthetic responses for calibration tests."""

import json
from pathlib import Path

from judgetrust import load_jsonl


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    items = load_jsonl(ROOT / "examples" / "pilot.jsonl")
    pair_keys = sorted({(item.base_item_id, item.perturbation) for item in items})
    correct_by_pair = {key: index % 2 == 0 for index, key in enumerate(pair_keys)}
    output = ROOT / "examples" / "recorded_synthetic_overconfident.jsonl"
    with output.open("w", encoding="utf-8") as handle:
        for item in items:
            correct = correct_by_pair[(item.base_item_id, item.perturbation)]
            if correct:
                winner = item.gold_winner
            elif item.gold_winner == "A":
                winner = "B"
            elif item.gold_winner == "B":
                winner = "A"
            else:
                winner = "A" if item.presentation_order == "original" else "B"
            score_a, score_b = {
                "A": (0.9, 0.1),
                "B": (0.1, 0.9),
                "tie": (0.5, 0.5),
            }[winner]
            response = json.dumps(
                {
                    "winner": winner,
                    "score_a": score_a,
                    "score_b": score_b,
                    "confidence": 0.9,
                    "reason_code": "uncertain",
                    "explanation": "Synthetic overconfident response for calibration testing.",
                }
            )
            handle.write(
                json.dumps({"item_id": item.item_id, "response": response}) + "\n"
            )
    print(f"Wrote {len(items)} overconfident responses to {output}")


if __name__ == "__main__":
    main()

