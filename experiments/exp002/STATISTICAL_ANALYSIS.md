# Frozen statistical analysis

All intervals below are the preregistered seed bootstrap over 30 held-out paired seeds. No
multiple-comparison-adjusted discovery claims are made; the comparisons were mechanistic decision
criteria, not an exploratory screening analysis.

| Metric | Primary | 95% CI where frozen | Key comparator |
|---|---:|---:|---|
| Pre-remap evaluation success | 0.528 | — | frozen 0.191; paired difference 0.338 [0.256, 0.419] |
| Post-remap evaluation success | 0.397 | — | frozen 0.178; paired difference 0.218 [0.132, 0.308] |
| Pre selected `T` alignment | 0.343 | — | direct copy 0.345; paired difference -0.002 [-0.009, 0.006] |
| Post selected `T` alignment | 0.287 | — | direct copy 0.288; paired difference -0.001 [-0.009, 0.008] |
| Pre longitudinal residual | -0.326 | [-0.423, -0.224] | vector error 0.660 [0.636, 0.682] |
| Post longitudinal residual | -0.016 | [-0.120, 0.091] | vector error 0.545 [0.501, 0.589] |

The primary-minus-random behavioral differences were 0.328 [0.243, 0.416] before and 0.234
[0.145, 0.329] after remapping. The primary and contextual bandit had exact zero paired behavioral
differences because the selected policies and scalar updates were computationally equivalent in
this task.

Top-down learning was measurable: primary-minus-learning-suppressed alignment was 0.337
[0.246, 0.424] before and 0.321 [0.206, 0.429] after remapping. The corresponding behavioral
differences were exactly zero. Thus learned `T` was statistically structured but causally
epiphenomenal for behavior.

Initial leakage criteria passed. Mean signed correlations were 0.003 (motor) and 0.020 (top-down).
Observed nearest-centroid decoding was 0.433 and 0.427; permutation-null means were 0.392 and
0.392, differences 0.041 and 0.035 versus the allowed 0.15. Mean seed permutation p-values were
0.509 and 0.520.

The negative primary residual was not a lack-of-power artifact: before remapping its confidence
interval excluded zero in the wrong direction, while the same pipeline recovered a large positive
effect in the explicit-vector control. Post-remap primary uncertainty included zero but excluded
the preregistered +0.15 target by its upper bound.
