# JudgeTrust Project Specification

## Decision problem

JudgeTrust audits an LLM used to compare two answers. It does not merely ask
whether the judge is accurate on average. It asks which decisions may be made
automatically under a stated error tolerance and which decisions must be
deferred to a human reviewer.

The first release focuses on bilingual English–Chinese evaluation of RAG and
question-answering outputs.

## Intended users

- ML engineers selecting or monitoring an automated evaluator
- Researchers studying LLM-as-a-Judge reliability
- Teams using LLM evaluation in model, prompt, or RAG regression tests

## Primary decision output

Given a target selective risk, initially 5%, report:

1. the fraction of cases that can be decided automatically (coverage);
2. the observed error rate among those decisions (selective risk);
3. uncertainty around that error rate;
4. the cases that should be deferred to a human.

If the evidence cannot support the target risk, JudgeTrust must report that the
judge is not safe for automated decisions at the requested threshold.

## Success criteria for the first release

- Evaluate at least one real judge on held-out bilingual data.
- Keep calibration, validation, and final test items separated by base item.
- Measure order consistency, controlled-bias sensitivity, calibration, risk,
  coverage, and abstention.
- Compare at least one mitigation with the unmitigated judge.
- Produce a reproducible machine-readable result and human-readable audit.

## Non-goals

- Training or fine-tuning a foundation model
- Claiming that a single benchmark proves universal judge reliability
- Replacing human review in high-stakes settings
- Maximising leaderboard accuracy without uncertainty estimates
- Supporting every task, language, and model provider in the first release

## Guardrails

- Paid APIs are optional and are not used until the offline pilot passes.
- Thresholds are selected without looking at the final test split.
- Variants derived from one base item remain in the same split.
- Negative or inconclusive results are valid outcomes.

