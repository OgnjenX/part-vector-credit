# EXP005 failure log

Failures are retained as methodological evidence and are not confirmatory results.

1. **Source-derived mechanism absent.** The primary-source audit found no published
   Grossberg rule joining neuron-local exploration to delayed scalar outcome with a
   bidirectional local update. This activated Outcome E and prohibited the planned
   Grossberg-primary run.
2. **v1 remap ceiling.** With 640 remap episodes, mean N=64 role alignment was
   0.686. The old topology required explicit unlearning time.
3. **v1 oracle warnings.** Correlation analysis received empty finite arrays because
   the oracle intentionally has no generic eligibility/outcome trace. `safe_corr`
   now returns zero for fewer than two samples; scientific calculations are
   unchanged.
4. **v2 larger base learning rate ineffective.** Raising 0.0015 to 0.0020 did not
   repair remapping and was reverted.
5. **v4 fixed-gain scaling limitation.** N=64 acquired correct signs but stable BCI
   control was only 0.183 after 640 episodes. This reflected the task's explicit
   population-mean normalization.
6. **v6 equal-stage remap failed the 0.70 floor at several N.** A 1,280-episode
   remap produced mean alignments 0.634, 0.714, 0.685, and 0.703 for N=8,16,32,64.
   The remap budget was doubled; the floor was not lowered.
7. **Development does not uniformly exceed the best single sample.** With finite
   stochastic exploration, some low-N and post-remap runs contain a sample as good
   as or better than the stable learned pattern. This endpoint remains descriptive,
   not a pass criterion.

Raw development directories remain local. Versioned parameter decisions and all
development summary/statistical outputs needed to reproduce these decisions are
committed; the held-out raw archive is mandatory and will be published via Git LFS.

