"""Create synthetic consistent responses for selective-risk pipeline tests."""

import json
from pathlib import Path

from judgetrust import load_jsonl


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    items = load_jsonl(ROOT / "examples" / "pilot.jsonl")
    output = ROOT / "examples" / "recorded_synthetic_reliable.jsonl"
    with output.open("w", encoding="utf-8") as handle:
        for item in items:
            winner = item.gold_winner
            if winner == "A":
                score_a, score_b = 0.95, 0.05
            elif winner == "B":
                score_a, score_b = 0.05, 0.95
            else:
                score_a, score_b = 0.5, 0.5
            response = json.dumps(
                {
                    "winner": winner,
                    "score_a": score_a,
                    "score_b": score_b,
                    "confidence": (
                        0.95
                        if item.perturbation in {"correctness", "unsupported_citation"}
                        else 0.9
                    ),
                    "reason_code": (
                        "citation"
                        if item.perturbation == "unsupported_citation"
                        else "factuality"
                    ),
                    "explanation": "Synthetic correct response for pipeline testing.",
                }
            )
            handle.write(
                json.dumps({"item_id": item.item_id, "response": response}) + "\n"
            )
    print(f"Wrote {len(items)} synthetic responses to {output}")


if __name__ == "__main__":
    main()

