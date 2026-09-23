# Judge Adapter Contract

Every adapter receives a `JudgeRequest` without gold labels and returns a
validated `JudgeResult`. The shared prompt requests exactly one JSON object.
The parser intentionally rejects prose, Markdown fences, missing fields, extra
fields, invalid categories, empty explanations, and numeric values outside
`[0, 1]`.

`RecordedJudge` replays raw responses by `item_id`. It exercises the same parser
and evaluation path that a future local or API adapter will use, without making
network calls. The included recorded fixture is synthetic and exists only to
test infrastructure; it is not experimental evidence.

