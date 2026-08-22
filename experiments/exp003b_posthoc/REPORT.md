# EXP003b post-hoc failure-localization report

> **POST HOC / FAILURE LOCALIZATION — NOT CONFIRMATORY EVIDENCE**

## Diagnostic classification

**A — learned `T` contains appropriate cell-specific information and predicts
local plasticity, but the current modeled Francioni readout loses it.**

Frozen EXP003b remains **Outcome C**. This diagnostic does not rescue or
reinterpret the confirmatory result.

The first demonstrable information loss is the current soma-conditioned
dendritic-residual construction. Signed information is not destroyed by clipping
alone: the excitatory center remains informative and the inhibitory surround
carries additional signed information. Both predict local weight change. Local
weight change predicts the held-fixed-hypothesis future soma. In contrast, the
current residual does not predict either endpoint.

## Arrow-by-arrow localization

Correlations are computed within a fixed hypothesis across eight neurons, averaged
over two contexts and pre/post-remap windows within each of 12 seeds. Intervals are
5,000-resample seed-level bootstrap 95% CIs.

| Arrow | Mean correlation | 95% CI | Interpretation |
|---|---:|---:|---|
| raw `T` → clipped `T` | 0.903 | [0.892, 0.913] | Positive-center clipping reduces sign detail but preserves rank strongly |
| clipped `T` → `g_td` | 0.963 | [0.921, 0.988] | Excitatory-center conductance faithfully expresses the clipped profile |
| raw `T` → `-g_inh` | 0.608 | [0.490, 0.727] | The off-surround carries substantial signed information omitted from modeled apical `D` |
| `g_td` → net top-down envelope | 0.973 | [0.931, 0.995] | Excitatory contribution dominates but does not erase surround information |
| `-g_inh` → net top-down envelope | 0.676 | [0.553, 0.800] | Inhibitory surround contributes materially to the net local transform |
| net envelope → mean modeled apical component | 0.954 | [0.913, 0.978] | The explicit excitatory/apical proxy still tracks the local top-down state |
| mean apical → error-improvement apical contrast | 0.418 | [0.141, 0.648] | Error conditioning retains a meaningful part of the patterned signal |
| apical contrast → soma-conditioned `D_residual` | 0.337 | [0.191, 0.479] | Residualization retains only part of that signal |
| net envelope → `D_residual` | 0.113 | [-0.020, 0.240] | **First non-estimable arrow** |
| latency advance → `delta_W` | 0.104 | [0.042, 0.167] | Positive but weak because comparable spikes are rare |
| created-spike frequency → `delta_W` | 0.125 | [0.062, 0.188] | Positive but sparse binary engagement |
| `delta_W` → held-hypothesis `delta_S` | 0.396 | [0.208, 0.583] | Local weight changes do alter future lower-cell response |
| `D_residual` → `delta_W` | -0.004 | [-0.141, 0.128] | Current Francioni proxy loses plasticity-predictive information |
| `D_residual` → `delta_S` | -0.037 | [-0.152, 0.075] | Current proxy also fails at the future-response endpoint |

The more direct variables predict the cellular endpoint:

| Early variable → `delta_W` | Mean | 95% CI |
|---|---:|---:|
| signed raw `T` | 0.416 | [0.290, 0.530] |
| clipped top-down profile | 0.493 | [0.357, 0.617] |
| recorded `g_td` | 0.492 | [0.350, 0.617] |
| recorded `-g_inh` | 0.405 | [0.270, 0.529] |
| equation-derived net envelope | 0.500 | [0.360, 0.630] |
| mean modeled apical component | 0.493 | [0.357, 0.617] |
| apical error-improvement contrast before soma regression | 0.391 | [0.223, 0.550] |

The last row is especially diagnostic: error conditioning itself does not erase
the effect. The loss appears when the current soma/network regression removes
variance that, in this model, is both soma-correlated and causally relevant.

