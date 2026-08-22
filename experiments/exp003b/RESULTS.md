# EXP003b results

## Development checkpoint (not confirmatory)

Canonical development output is `results/exp003b/development_v2`; the invalid
evaluation-learning run remains in `development_v1`.

Across four development seeds, the primary model exceeded frozen/random behavior
and learned top-down alignment (`T` alignment 0.340 before remap and 0.410 after).
The old expectation was poorly aligned to the remapped role (0.069), and the new
one reorganized. The learned top-down pathway had a real local effect: it created
spikes on 0.96% of cell-frames and advanced comparable first-spike latency by
6.29 ms; lower weights changed by norm 0.263.

Nevertheless, the primary within-hypothesis longitudinal chain failed:
pre-remap `D→W=0.020`, `D→S=0.020`; post-remap `D→W=-0.056`, `D→S=0.025`.
All intervals crossed zero. Context opposition was 0.167, below the 0.25 floor.
The explicit vector-credit control passed behavior and all longitudinal endpoints,
showing that the task and analysis can detect the intended chain.

No change was made in response. The frozen held-out result will be appended below
after the single confirmation run.

## Held-out confirmation

The frozen protocol was committed and pushed as `f10868f` before any held-out
seed was instantiated. Seeds 3100–3111 were then run exactly once into the
append-only `results/exp003b/frozen_v1` directory. All 23 evidence files match
`SHA256SUMS.json`. No source, parameter, threshold or analysis rule changed after
inspection.

The preregistered classifier returned:

> **Outcome C — Grossbergian composition fails despite a validated SMART motif.**

### Criteria

| Criterion | Held-out result | Pass? |
|---|---:|:---:|
| Behavior above frozen/random before remap | paired advantages 0.238 `[0.121, 0.354]` / 0.242 `[0.117, 0.363]` | yes |
| Behavior above frozen/random after remap | 0.171 `[0.050, 0.296]` / 0.150 `[0.021, 0.283]` | yes |
| No initial hidden vector | motor mean `6.2e-18`; `T` mean `7.5e-5`; lower weight 0 | yes |
| Learned `T` emergence | alignment 0.402 before, 0.370 after | yes |
| `D_early→delta_W→delta_S` | all four primary endpoints near zero or negative | **no** |
| `T→SMART` specificity | all four paired longitudinal CIs include zero | **no** |
| Top-down changes SMART timing | 0.963% created-spike fraction; 6.293 ms latency advance | yes |
| Post-learning expression separation | post-remap success changed by 0.067 | **no** |
| Remap reorganization | new `T↔c=0.370`; old `T↔new c=0.012` | yes |
| Opposite-context top-down pattern | opposition 0.174 vs 0.25 floor | **no** |
| Generic Hebb full chain | did not reproduce it | no generic sufficiency |
| Vector positive control | success 1.0/1.0 and all four longitudinal CIs > 0 | yes |

### Behavior and representation learning

Primary frozen-evaluation success was 0.250 before remap and 0.179 after remap,
compared with frozen 0.013/0.008 and random 0.008/0.029. Absolute performance was
modest, but the paired advantages met the frozen behavioral criterion.

Scalar outcome and delayed structural credit learned a useful structured
expectation without hidden neuronal credit. Removing structural credit reduced
success to 0.017/0.000; removing real working memory to 0.042/0.004; and removing
motivated reinforcement to 0.021/0.013. The learned `T` alignment was not an
initialization artifact. A direct-copy bandit produced even stronger instantaneous
apical alignment (0.443/0.449), demonstrating again that instantaneous alignment
alone is not diagnostic.

After secret remapping, the old selected expectation was effectively unrelated to
the new causal vector (0.012); selected expectations reorganized to 0.370 and
behavior remained above controls. The two opposite contexts did not meet the
stronger context-specific criterion: their selected top-down patterns had only
0.174 opposition.

### Local SMART effect and longitudinal failure

The learned top-down pathway physically affected the locked SMART motif. It
created spikes in 0.963% of training cell-frames, advanced first-spike latency by
6.293 ms when both counterfactual traces spiked, and changed lower weights by norm
0.218. Thus the integration did not fail because `T` was disconnected.

It failed at the intended cellular-credit relationship:

| Fixed-hypothesis endpoint | Mean | 95% bootstrap CI |
|---|---:|---:|
| pre-remap `D_residual→delta_W` | 0.008 | `[-0.137, 0.148]` |
| pre-remap `D_residual→delta_S` | 0.008 | `[-0.137, 0.148]` |
| post-remap `D_residual→delta_W` | -0.052 | `[-0.282, 0.163]` |
| post-remap `D_residual→delta_S` | -0.044 | `[-0.277, 0.172]` |

Blocking learned `T` from the SMART motif set weight change and all longitudinal
endpoints to zero. But because the primary endpoints were themselves near zero,
the paired primary-minus-blocked effects were only 0.008/0.008 before remap and
-0.052/-0.044 after it; every interval included zero. The key ablation therefore
did not support the proposed explanation.

Suppressing apical expression only during learning-off evaluation did not erase
the learned motor path or weights: success remained 0.233 before and 0.113 after
remap. It did change post-remap expression relative to primary (0.179), exceeding
the 0.05 inert-expression floor. The paths are mechanically separate, but apical
modulation still contributes to current lower-cell output.

### Controls

The generic scalar-gated Hebbian comparator achieved success 0.171/0.129 but not
the longitudinal chain: pre `D→W=-0.274`, `D→S=-0.122`; post `D→W=0.067`,
`D→S=0.162`. The direct-copy baseline had zero weight and longitudinal change.

The explicit vector-credit control validated the assay with success 1.0/1.0;
pre-remap `D→W=1.000`, `D→S=0.554`; post-remap `D→W=0.591`, `D→S=0.571`, with
all confidence-interval lower bounds well above zero. The failure is therefore
specific to the tested scalar-selection/expectancy/SMART composition, not a
mathematical impossibility of the task or residual analysis.

Ordinary primary resonance was 0.9999, so disabling the resonance gate produced
the same computation and result. Reset/search did operate—12.5 categories were
recruited and 0.094 resets occurred per selection—but EXP003b does not establish a
causal role for the resonance gate in the ordinary regime.

Figures:

- [Behavior, longitudinal chain, and remap](FIGURES/behavior_longitudinal_expectancy.png)
- [Timing and causal local-plasticity contrast](FIGURES/timing_and_causal_ablation.png)
