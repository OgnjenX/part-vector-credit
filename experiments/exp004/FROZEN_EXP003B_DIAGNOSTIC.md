# POST-HOC EXP003b repertoire diagnostic

> **POST HOC / DIAGNOSTIC ONLY. Frozen EXP003b remains Outcome C.**

This analysis reads only the committed `primary_part_t_smart` held-out arrays. It does not rerun the BCI. Initial B, initial T, and the zero-top-down initial soma probe are deterministically reconstructed from the frozen seeds and locked response cache. Values and T are replayed from archived category, hypothesis, resonance, soma, outcome, and working-memory arrays.

The replay predicts the archived motivated-gain-scaled evaluation top-down vector with mean RMSE \(1.9\times10^{-8}\), validating the reconstruction.

## Coverage and outcome relationships

Correlations use the 12 held-out mapping seeds separately before and after remapping. Intervals are 5,000-resample seed bootstrap 95% CIs and are descriptive.

| Predictor → endpoint | Pre-remap r [95% CI] | Post-remap r [95% CI] |
|---|---:|---:|
| Best initial motor alignment \(A_B\) → evaluation success | 0.572 [0.080, 0.867] | -0.205 [-0.736, 0.396] |
| Best initial soma alignment \(A_S\) → evaluation success | 0.681 [0.296, 0.894] | -0.235 [-0.788, 0.391] |
| Best initial soma alignment \(A_S\) → final emitted-T alignment | 0.358 [0.003, 0.681] | 0.200 [-0.284, 0.707] |
| Best initial soma causal score \(Q_S\) → evaluation success | 0.286 [-0.325, 0.688] | -0.314 [-0.786, 0.392] |
| Selected-h initial soma alignment → final emitted-T alignment | **0.958 [0.856, 0.989]** | **0.866 [0.731, 0.958]** |
| Selected-h initial causal score → evaluation success | 0.232 [-0.414, 0.711] | 0.511 [0.125, 0.814] |

Initial coverage helped explain acquisition success before remap, but its relationship with post-remap behavior was unstable and reversed in this small sample. The robust result is narrower: whichever hypothesis became selected, its initial population geometry almost completely predicted the sign structure of its final T.

## What T stored

| Quantity | Pre-remap mean | Post-remap mean |
|---|---:|---:|
| Best initial soma alignment \(A_S\) | 0.614 | 0.700 |
| Final emitted-T role alignment | 0.298 | 0.415 |
| Selected-h initial soma role alignment | 0.311 | 0.405 |
| corr(T, selected-h initial soma) | **0.952** | **0.872** |
| corr(T, simple mean of actual selected-pair targets) | **0.996** | **0.993** |
| T alignment minus best individual sampled-target alignment | -0.058 | -0.065 |
| Dominant evaluation-pair occupancy | 0.467 | 0.467 |

Final T was not an unexplained vector and did not improve on the best sampled target. It was an extremely accurate outstar compression/average of the soma patterns experienced under the selected category–hypothesis pair, and those patterns remained close to the selected fixed motor response.

## Antithetic handling

Coverage is computed in the behaviorally useful signed direction. Each frozen bank consists of eight random directions and their negatives. The diagnostic records both pair identity and orientation; context reversal is evaluated against the reversed causal role. Therefore a useful negative partner is not incorrectly scored as bad coverage.

## Information-source interpretation

The frozen result supports both of these statements:

1. **Genuine scalar-outcome learning occurred.** Outcome changed V, future hypothesis occupancy, and which targets were repeatedly associated with each T.
2. **The neuron-wise coordinates stored by T were supplied primarily by the selected fixed repertoire response.** T copied/averaged that response rather than constructing a more role-aligned vector across hypotheses.

This is not evidence that ART is a lookup table. Categories and values changed and controlled which memory slot and action were active. It is evidence that frozen `T[k,h]`, because it is indexed by h and updated only from soma produced while h is active, inherited most of its cellular topology from that h.

## Limitations

- Only 12 held-out seeds exist; coverage→behavior intervals are wide.
- The frozen archive did not save B, initial probes, values, or T directly. Deterministic reconstruction is independently cross-checked against archived emitted T, but it is still reconstruction.
- SMART lower weights changed during EXP003b, especially after remap. The initial probe deliberately asks what coverage existed before that plasticity; later targets can also reflect lower-weight changes.
- This diagnostic cannot distinguish fixed-repertoire selection from ART/outstar construction under controlled coverage because EXP003b did not manipulate bank size or coverage.

## Diagnostic conclusion

EXP003b's learned T was highly predictable from the initially selected repertoire direction and the actual within-pair soma-target mean. Lucky initial coverage contributed materially before remap, but the frozen sample is too small and post-remap behavior too variable to quantify a general repertoire bottleneck. EXP004 must manipulate bank size and coverage prospectively.

Machine-readable results: `results/exp004/frozen_exp003b_diagnostic/diagnostic.json`. Exact reconstruction arrays: `results/exp004/frozen_exp003b_diagnostic/reconstruction_arrays.npz`.
