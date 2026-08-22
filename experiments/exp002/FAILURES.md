# Failure log

## Historical issue carried forward, not repaired in EXP001

EXP001's plastic-basis probe had an exactly zero update. It remains preserved. EXP002 contains a
new corrected control and a test that fails if its update norm is zero.

## EXP002 development failures

### v0: binary endpoint unreachable outside vector control

With causal strength 0.34, all 14 non-vector conditions had 0% plasticity-off evaluation success.
The primary/bandit nevertheless improved state by about 0.28 versus 0.11 frozen, and the explicit
vector control was 100%. This was an environment-scale failure, not evidence against a learning
mechanism. The complete v0 output is preserved at `results/exp002/development_v0/`. A documented
development-only causal-strength sweep led to 1.50; no learning rule or analysis was changed.

### v1: positive control did not expose its teaching vector to the measurement

The calibrated full development suite ran successfully, but the explicit-vector control used the
hidden vector to update motor policy while its modeled dendrite only expressed the resulting
policy. Soma conditioning therefore removed the shared signal and the control failed to validate
the residual analysis. This was a control implementation defect: a vector-error positive control
must express its neuron-indexed teaching signal after task feedback. Development v2 adds
`3 * error_improvement * c` only to the sensory-feedback, outcome, and post-outcome dendritic bins
of that explicitly forbidden condition. No Grossberg condition, metric, or threshold changed.
