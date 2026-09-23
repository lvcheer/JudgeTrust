# Experiment Protocol

## Scope

The planned full dataset contains 96 base items: 48 English and 48 Chinese.
Each language contains factual QA, summarisation, and instruction-following
items in approximately equal proportions.

## Controlled variants

Each base item is paired with four independently controlled variants:

1. a decrease in factual or task correctness;
2. added verbosity without added correctness;
3. a style-only change;
4. an unsupported or fabricated citation.

Every comparison is presented in both A/B orders. The full design therefore
contains 96 x 4 x 2 = 768 comparisons per judge.

## Pilot

Before full data production, a 24-item pilot will exercise the same design,
producing 192 comparisons per judge. The pilot initially uses deterministic
fake and recorded adapters; a local model may be added without changing the
protocol.

The pilot is balanced across language and task: each English/Chinese and task
combination contains four base items. Correctness and unsupported-citation
variants have a preferred clean answer. Verbosity-only and style-only variants
are labelled as ties because their substantive content is intentionally held
constant. The pilot is for pipeline validation and exploratory estimates, not
for final inferential claims.

## Splitting

Base items, not individual variants, are assigned to calibration (20%),
validation (20%), and final test (60%) splits. All variants and both answer
orders from a base item remain together.

## Primary analysis

The primary analysis is a risk-coverage curve for automated decisions.
Threshold selection occurs on calibration/validation data. Final claims are
reported once on the held-out test set with uncertainty intervals clustered by
base item.

Secondary analyses include accuracy, order consistency, position flips,
language gaps, perturbation-specific error, Brier score, expected calibration
error, and high-confidence errors.

## Mitigation comparison

The first release will compare the raw judge with at least:

- dual-order evaluation;
- automatic abstention when the two orders disagree;
- language- or task-specific calibration when supported by sample size.
