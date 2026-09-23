# Data and Result Schemas

## Dataset item

Required fields for a comparison record:

| Field | Meaning |
| --- | --- |
| `item_id` | Unique comparison identifier |
| `base_item_id` | Identifier shared by all variants and orders |
| `split` | `calibration`, `validation`, or `test` |
| `task` | `factual_qa`, `summarisation`, or `instruction_following` |
| `language` | `en` or `zh` |
| `prompt` | User question or instruction |
| `context` | Reference material, if applicable |
| `answer_a` | First candidate answer |
| `answer_b` | Second candidate answer |
| `gold_winner` | `A`, `B`, or `tie` |
| `perturbation` | Controlled change applied to one answer |
| `presentation_order` | `original` or `swapped` |

## Judge result

Every adapter returns:

```json
{
  "winner": "A",
  "score_a": 0.9,
  "score_b": 0.3,
  "confidence": 0.82,
  "reason_code": "factuality",
  "explanation": "Answer A is better supported by the supplied context."
}
```

`winner` may be `A`, `B`, `tie`, or `abstain`. Scores and confidence are in
the closed interval from 0 to 1. Raw model output and run metadata will be
stored alongside the parsed result in later phases.

## Pilot authoring source

`examples/pilot_base_items.jsonl` is the reviewed source of the pilot. Each
base item contains one clean answer and one variant for every perturbation.
`scripts/build_pilot.py` deterministically expands those records into
`examples/pilot.jsonl`. Generated comparison records should not be edited by
hand.
