"""Create a deterministic 192-response fixture for offline replay tests."""

import json
from pathlib import Path

from judgetrust import load_jsonl


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    items = load_jsonl(ROOT / "examples" / "pilot.jsonl")
    response = json.dumps(
        {
            "winner": "A",
            "score_a": 1.0,
            "score_b": 0.0,
            "confidence": 0.9,
            "reason_code": "uncertain",
            "explanation": "Deterministic recorded response for pipeline testing.",
        }
    )
    output = ROOT / "examples" / "recorded_fake_a.jsonl"
    with output.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(
                json.dumps(
                    {"item_id": item.item_id, "response": response},
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"Wrote {len(items)} recorded responses to {output}")


if __name__ == "__main__":
    main()

