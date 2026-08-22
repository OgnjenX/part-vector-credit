# EXP001 results

## Run sequence

The two-seed smoke run and its measurement correction are recorded in
`FAILURES.md`. The initial development configuration (reinforcement rate 0.12)
failed behavior. A prespecified one-factor development sweep selected rate 0.30;
all other defaults and all criteria remained fixed. The frozen development run is
under `results/exp001/frozen_v1/exp001_development.*`. Held-out seeds 1000–1029 were
then executed once and are under `exp001_confirmatory.*`.

## Held-out primary result

| Condition | Early success | Late pre-remap | Late post-remap | Dendritic role alignment | Residual predicts later soma |
|---|---:|---:|---:|---:|---:|
| frozen zero plasticity | 0.064 | 0.055 | 0.060 | 0.375 | −0.123 |
| random policy/feedback | 0.055 | 0.046 | 0.045 | 0.511 | −0.253 |
| pART-inspired full | 0.370 | 0.728 | 0.716 | 0.497 | 0.124 |
| no structural credit | 0.021 | 0.020 | 0.021 | 0.055 | −0.114 |
| no working memory | 0.028 | 0.027 | 0.029 | −0.012 | −0.105 |
| no motivated attention | 0.000 | 0.000 | 0.002 | 0.271 | 0.148 |
| no Now Print gate | 0.064 | 0.055 | 0.060 | 0.375 | −0.123 |
| shuffled top-down feedback | 0.066 | 0.073 | 0.076 | 0.374 | −0.100 |
| apical pathway suppressed | 0.000 | 0.000 | 0.000 | 0.043 | −0.063 |
| explicit vector-error positive control | 0.715 | 1.000 | 1.000 | 0.999 | 0.461 |

Full-model learning and remapping criteria passed. Removing structural credit,
working memory, motivated attention, reinforcement gating, or the apical path
abolished behavior. Passive sensory observation was unchanged by apical suppression.
In the one-context primary task, resonance was 100% and reset never occurred; no
reset and no resonance-gate conditions were therefore identical to full.

Seed-bootstrap 95% intervals were [0.647, 0.792] for pre-remap late success and
[0.628, 0.789] post-remap. Thus the prespecified mean thresholds passed, but their
uncertainty intervals include values below 0.70. Paired post-remap advantages over
frozen and random policy were 0.656 [0.573, 0.722] and 0.671 [0.578, 0.748]. Full
statistics are committed in `exp001_confirmatory_statistics.json`.

## Leakage and basis selection

The mean signed initialization correlation was −0.0109 (criterion: absolute value
< 0.05). Group label-decoding permutation p was 0.144; one of 30 individual seeds
was significant, consistent with chance. Every candidate correlation is stored in
the seed records. No visible index or initialization label encoded hidden roles.

The bank nevertheless contained chance-aligned distributed directions. Capacity
increased mean best absolute initial alignment from 0.360 (2 patterns) to 0.852
(512). Behavioral success was non-monotonic because larger banks were harder to
search in fixed trials, but within the 32-pattern full condition, alignment of the
selected post-remap pattern predicted success (`r = 0.679`). Full, frozen-basis,
and the nominal plastic-basis probe were numerically identical: the allowed
outstar-like probe had no causal information with which to rotate a pattern.

The behavioral mechanism is therefore **selection from a pre-existing random
basis**, not de novo representational learning.

## Dendritic analysis and causal perturbation

Full-model soma-conditioned residuals had an instantaneous hidden-role correlation
of 0.497 and opposite population means in 28/30 seeds. This is not sufficient.
Frozen, random-policy, and shuffled-feedback controls also showed instantaneous
alignment (0.375, 0.511, and 0.374) without learning. Closed-loop covariance can
create this statistic because a random action determines error change and the same
pattern appears in the engineered dendritic proxy.

The preregistered longitudinal discriminator failed: early post-remap residuals
predicted later somatic change at only `r = 0.124`, below 0.20, versus 0.461 in the
explicit-vector positive control. Apical suppression abolished both behavior and
the residual signature, but this does not rescue specificity because the apical
path is also the model's motor-output route.

The bootstrap interval for the full longitudinal statistic was [−0.053, 0.301]; it
crossed both zero and the preregistered threshold. The conclusion rests on failure
of the fixed mean criterion plus the non-specific instantaneous control results,
not on evidence that the true association is exactly zero.

This abstraction therefore does **not** reproduce the full Francioni phenomenon.

## ART search, robustness, and generalization

The base task did not require search. A separate two-context probe forced mismatch:
search recruited two categories and achieved 0.603 post-remap success; disabling
search retained one category and achieved 0.307. This held at vigilance 0.60, 0.80,
and 0.95. Reset occurred only at category recruitment (~0.1% of trials), rather
than being a continuous explanation of the primary result.

Development generalization was uneven: late post-remap success was 0.799 for six
neurons, 0.315 for twenty, 0.795 for an unequal 3/7 split, 0.284 under weak causal
strength, 0.772 with transition noise, 0.762 after partial remap, 0.547 with 15%
reward flips, 0.739 with a long delay, 0.629 for the changed target, and 0.603 for
opposing contexts. The mechanism is not robustly sufficient across task variants.

A heterogeneous-causal-weight probe was added only after confirmation and is
explicitly post hoc; it is not part of the confirmatory claim. On development
seeds, post-remap success was 0.796 but the longitudinal dendritic statistic again
failed (0.100). Re-executing confirmatory seed 1000 under default weights reproduced
every scalar metric exactly (`max_abs_diff = 0`).

## Outcome

**Outcome 3 — Behavioral learning without validated dendritic vectorization**, with
an **Outcome-2 random-basis selection mechanism** explaining the behavior.

The experiment supports Grossberg-style structural and temporal credit at the
level of choosing a distributed causal representation. It finds no published or
implemented Grossberg-only rule that learns arbitrary neuron signs from scalar BCI
outcome. A cellular/parametric credit mechanism remains unspecified. Because the
dendritic proxy and bandit association are engineered abstractions, the broader
theory is not falsified; a more faithful model would need explicit pART/MOTIVATOR/
SMART equations and a justified interface to VAM-like motor mismatch learning.
