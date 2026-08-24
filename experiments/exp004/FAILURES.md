# EXP004 failure log

All entries precede protocol freeze and use development seeds only.

## Development smoke v1 — global T metric was incomplete for composition

The first three-scenario smoke run completed. Standard controlled-low behavior varied across seeds; the phase-composition condition approached its allowed-sequence oracle and exceeded the best repeated-single oracle. However, its global `corr(T,c)` was near zero because each category/action was useful only on a prespecified phase mask. Treating this as failed representation learning would conflate global with category-conditional expressivity.

Repair made before confirmation: retain global T-role alignment, and add a prespecified effective alignment computed against the same phase-specific causal mask used by the environment/oracle. The raw full vector remains archived. No parameter or success threshold changed.

Output preserved at `results/exp004/development_smoke_v1/`.

## Development v1 attempt — high-coverage rejection sampler failed

The first full development attempt completed 46 of 58 in-memory scenarios, then stopped before writing any output. The controlled-high bank requested exact absolute correlation 0.875 using naive rejection sampling of balanced 32-cell sign vectors. Such near-perfect balanced vectors are too rare for the fixed 200,000-draw bound.

This was a bank-generator failure, not a learning result. The output path was never created and no held-out seed was used.

Repair: construct the preregistered exact-coverage anchor analytically by starting from the hidden role and flipping equal numbers of P+ and P− coordinates. This preserves balance, row mean, norm, variance, amplitude, and antithetic structure. Remaining non-anchor directions are still randomly sampled under the same maximum-coverage bound. Tests verify exact LOW/MEDIUM/HIGH coverage and matched row norms.

## Generic motor-plasticity control rate calibration

The generic scalar reward-gated perturbation control changed its motor bank by norm 0.026 and was behaviorally indistinguishable from the fixed-repertoire primary at learning rate 0.08. A development-only sweep was run to prevent a trivially inert control.

| learning rate | evaluation success | normalized behavior | motor-bank change norm |
|---:|---:|---:|---:|
| 0.08 | 0.250 | 0.793 | 0.026 |
| 0.40 | 0.256 | 0.800 | 0.132 |
| 1.00 | 0.347 | 0.824 | 0.328 |
| 2.00 | 0.378 | 0.824 | 0.645 |
| 3.00 | 0.378 | 0.801 | 0.980 |
| **4.00** | **0.475** | 0.814 | 1.292 |
| 8.00 | 0.125 | 0.763 | 2.260 |

Rate 4.0 was frozen for the secondary generic control because it maximized development success before degradation at 8.0. The per-update displacement remains scaled by the small executed perturbation, eligibility, and scalar advantage. This rate does not affect the fixed-repertoire primary or any ART/outstar rule.

## Held-out confirmation

The single `frozen_v1` run completed all 58 scenarios without a runtime or integrity failure. Scientifically, full ART failed to beat the contextual bandit, category proliferation was inferior to the no-recruitment condition, R2/R3 construction criteria failed, and the generic motor-plasticity extension missed its frozen 0.20 effect floor. These negative results were retained without repair or rerun.