## Hidden-role information at each representation

| Representation | Alignment with hidden role | 95% CI |
|---|---:|---:|
| signed raw `T` | 0.348 | [0.271, 0.430] |
| clipped `T` | 0.319 | [0.231, 0.405] |
| `g_td` | 0.320 | [0.239, 0.398] |
| `-g_inh` | 0.231 | [0.162, 0.296] |
| net local top-down envelope | 0.307 | [0.225, 0.386] |
| mean modeled apical component | 0.319 | [0.231, 0.405] |
| apical error-improvement contrast | 0.370 | [0.289, 0.444] |
| soma-conditioned `D_residual` | 0.075 | [0.003, 0.154] |

Thus the Grossberg-style on-center/off-surround transform does contain signed
role information that the current residual largely discards. The omission of
inhibitory surround from modeled `D` is real, but it is not the only issue: even
the recorded excitatory apical contrast predicts `delta_W` before soma regression.

## Sparsity and quantization

- Top-down changed spike count in 1.744% of training cell-frames
  (CI [1.220%, 2.243%]).
- It created a spike in 0.963% ([0.724%, 1.181%]).
- Latency changed in 0.961% of all cell-frames; only 1.009% had finite latency in
  both actual and no-top-down traces. Conditional on comparability, 79.2% changed.
- A frame-level weight update was nonzero in 1.971% of cell-frames.
- Across fixed-hypothesis early-to-late endpoints, 92.97% of neuron weights were
  exactly unchanged in archived float32 data; the median unit had one of eight
  neurons change (IQR 0–1).
- Frame `delta_W` had median and 75th percentile zero; 99th percentile 0.00402,
  maximum 0.00818 and minimum -0.000775.

The full-population correlations therefore mainly identify **which cell crosses
the SMART plasticity gate**, not a smooth relationship among many changing cells.
Among the post-hoc engaged subset, only 2.25 of 32 pooled fixed-h neuron endpoints
per seed were available on average, and raw-`T`/`delta_W` magnitude correlation was
not estimable (`r=-0.025`, CI [-0.291, 0.256]). This subset is diagnostic only and
is not used to claim success.

Sparsity weakens the strength of classification A but does not force E: the
cell-selection correlations, net-transform correlation and `delta_W→delta_S`
effect are all estimable across seeds with intervals above zero. It does mean a
future experiment must preregister a dose-response regime with denser, non-saturated
SMART engagement before testing graded cellular magnitudes.

## Net membrane-influence definition

No subtraction coefficient was fitted. Per frozen cell-frame the diagnostic uses
the actual lower-cell membrane equation:

\[
\frac{g_{td}^{peak}(E_E-V^{peak}) + g_I^{peak}(E_I-V^{peak})}{\tau_m},
\]

with `E_E=0 mV`, `E_I=-80 mV`, and `tau_m=10 ms` from the locked motif.

The raw archive stores separate maxima, not time-aligned trajectories. This is
therefore an equation-derived **peak-current envelope**, not an exact instantaneous
or integrated current. Computing the exact integral would require a new simulation
and is intentionally not done here.

## Recommendation for the next experiment

Do not add cellular credit yet. First preregister a measurement-focused experiment
that records full time-aligned apical voltage, `g_td`, `g_inh`, membrane-current
terms and float64 lower weights. Its dendritic observation model should explicitly
represent excitatory center and inhibitory surround and compare, before looking at
outcomes:

1. raw apical current;
2. signed net apical/surround membrane influence;
3. soma-conditioned residuals with regression choices fixed in advance; and
4. a calibrated SMART dose-response that engages more than one neuron per typical
   fixed-hypothesis unit without changing the validated local learning rule.

This is a measurement/readout hypothesis, not a new credit-assignment mechanism.

Figures: [failure localization](results_v3/figures/failure_localization.png) and
[engagement sparsity](results_v3/figures/engagement_sparsity.png).
