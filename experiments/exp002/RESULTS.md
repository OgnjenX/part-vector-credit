# EXP002 results

## Development history

- **v0** is the preserved unreachable-endpoint failure at causal strength 0.34.
- **v1** is the first calibrated full suite and robustness grid. It exposed that the vector-error
  control did not place its teaching event in the dendritic measurement.
- **v2** repaired that positive control only.
- **v3** is the final pre-freeze development suite after renaming the first-window alignment so it
  cannot be mistaken for an initialization measure.

All runs and raw data are under `results/exp002/development_v*/`. The robustness grid is in
`development_v1/development_robustness.json`.

## What development v3 showed

The primary and plain contextual bandit had exactly the same behavior: 0.603 pre-remap evaluation
success and 0.384 post-remap, versus 0.156/0.175 frozen and 0.163/0.191 random. Removing structural
credit (0.050/0.003), working memory (0.009/0.022), or motivated reinforcement (0.156/0.175)
destroyed most selection learning. These ablations establish properties of this abstraction; the
identical strong bandit result means they do not establish a specifically pART computation.

The independently initialized outstar expectancy acquired role alignment: initial-bank mean
signed correlation was -0.008, while selected `T` reached 0.368 before and 0.256 after remapping.
The direct-copy bandit was slightly stronger (0.381/0.271). Old `T` versus the remapped roles was
-0.043. Context opposition was weak (0.114), below the preregistered 0.25 criterion.

The key Francioni analyses failed in development. Primary residual role alignment was negative
(-0.164/-0.206), and early residual did not predict later soma change (-0.212, 95% CI
[-0.420, -0.023], then -0.019 [-0.138, 0.102]). Direct copy failed similarly. The repaired
explicit-vector control validated the analysis: residual alignment was approximately 1.000 and
longitudinal prediction was 0.667 [0.621, 0.716] and 0.639 [0.561, 0.709], expressed specifically
after sensory feedback/outcome.

Suppressing top-down learning left behavior exactly unchanged while removing most learned `T`
alignment. Suppressing expression only during evaluation also left motor behavior exactly
unchanged and eliminated emitted alignment. Thus the modeled outstar branch currently reads out
which motor representation was selected; it does not cause the scalar selection learning.

ART reset/search occurred mainly during first encounters with new visible context/state patterns:
14 categories were recruited, with 0.022 resets per selection. After recruitment, primary
resonance was 1.000 and removing resonance gating was identical. Removing search collapsed the
model to one category, reduced pre-remap behavior to 0.500, and eliminated structured `T`, but did
not change post-remap evaluation behavior (0.384). Search is not a general explanation of the
cellular result.

Robustness was qualitative rather than universal. Primary pre/post success ranged from
0.453/0.169 to 0.653/0.722 across WM and reinforcement-rate settings. Varying outstar rate changed
alignment without behavior. Capacity 12, 48, and 192 produced 0.581/0.541, 0.603/0.384, and
0.491/0.441 success respectively; more random hypotheses did not monotonically improve this fixed
training budget.

These are development observations, not confirmatory conclusions. The held-out outcome remains
unassigned until the frozen run.

## Frozen held-out confirmation (`frozen_v1`)

The protected run used seeds 2000-2029 exactly once after protocol commit `6764932`. Raw data,
seed-level audits, statistics, and the preregistered figure are under
`results/exp002/frozen_v1/`.

### Initialization and behavior

There was no initial hidden-role vector. Mean signed motor and top-down correlations were 0.003
and 0.020. Decoder accuracies were 0.433 and 0.427 versus permutation-null means 0.392 and 0.392,
well within the preregistered 0.15 margin; mean permutation p-values were 0.509 and 0.520.

The primary learned behavior: evaluation success was 0.528 before remapping and 0.397 after it,
versus frozen 0.191/0.178 and random 0.200/0.162. Paired primary-minus-frozen intervals were
[0.256, 0.419] and [0.132, 0.308]; primary-minus-random intervals were [0.243, 0.416] and
[0.145, 0.329]. Structural-credit removal gave 0.024/0.039, no working memory 0.052/0.028, and no
motivated reinforcement 0.191/0.178.

The plain contextual bandit was **exactly identical** to the primary on all behavior values. Thus
the behavior supports delayed scalar selection over a random motor repertoire, not a uniquely
pART/SMART algorithm.

### Learned top-down pattern and remapping

The primary outstar expectancy reached selected-pattern correlation 0.343 before remapping and
0.287 after it. The previously selected pattern correlated only 0.056 with the new hidden map;
the post-remap increase to 0.287 passed the preregistered 0.20 remapping contrast. This is genuine
learned-expression emergence from an initially uninformative `T` bank, mediated by repeated local
sampling of selected soma patterns.

However, direct bandit pattern-copy produced 0.345/0.288—statistically indistinguishable from the
outstar primary. The two-context opposition score was only 0.135, below 0.25. Selection found
useful context-specific patterns, but it did not establish robust approximately opposite
expectancies for the same cells.

### Francioni residual and longitudinal test

The primary failed in the wrong direction. Soma-conditioned dendritic role alignment was
-0.206/-0.260. Early residual predicted later soma change at -0.326 (95% CI [-0.423, -0.224])
before remapping and -0.016 ([-0.120, 0.091]) afterward, rather than the preregistered positive
effect. Direct pattern-copy also failed: -0.324 ([-0.431, -0.216]) and -0.104
([-0.203, 0.000]). A plain bandit without patterned apical output was near zero.

The explicit vector-error positive control passed: role alignment was 1.000 before and after
remapping; longitudinal correlations were 0.660 ([0.636, 0.682]) and 0.545
([0.501, 0.589]). Its cell-specific residual appeared after sensory feedback and at outcome/post-
outcome (approximately 1.000), whereas the primary's negative statistic was unchanged across all
five timing bins. The task and analysis could therefore detect a supplied neuron-wise teaching
signal; the outstar/readout mechanisms did not generate it.

### Apical perturbations and ART search

Suppressing outstar/apical learning removed learned alignment (primary-minus-suppressed was 0.337
pre and 0.321 post, with paired intervals excluding zero) but changed behavior by exactly 0.000.
Suppressing expression only during evaluation also left motor behavior exactly unchanged while
zeroing emitted top-down alignment. The motor/apical separation worked, but it revealed the
apical branch as a non-causal readout in this architecture.

Search recruited 14 visible context/state categories and produced 0.022 resets per selection,
then ordinary resonance was 1.000. Removing resonance gating was exactly identical. Removing
reset/search collapsed recruitment to one category and eliminated top-down structure, but still
gave 0.477/0.415 behavior. ART search organized context/state representations; it did not explain
the Francioni cellular signal.

The corrected motor-basis outstar probe had a nonzero mean basis-change norm of 10.67, verifying
that the EXP001 no-op was repaired, but behavior deteriorated to 0.082/0.023. Locally consolidating
executed activity without neuron-wise causal information did not construct a useful motor basis.

## Classification

**Outcome C — behavioral selection works, learned top-down feedback does not reproduce
Francioni.** The tested Grossberg-compatible composition is falsified as an account of the full
Francioni phenomenon. It remains a valid account of how selection can make a learned patterned
expectation look cell-specific at an instantaneous level.
