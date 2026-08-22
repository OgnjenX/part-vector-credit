# EXP003b frozen protocol

Status before confirmation: **frozen after development; held-out seeds untouched**.
The machine-readable lock is `FROZEN_PROTOCOL.json`.

## Question

Can scalar-outcome selection of a pART-inspired causal representation, its learned
context-specific ART-outstar expectation, and the independently validated SMART
local timing motif jointly generate the Francioni longitudinal dendrite→cellular-
plasticity signature without a neuron-wise error vector?

## Fixed design

- Neurons: 8; hidden balanced causal roles; context B has the opposite roles.
- Hypotheses: 16 (8 independently sampled antithetic pairs).
- ART capacity: 18; visual bins: 7; vigilance: 0.88.
- Each episode: 3 genuinely closed-loop action frames, then 4 distractors and
  delayed scalar outcome.
- Acquisition: 100 episodes; frozen evaluation: 20; secret full remap; relearning:
  120; frozen evaluation: 20.
- Development seeds: 41–44. Held-out seeds: 3100–3111.
- Confirmation runs all conditions on all 12 held-out seeds exactly once.
- Brian2 SMART-cache and all source hashes are checked before confirmation.

The complete parameter object is frozen in `FROZEN_PROTOCOL.json` and repeated in
each result summary.

## Conditions

1. frozen/no learning;
2. random controller;
3. contextual bandit;
4. bandit + direct motor-pattern copy to apical readout;
5. bandit + scalar-gated generic local Hebb;
6. pART-inspired selection without learned expectancy;
7. pART-inspired learned `T` without SMART plasticity;
8. primary pART-inspired + learned `T` + SMART;
9. primary without structural credit;
10. primary without working-memory retention;
11. primary without motivated reinforcement;
12. primary without reset/search;
13. primary without resonance gating;
14. primary with neuron-shuffled top-down feedback;
15. primary with `T` learning disabled;
16. primary with learned/measured `T` blocked from SMART;
17. primary with apical expression suppressed only during frozen evaluation;
18. corrected motor-basis outstar probe; and
19. explicit hidden-vector positive control.

## Primary endpoints

All correlations are averaged first across the two contexts within seed and then
across held-out seeds. Confidence intervals are nonparametric 5,000-resample
seed-level bootstrap intervals.

- pre/post frozen-evaluation reward success;
- initial motor, top-down and lower-weight leakage metrics;
- pre/post selected-`T` alignment to current hidden role;
- old-`T` alignment immediately under the new remapped role;
- opposing-context `T` opposition;
- within-fixed-hypothesis `D_residual_early→delta_W` and
  `D_residual_early→delta_S_probe`, before and after remap;
- paired primary-minus-`T→SMART`-blocked effects;
- counterfactual top-down-created-spike fraction and first-spike latency advance;
- expression-only evaluation behavior; and
- positive-control validity.

The dendritic residual regresses dendrite on intercept, same-neuron soma and
population-mean soma. `D_early` is the median-split difference between globally
error-improving and error-worsening frames. A fixed hypothesis needs at least four
early and two late records; otherwise its longitudinal endpoint is zero.

## Frozen support floors

Outcome A requires every item below and requires the generic Hebbian baseline not
to pass its full-chain criterion.

- Primary minus both frozen and random success ≥ 0.10 before and after remap,
  with paired 95% CI lower bound > 0.
- Absolute initial mean signed correlations < 0.05; decoder excess over its
  permutation-null mean ≤ 0.15.
- Pre- and post-remap `T` alignment increases ≥ 0.20 above initial alignment.
- All four primary longitudinal correlations ≥ 0.20 with CI lower bound > 0.
- Each primary-minus-`T→SMART`-blocked longitudinal effect ≥ 0.15 with paired CI
  lower bound > 0.
- Top-down creates some spikes or advances latency.
- Expression suppression changes pre/post evaluation success by at most 0.05.
- Post-remap selected-`T` minus old-`T` alignment ≥ 0.20.
- Context opposition ≥ 0.25.
- Positive control success ≥ 0.80 before and after remap and all four
  longitudinal correlations ≥ 0.20 with CI lower bound > 0.

## Frozen classification

- **A**: all strong-support criteria pass and generic Hebb does not.
- **B**: generic Hebb beats frozen/random behavior by ≥0.10 pre/post and all four
  of its longitudinal correlations are ≥0.20.
- **C**: the positive control validates the assay, primary behavior passes, but
  the primary longitudinal chain fails.
- **E**: positive control fails or results do not meet those discriminating cases.

Category D was decided before simulation: primary-source audit found a defensible
local SMART timing mechanism, so the mechanism can be specified, albeit only as a
cross-system composition.

No threshold is lowered after confirmation. Any source or metric repair after the
frozen run must be a new experiment/checkpoint.
