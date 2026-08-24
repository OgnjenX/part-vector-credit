# EXP004 protocol — origin of neuron-specific topology

Protocol status: **FROZEN before confirmation**. Held-out seeds have not been executed. The exact machine-readable lock is in `FROZEN_PROTOCOL.json`; its development checkpoint is `bcd6c838d04b8d21892ec0177bdb5605bc0f068e`.

## Primary question

Can scalar outcome, delayed structural credit, plastic ART categories, and outstar learning acquire an arbitrary neuron-resolved T over a fixed action repertoire? Or do behavior and T remain limited by pre-existing motor/soma directions?

The clean primary contains no SMART, dendritic proxy, lower plasticity, motor-basis plasticity, or neuron-indexed teaching vector.

## Confirmatory units

- Independent unit: hidden-mapping/bank seed.
- Development seeds: 101–104.
- Held-out seeds: 7000–7015.
- Neurons: 32 balanced hidden roles.
- Contexts: two; context B reverses c.
- Action frames: three, closed loop.
- Outcome delay: four distractor steps, yielding WM strength \(0.9^4\).
- Evaluation: 80 episodes after learning, no exploration/category/value/T update.

## Experience regimes

- **Fixed:** 512 training episodes for every M.
- **Search-normalized:** \(16M\) training episodes, equal to 48 action opportunities per hypothesis before exploration/policy concentration.

The search-normalized rule was chosen before held-out access. It deliberately equalizes total opportunities, not guaranteed exploratory visits.

## Scenario suite

Fifty-eight paired scenarios are generated from the same c/bank seeds:

1. M = 2,4,8,16,32,64,128 × fixed/search-normalized × random selector/contextual bandit/primary ART-outstar: 42.
2. Controlled LOW/MEDIUM/HIGH × contextual bandit/primary: 6.
3. Medium coverage ART ablations: fixed categories, no new recruitment, no category modification: 3.
4. Medium outcome controls: online outcome shuffle and random credited-h target: 2.
5. Low-coverage extensions: generic scalar perturbation-based motor plasticity and explicit hidden-vector control: 2.
6. Low-single-coverage phase-composition × random/bandit/primary: 3.

Scenario order is frozen in `FROZEN_PROTOCOL.json`.

## Primary explanatory tests

1. Nested M → A_single/Q_single → behavior/T relationships.
2. Cluster-bootstrap mediation of log2(M) through initial coverage.
3. Fixed-M controlled coverage → behavior and T.
4. Learner behavior relative to best repeated-single and best allowed-sequence oracles.
5. ART category contribution after identical coverage/experience.
6. Exact T reconstruction and improvement over individual initial/experienced patterns.
7. Online outcome controls and frozen-visitation outcome-permutation replay.

## Frozen effect floors

| Criterion | Floor |
|---|---:|
| Behavioral/coverage/category substantive effect | 0.15 / 0.10 as named |
| Composition advantage over repeated single | 0.15 with CI > 0 |
| Gap to allowed sequence for B2 | ≤ 0.10 |
| Copy similarity corr(T, selected initial soma) | ≥ 0.95 |
| Representational gain over every target | ≥ 0.10 |
| Same-h category T distance for R3 | ≥ 0.10 |
| Outcome-information T effect | ≥ 0.15 with CI > 0 |
| Additional motor-plasticity effect | ≥ 0.20 with CI > 0 |
| Exact reconstruction RMSE | ≤ \(10^{-8}\) |

Seed-bootstrap intervals use 5,000 resamples. M mediation resamples seed clusters so nested banks are not treated as independent.

## Two-axis classification

Behavioral B1–B4 and representational R1–R4 flags are evaluated independently as specified in `SOLVABILITY_AND_ORACLES.md`, `REPRESENTATIONAL_REACHABILITY.md`, and frozen statistics source. Multiple behavioral flags may be true in different task regimes.

A2 is classified:

- **weak-form supported** if real outcome association contributes at least 0.15 to T with CI above zero and T is exactly reachable;
- **repertoire-limited** if controlled HIGH–LOW behavior differs by at least 0.15 with CI above zero;
- **requires additional plasticity** only if the generic motor extension exceeds the fixed primary by at least 0.20 with CI above zero;
- **non-diagnostic** if controlled banks fail their admitted-action oracle or reconstruction fails.

## Hard stop

Confirmation is executed exactly once at `results/exp004/frozen_v1`. Source, seeds, scenario names, thresholds, and config are hash-checked. No threshold or parameter may be changed after viewing it. A failed confirmation remains the result.
