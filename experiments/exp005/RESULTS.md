# EXP005 results

Status: **FROZEN HELD-OUT GENERIC DIAGNOSTIC COMPLETE**

## Two results that must remain separate

1. **Source-theory result: Outcome E.** The pre-implementation audit found no
   Grossberg-explicit or complete Grossberg-derived-composition rule for learning
   arbitrary neuron-resolved RSC topology from scalar consequence. No Grossberg
   primary experiment was manufactured or run.
2. **Generic computational result: class-D cellular credit works.** The separately
   labeled node-perturbation comparator learned and remapped the hidden topology
   from local exploratory eligibility plus scalar outcome.

The second result demonstrates what the missing operation can do. It does not turn
that operation into Grossberg's published mechanism.

## Frozen held-out run

Sixteen unseen balanced mappings (seeds 9500–9515) were run once under the locked
protocol. The adaptive projection began weak and independently randomized. After
1,280 acquisition episodes and a secret independent remap followed by 2,560
episodes, the generic comparator produced:

| N | Initial alignment | Acquisition alignment | Post-remap alignment | Acquisition BCI control | Post-remap BCI control | Changed-cell reversal |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | -0.062 `[-0.206, 0.084]` | 0.997 `[0.996, 0.998]` | 0.968 `[0.964, 0.972]` | 0.755 `[0.748, 0.762]` | 0.939 `[0.911, 0.961]` | 1.000 |
| 16 | 0.049 `[-0.083, 0.182]` | 0.993 `[0.991, 0.994]` | 0.960 `[0.954, 0.966]` | 0.729 `[0.715, 0.743]` | 0.910 `[0.879, 0.942]` | 1.000 |
| 32 | -0.014 `[-0.089, 0.060]` | 0.987 `[0.986, 0.988]` | 0.964 `[0.959, 0.969]` | 0.746 `[0.730, 0.763]` | 0.951 `[0.930, 0.971]` | 1.000 |
| 64 | 0.021 `[-0.024, 0.069]` | 0.972 `[0.969, 0.975]` | 0.950 `[0.941, 0.957]` | 0.742 `[0.732, 0.752]` | 0.947 `[0.926, 0.966]` | 0.975 `[0.960, 0.989]` |

All means show bootstrap 95% intervals where displayed. Stable evaluation success
was 1.0 at every N in both phases. At N=64, 98.8% of all cells and 97.5% of cells
whose role changed had the correct final sign.

## N=32 anchor controls

| Condition | Acquisition alignment | Post-remap alignment | Post-remap BCI control | Interpretation |
|---|---:|---:|---:|---|
| Generic node perturbation | 0.987 | 0.964 | 0.951 | Learns and reverses |
| Outcome shuffled within blocks | 0.241 | 0.229 | 0.054 | Same reward distribution, wrong eligibility pairing |
| Plasticity disabled | -0.014 | -0.016 | -0.000 | Initial geometry does not solve task |
| Temporal eligibility disabled | -0.014 | -0.016 | -0.000 | Delayed scalar outcome has no local trace |
| Exploration removed | -0.014 | -0.016 | -0.000 | Scalar outcome alone cannot distinguish cells |
| Zero-topology random/no learning | 0.000 | 0.000 | 0.000 | Pure exploration does not create stable topology |
| Hidden-vector oracle | 1.000 | 1.000 | 1.000 | Task sensitivity ceiling |

The primary post-remap generic-minus-shuffled alignment effect was 0.735, 95% CI
`[0.655, 0.820]`. Generic-minus-no-exploration and generic-minus-no-eligibility
effects were both 0.981 with intervals excluding zero. All frozen support floors
were passed.

## Where neuron-specific information entered

The learner's only neuron-varying credit variable was the local perturbation
eligibility. Across cells, the correlation between eligibility and later true
outcome aligned with hidden causal role during acquisition by 0.982, 0.916, 0.764,
and 0.499 at N=8,16,32,64, respectively. The decline quantifies the worsening
single-cell signal-to-noise of a population-mean decoder. The transparent
`eta_N = eta N/32` normalization compensated for known `1/N` reward scaling; it did
not provide role information.

The simple eligibility-to-update correlation is low because update sign also
depends on the scalar advantage. The complete legal local predictor
`eta_N (R-b)e_i` predicted recorded deltas with correlations 0.937–0.980. Exact
replay including centering and bounds reconstructed every generic update with RMSE
below reported numerical precision; cumulative delta histories reconstructed final
weights exactly.

Outcome shuffling preserved the scalar outcomes but broke their pairing with local
eligibility and abolished the large effect. Exploration removal and eligibility
removal yielded exactly zero plastic change. Thus the causal information came from
the conjunction of local variation and scalar consequence, not from initialization,
indices, or an unobserved target vector.

## Construction versus lucky sample selection

During initial acquisition, final stable topology exceeded the best single
exploratory sample at every N. The mean margins were 0.002, 0.021, 0.034, and 0.048
for N=8,16,32,64, with all 95% intervals above zero. This is evidence accumulation,
not selection of one lucky fixed response.

After remap, final topology also exceeded every sample at N=32 and N=64 by 0.008
and 0.020. At N=8 and N=16 it did not: the much larger finite sample set contained
rare transient samples slightly more aligned than the stable result (margins -0.025
and -0.015). The remapped topology nevertheless reconstructed from thousands of
legal local updates and reached correct signs for every cell at those sizes. The
strict “better than every sample” criterion is therefore supported for acquisition
at all N and for remap only at N>=32.

## Remapping and sample efficiency

Using a 64-episode smoothed 0.70 alignment criterion for descriptive timing,
acquisition crossed threshold after mean 95, 95, 113, and 133 episodes for
N=8,16,32,64. Remapping took mean 1,194, 1,313, 1,277, and 1,338 episodes because
the established old topology first had to be reversed. This asymmetry was exposed
during development and the longer remap window was frozen before confirmation.

## Classification

- Source classification: **E — no Grossberg candidate exists**.
- Generic diagnostic: **works under the frozen class-D assumptions**.
- Combined interpretation: **C/E — scalar reward is sufficient in principle when
  paired with a new local perturbation eligibility, but the audited Grossberg theory
  does not currently provide that bridge.**

The raw archive, summary, bootstrap statistics, figures, and checksums are under
`results/exp005/frozen_generic_v1/`. All 21 manifest entries were independently
rehash-verified after the run.
