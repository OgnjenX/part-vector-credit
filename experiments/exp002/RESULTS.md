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
