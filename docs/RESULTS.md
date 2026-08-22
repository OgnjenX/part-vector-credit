# Results log

This file is updated from the committed confirmatory run. Machine-readable seed
data and the figure are generated locally by `part-credit` and intentionally not
tracked, so results can be regenerated rather than treated as opaque artifacts.

## Run 0: failed calibration (retained as a failure)

On 2026-08-22, Python 3 with NumPy 2.3.4, the initial 30-seed run used vigilance
0.72. The full model obtained 0.080 late accuracy, 0.027 resonance rate, and 0.973
reset rate. Its opposition index was -0.210, despite opposite signs in every seed.
The no-reset ablation obtained 0.947 accuracy and +1.232 opposition. This exposed
an implementation pathology: the toy task's noisy inputs almost never passed the
hand-set vigilance threshold, so reset nearly always rejected the best hypothesis
and forced the remaining, usually wrong one. This run falsified H1 for that
parameterization; it was not discarded as scientific evidence.

Before another confirmatory run, vigilance was changed to 0.50. No other parameter,
metric, seed, threshold, or condition was changed. This is a calibration revision,
not an independent preregistered confirmation; any success must be labeled
post-failure and checked with a full vigilance sweep.

## Run 1: vigilance calibration also failed

With vigilance 0.50, the full model reached 0.286 accuracy, +0.111 opposition,
0.967 opposite-sign seeds, 0.161 resonance, and 0.840 reset. The no-reset ablation
again performed much better (0.864 accuracy). Inspection identified the real error:
the model used a fuzzy-intersection update on raw, non-complement-coded noisy inputs.
Prototypes monotonically contracted, lowering later match and causing pathological
reset. Merely lowering vigilance did not repair that representational mistake.

## Run 2: corrected complement-coded abstraction

The match was replaced by normalized L1 similarity of complement-coded inputs, and
resonant prototypes now track the raw half of that code. Vigilance returned to the
original 0.72. Conditions, metrics, seeds, and all other parameters remained fixed.
The corrected run met the primary criteria: full-model late accuracy was 0.978,
P+ modulation +0.673, P- modulation -0.673, opposition index +1.346, and all 30
seeds had opposite signs. Removing motivated-attention gain reduced opposition to
+0.343. Removing working memory nearly eliminated it (+0.019), while accuracy
remained 0.977 because this one-step task does not require delayed action selection.
Shuffled feedback eliminated the population-locked effect (-0.001).

However, ordinary trials had 1.000 resonance and zero resets; consequently the
no-reset condition was identical to full. The corrected primary run therefore does
not test reset causally. A high-vigilance mismatch stress condition was added after
seeing this diagnostic. It is reported separately and is not counted toward H1.
At vigilance 0.90, the stress condition produced 0.142 accuracy, 0.124 resonance,
0.876 reset, and -0.128 opposition. Thus this two-category reset implementation
fails under frequent mismatch; it does not validate SMART-like search dynamics.

## Interpretation

Run 2 supports a narrow existence claim: selected, motivated top-down feedback can
route an oppositely signed population pattern without a neuron-indexed error. It
does **not** show that scalar reward learned the sign structure. Contrasting P+/P-
templates were an architectural prior, and the model's “apical” variable directly
reads their on-center/off-surround feedback. The result is therefore compatible
with Grossberg-style selection being computationally sufficient for routing while
leaving the cellular origin of the vector basis unresolved.

The committed `results/initial_experiment.json` contains every seed-level metric;
`results/initial_experiment.png` is the corresponding condition comparison. Tests
passed (3/3). Ruff was declared as a development dependency but was not installed
in the host environment used for this run, so lint validation remains pending.
