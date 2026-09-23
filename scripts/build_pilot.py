"""Regenerate examples/pilot.jsonl from the reviewed authoring records."""

from pathlib import Path

from judgetrust.pilot import expand_base_items, load_base_items, write_jsonl


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    records = load_base_items(ROOT / "examples" / "pilot_base_items.jsonl")
    items = expand_base_items(records)
    output = ROOT / "examples" / "pilot.jsonl"
    write_jsonl(items, output)
    print(f"Wrote {len(items)} comparisons from {len(records)} base items to {output}")


if __name__ == "__main__":
    main()

