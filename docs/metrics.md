# Metric Definitions

- **Accuracy**: exact agreement between `winner` and `gold_winner`. An
  abstention is not counted as correct.
- **Decision coverage**: fraction of records for which the judge does not
  abstain. This is descriptive until a risk threshold is introduced.
- **Position A rate**: fraction of A/B decisions that select position A.
- **Order consistency**: fraction of original/swapped pairs that choose the
  same underlying content (`clean`, `variant`, `tie`, or `abstain`).
- **Position flip rate**: among pairs with an A/B decision in both orders, the
  fraction that switch the selected underlying content when positions swap.

Accuracy is also reported by language, task, and perturbation.

## Selective automation

The unit of an automation decision is an original/swapped pair. If the two
orders do not select the same underlying content, the pair is deferred to a
human. Otherwise, the lower of the two reported confidences is used.

- **Selective risk**: error rate among automatically decided pairs.
- **Coverage**: automatically decided pairs divided by all pairs.
- **Risk upper 95%**: one-sided 95% Wilson upper confidence bound for the
  selective error rate.

An isotonic calibrator is fitted only on the calibration split. Thresholds are
then selected only on validation records, and the selected threshold is
evaluated once on the test split. Brier score, expected calibration error
(ECE), and reliability bins are reported before and after calibration. A zero observed
error rate is not treated as proof of zero risk: if the upper confidence bound
exceeds the target, the result is `insufficient_evidence` or `failed_on_test`.
