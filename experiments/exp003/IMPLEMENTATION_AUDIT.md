# EXP003 implementation audit

Status: **no EXP003 implementation exists at this checkpoint**.

## Preserved history

- EXP000 and EXP001 are not modified.
- The frozen EXP002 confirmation and interpretation at commit `bc2e46f` are not modified,
  rerun, overwritten, or treated as new evidence.
- EXP003 will use separate source modules, tests, entry points, and result directories.

## Required code boundary before development

The eventual implementation must enforce all of the following:

1. Environment-only hidden causal roles. The main learner may never own, receive, or derive an
   array containing `c`, `P+`, `P-`, `delta_i`, or `dE/dS_i`.
2. Positive-control access must pass through an explicitly named, condition-guarded interface.
3. Motor output must depend on `B` and `W_lower`, never on the measured apical branch alone.
4. `T` and `B` must be independently initialized; `T` may not be assigned or copied from `B` in
   the primary model.
5. `D` must arise from active `H_{k,h}` through learned `T_{k,h}`.
6. `T` may affect `W_lower` only by changing local lower-cell state/spike timing and resonance,
   then applying the documented SMART-derived local law.
7. Scalar reward may change representation selection/gain but may not be multiplied by a
   neuron-indexed pattern inside the primary local update.
8. `W_lower` must affect a later soma response. Unit tests must demonstrate this causal direction.
9. All longitudinal statistics must have a within-hypothesis form that holds `h` fixed.
10. Learned categories must be recruited from visible observations, not supplied as fixed A/B
    vector slots.

## Mandatory tests before any development sweep

- initial `B`, `T`, `W`, category ID, hypothesis ID, and neuron index leakage correlations;
- label-permutation decoding with a fixed null procedure;
- replay invariance: hidden-role permutation with identical visible/local replay cannot alter a
  Grossberg-condition update;
- nonzero, bounded SMART update for matched pre/post timing;
- no update for mismatch/reset and for the preregistered out-of-window timing case;
- cell selectivity caused by on-center/off-surround timing differences;
- learned `T` without `T -> W` in the dedicated ablation;
- unchanged immediate motor action when only apical expression is suppressed;
- changed future soma when and only when `W_lower` changes;
- no top-down equality/copy with `B` in the primary model;
- frame-by-frame environment feedback before the next action frame;
- distinct computations for every mandatory condition.

## Open implementation decisions

These remain unresolved and therefore block protocol freezing, but not the theory audit:

- exact stable discrete integration of SMART Equation 5 and its spike-time gate;
- within-frame timescale separating pre-action, action, sensory feedback, match, outcome, and
  plasticity;
- whether the reduced cell model needs explicit spike times or a trace formulation that can be
  numerically validated against the published window;
- development seed count and computational budget;
- the observable feature representation used by the ART category layer;
- a non-arbitrary joint endpoint for comparing the primary and generic-Hebbian control.

None may be resolved using held-out results.
