# EXP004 frozen results — origin of neuron-specific topology

The preregistered `frozen_v1` suite was executed exactly once on 16 held-out seeds (7000–7015) after the protocol was pushed at commit `a1d8aee`. All 58 scenarios completed. No parameter, threshold, model rule, bank generator, seed, or analysis window changed after inspection.

Raw seed-level arrays, summary statistics, figures, and file hashes are preserved under `results/exp004/frozen_v1/`. Intervals below are preregistered 5,000-resample seed-bootstrap 95% intervals.

The raw NPZ archives use Git LFS solely for reliable publication. This does not alter their bytes: all 63 output files were independently checked against `SHA256SUMS.json` before commit.

## Frozen classification

| Axis | Result | Meaning |
|---|---|---|
| Behavioral | **B1 + B2 + B3** | Single-pattern selection explains ordinary controlled banks; valid action sequences solve the special composition task; large random banks still expose a search/architecture limitation. |
| Representational | **R1** | T is copy/compression of a selected experienced response, not R2 construction or R3 category factorization. |
| A2 | **weak-form supported and repertoire-limited** | Scalar outcome genuinely selects neuron-resolved representations over a fixed repertoire, but useful topology remains strongly dependent on repertoire coverage. |
| Additional plasticity | **not established** | The generic scalar motor-plasticity probe improved behavior but missed its frozen effect floor; the hidden-vector control succeeded. |

These flags are intentionally not mutually exclusive across task regimes.

## Controlled initial coverage

At fixed M=16, the banks had matched amplitudes, row norms, balance, pair structure, and hypothesis count. Only experimenter-controlled alignment with hidden c differed; the learner never saw the coverage label or score.

| Coverage | A_single | Q_single | Primary normalized behavior | Success | T-role alignment |
|---|---:|---:|---:|---:|---:|
| LOW | 0.375 | 0.1125 | 0.765 | 0.220 | 0.258 |
| MEDIUM | 0.625 | 0.1875 | 0.882 | 0.566 | 0.327 |
| HIGH | 0.875 | 0.2625 | 0.962 | 0.813 | 0.395 |

Across these held-out controlled banks, A_single correlated 0.581 with final behavior and 0.657 with final T alignment. HIGH minus LOW behavior was **0.197 [0.137, 0.255]**, passing the frozen repertoire-limitation floor.

## Random-bank size and the search confound

Nested random banks improved coverage monotonically, but practical performance did not improve monotonically because structural-credit search became harder.

| M | A_single | Fixed-budget behavior | Search-normalized behavior | Allowed oracle |
|---:|---:|---:|---:|---:|
| 2 | 0.117 | 0.351 | 0.315 | 0.344 |
| 4 | 0.211 | 0.564 | 0.405 | 0.563 |
| 8 | 0.289 | 0.703 | 0.547 | 0.758 |
| 16 | 0.320 | 0.676 | 0.597 | 0.836 |
| 32 | 0.367 | 0.645 | 0.645 | 0.938 |
| 64 | 0.430 | 0.598 | 0.641 | 1.000 |
| 128 | 0.437 | 0.563 | 0.725 | 1.000 |

For the primary model, the cluster-bootstrap indirect M→coverage→behavior coefficient was 0.097 [0.071, 0.125] at fixed experience and 0.074 [0.053, 0.098] under search-normalized experience. The total M effects were much smaller (0.023 and 0.064), showing that better candidates and harder search opposed each other. At M=64/128 the oracle was perfect while the learner remained far below it, producing B3.

## Valid low-single-coverage composition

The special bank was admitted only when no repeated single hypothesis was a strong solution but a three-frame sequence available to the learner was oracle-solvable.

| Quantity | Mean [95% CI] |
|---|---:|
| A_single | 0.242 [0.227, 0.250] |
| Best repeated-single behavior | 0.667 [0.615, 0.708] |
| Primary behavior | 0.980 [0.956, 0.993] |
| Primary − repeated single | **0.313 [0.260, 0.374]** |
| Allowed-sequence oracle | 1.000 |
| Oracle − primary | **0.020 [0.007, 0.043]** |

