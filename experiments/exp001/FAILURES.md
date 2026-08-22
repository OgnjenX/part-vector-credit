# EXP001 failure and decision log

Entries are append-only. Development and confirmatory failures are not removed.

## 2026-08-22 — Pre-development smoke run

A two-seed, 200-trial smoke run passed all unit tests. The explicit vector-error
positive control learned the behavior but failed the dendritic role metric. The
cause was not a learning failure: the simulated dendritic trace contained selected
top-down activity but no task-error-change modulation, whereas the preregistered
analysis contrasted somato-dendritic residuals across error-change epochs.

Before any development-seed run, an outcome-phase measurement component was added:
observable scalar change in visual error multiplies the already-selected top-down
pattern. In the Grossberg-inspired conditions this remains a global scalar routed
through a selected representation. In the explicit positive control only, the
hidden causal vector replaces that pattern. Criteria and learner updates were not
changed. This decision is an engineered functional abstraction, documented in the
theory map; it is not asserted to reproduce SMART dendritic equations.

## 2026-08-22 — Initial development configuration failed behavior

With reinforcement rate 0.12, full-model success improved but plateaued at 0.525
before remapping and 0.514 afterward. The explicit-vector control reached 1.000.
The prespecified one-factor sweep identified 0.30 as the only tested reinforcement
rate meeting behavioral criteria; the choice and all alternatives are preserved in
`PARAMETER_LOG.md` and `results/exp001/exp001_development.*`.

## 2026-08-22 — Frozen development: behavioral selection, cellular criterion failed

At the development-selected rate 0.30, full-model success reached 0.716 before and
0.802 after remapping. Yet its post-remap residual-to-later-soma correlation was
−0.089, failing the frozen ≥0.20 longitudinal criterion. Moreover, instantaneous
post-remap dendritic role alignment was 0.448 in full, but also 0.432 in frozen,
0.476 in random-policy, and 0.537 under shuffled feedback. This signature can arise
from closed-loop covariance between a random action, its global error change, and
the same action pattern used in the dendritic proxy. It is not evidence that a
neuron-specific instructive signal was learned.

The outcome classifier initially omitted the longitudinal clause even though it
was present in the preregistered protocol. It was corrected before confirmatory
execution; no criterion or numerical threshold changed.

## 2026-08-22 — Held-out confirmation

On seeds 1000–1029, full-model late success reached 0.728 before and 0.716 after
hidden remapping; the explicit-vector control reached 1.000. The full model again
failed the longitudinal cellular criterion: post-remap residual-to-later-soma
correlation was 0.124 rather than ≥0.20. No parameters or thresholds were revised.
The final classification is Outcome 3, with the behavioral success attributed to
Outcome-2 pre-existing basis selection.

After confirmation, heterogeneous hidden causal weights were added as a separately
labeled exploratory generalization probe. Default-weight execution is unchanged
and the held-out confirmation was not rerun.
