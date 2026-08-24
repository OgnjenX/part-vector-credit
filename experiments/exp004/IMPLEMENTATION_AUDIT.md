# EXP004 implementation and information-boundary audit

## Clean primary computation

```text
visible context/phase/state
  -> complement-coded ART category competition
  -> vigilance, resonance, reset/search, recruitment/modification
  -> category-specific scalar V(k,h)
  -> select fixed motor B_h
  -> noisy experienced soma S_t
  -> hidden environment c computes state transition
  -> visible delayed scalar outcome
  -> working-memory/eligibility trace assigns outcome to (k,h)
  -> value update changes later selection
  -> resonance-gated outstar update integrates S_t into T(k,h)
```

SMART, dendritic measurement, lower synaptic plasticity, and a cellular teaching vector are absent.

## Learner-visible information

- visible context code;
- normalized action phase;
- current normalized task state;
- its own fixed motor bank and selected h;
- experienced soma pattern;
- delayed scalar outcome/reward;
- internally generated category, match, reset, value, and eligibility states.

## Offline/environment-only information

- hidden c/P+/P− roles;
- coverage class, A_single, Q_single;
- oracle h or sequence;
- phase masks in the composition environment;
- bank-construction metadata.

The environment and offline analyses use these quantities. Primary selection, category, value, and outstar methods do not accept them. The one exception is the isolated explicit-hidden-vector positive control, guarded by a condition flag and a dedicated argument.

## Grossberg-derived versus engineered

| Component | Status | Simplification |
|---|---|---|
| Complement coding, fuzzy choice/match, vigilance, reset/search, category recruitment/modification | Grossberg-derived ART principles | Rate/discrete event abstraction, not a laminar/spiking ART circuit |
| Structural credit V(k,h) and delayed eligibility/working memory | pART-inspired / Grossberg-compatible | Scalar temporal-difference-like value update is engineering, not a reproduced pART equation |
| Outstar T update toward active lower pattern | Grossberg-derived associative principle | Simple bounded exponential average; no SMART dendritic circuit |
| Motivated gain on outstar rate | Grossberg-compatible abstraction | Scalar gain based on positive V |
| Fixed antithetic motor repertoire | Experimental manipulation | Not claimed as Grossberg anatomy |
| Phase-composition masks | Engineering diagnostic | Creates a valid sequential expressivity test; not a Francioni reproduction |
| Generic scalar motor plasticity | Non-Grossberg secondary control | Reward-weighted perturbation update; no hidden vector |
| Explicit vector control | Non-Grossberg positive control | Receives hidden c directly |

## Consequential distinctions

- A recruited category is a new memory state, not a new B.
- A new T vector is a learned representation, not a new motor command.
- Outcome can add information by changing selection/occupancy without adding a neuron-wise vector.
- Outstar can average/denoise targets but cannot leave their convex hull under the primary update.
- A bank can be oracle-solvable while the ART/value search architecture fails to find the solution.

## Append-only and confirmation controls

Development and confirmation outputs refuse overwrite. Confirmation requires a committed protocol with exact seed list, scenario order, output path, parameters, source hashes, thresholds, and untouched flag. Any post-confirmation repair becomes a later experiment/version and cannot overwrite `frozen_v1`.