This is genuine behavioral composition of existing motor patterns (B2), not creation of a new motor vector. The contextual bandit achieved 0.977 behavior, essentially the same as primary ART (0.980); therefore the composition result is not ART-specific.

## ART category contribution

At controlled medium coverage, full ART recruited 9.94 categories, modified prototypes 328 times, and accumulated prototype change norm 2.43. Those are real category-learning events. They did not provide a held-out advantage over the contextual bandit:

| Primary minus comparison | Behavior effect [95% CI] | T-alignment effect [95% CI] |
|---|---:|---:|
| Contextual bandit | 0.001 [-0.080, 0.064] | 0.015 [-0.028, 0.055] |
| Fixed categories | 0.046 [-0.050, 0.125] | 0.017 [-0.028, 0.057] |
| No category modification | -0.007 [-0.064, 0.048] | 0.003 [-0.033, 0.042] |
| No new category recruitment | **-0.118 [-0.191, -0.057]** | **-0.274 [-0.310, -0.239]** |

The two broad, plastic context categories in the no-recruitment condition reached perfect behavior and T alignment 0.601. In this abstraction, proliferation fragmented structural-credit evidence; it did not reduce dependence on repertoire coverage. Same-h category T distance was only 0.0074 [0.0045, 0.0101], far below the 0.10 R3 floor.

## What T actually learned

For the medium primary condition:

| Reachability quantity | Held-out mean |
|---|---:|
| corr(T, selected-h initial soma) | **0.999851** |
| corr(T, simple mean of its actual targets) | **0.999870** |
| T alignment − best initial pattern | -0.298 |
| T alignment − best individual target | -0.0325 |
| Exact update-history reconstruction RMSE | **0.0** |

Thus T acquired new numerical values by local outstar averaging, but it did not denoise/generalize into a more role-aligned vector than any constituent pattern. Every final T was exactly generated by the archived scalar-rate update sequence and targets. R1 is supported; R2, R3, and R4 are not.

The composition task's global T alignment was 0.046 because different cell subsets mattered at different frames; its prespecified phase-masked effective alignment was 0.437. Even there, T remained a near-copy of the selected response (corr 0.99984), so behavioral composition did not become cross-h representational synthesis.

## Where hidden-role information entered

Scalar outcome mattered strongly, but mainly through policy and occupancy:

- primary minus online outcome-shuffled T alignment: **0.302 [0.234, 0.368]**;
- primary minus random credited-h T alignment: **0.267 [0.228, 0.305]**;
- with actual category/h/target visitation frozen, permuting outcome changed T alignment by only -0.000041 on average;
- the selected initial pattern's mean role alignment (0.3268) was already essentially the final T alignment (0.3268).

The information path was therefore:

```text
initial motor/soma geometry
        +
scalar outcome selecting which h is revisited
        ↓
outcome-conditioned trajectory occupancy
        ↓
within-(category,h) outstar averaging
        ↓
T ≈ selected experienced soma pattern
```

This is genuine outcome-driven information acquisition and structural credit. It is not arbitrary coordinate construction from an uninformative repertoire.

## Secondary plasticity controls

The calibrated generic scalar perturbation-based motor update improved LOW-coverage behavior over the fixed primary by 0.070 [0.022, 0.120], below the preregistered 0.20 floor. It therefore does not establish B4 or identify a sufficient added mechanism. The isolated hidden-vector positive control reached behavior 1.000 and exceeded the low primary by 0.235 [0.179, 0.290], verifying task learnability when neuron-wise information is supplied.

## Relation to frozen EXP003b

The earlier post-hoc diagnosis is replicated conceptually, not reinterpreted: frozen EXP003b's selected-h initial soma alignment predicted final emitted-T alignment at r=0.958 pre-remap and r=0.866 post-remap; corr(T,target mean) was 0.996/0.993. EXP004 prospectively demonstrates why: the implemented T[k,h] update stores the response topology selected by scalar outcome. Frozen EXP003b remains Outcome C.

## Figures

- `results/exp004/frozen_v1/figures/bank_size_coverage_behavior.png`
- `results/exp004/frozen_v1/figures/controlled_coverage.png`
- `results/exp004/frozen_v1/figures/composition_and_categories.png`
