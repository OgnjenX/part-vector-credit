# EXP005 frozen generic-diagnostic protocol

Status: **READY TO FREEZE; GROSSBERG PRIMARY RUN FORBIDDEN**

## Scientific outcomes

The source audit has already fixed the theory classification as **Outcome E: no
Grossberg candidate exists**. The held-out run tests only whether a separately
labeled generic local perturbation rule can perform the missing operation. If it
succeeds, the combined interpretation is category C/E: scalar reward is sufficient
in principle given a new cellular eligibility rule, but Grossberg's audited theory
does not supply that rule.

## Seeds and stages

- development seeds: 501–504;
- held-out seeds: 9500–9515, never used during development;
- acquisition: 1,280 episodes under random balanced `c`;
- hidden remap: 2,560 episodes under independent balanced `c'`;
- action frames per episode: 3;
- remap Hamming fraction constrained to `[0.25, 0.75]`.

The longer remap window was selected before confirmation because it must first undo
an established old topology. The equal 1,280/1,280 development run is preserved as
a failed calibration and did not justify lowering any outcome floor.

## Frozen scenarios

At every `N in {8,16,32,64}`:

1. `generic_node_perturbation` — class-D comparator;
2. `outcome_shuffled` — exact within-block reward permutation;
3. `hidden_vector_oracle` — class-E sensitivity control.

At N=32 additionally:

4. `plasticity_disabled`;
5. `temporal_eligibility_disabled`;
6. `exploration_removed`;
7. `random_no_learning` with exactly zero deterministic topology.

## Frozen endpoints

- initial, pre-remap, old-to-new, and post-remap topology–role correlation;
- fraction of cells with correct learned sign;
- sign-reversal accuracy among remapped cells;
- stable no-noise BCI control and threshold success;
- best exploratory-sample alignment and final-minus-best-sample;
- weight-space distance;
- exact update-history reconstruction error;
- exact legal-local-equation reconstruction error;
- local eligibility-to-update correlation;
- local predicted-to-recorded update correlation;
- alignment of per-cell eligibility/outcome covariance with hidden role;
- global outcome-magnitude-to-update-magnitude correlation;
- acquisition/relearning trajectory and population-size scaling.

## Frozen support floors for the generic diagnostic

At the N=32 anchor, generic cellular credit is classified as working only if:

- mean pre-remap topology alignment >= 0.70;
- mean post-remap topology alignment >= 0.70;
- mean post-remap correct-sign fraction >= 0.80;
- mean changed-cell sign-reversal accuracy >= 0.75;
- generic minus outcome-shuffled post-remap alignment >= 0.40 with paired 95% CI
  excluding zero;
- generic minus exploration-removed post-remap alignment >= 0.40 with paired 95%
  CI excluding zero;
- no hidden role enters the generic learner;
- update histories reconstruct to <= `1e-12` RMSE.

The stable behavioral success threshold remains 0.60. It was not lowered after
development.

Exceeding every exploratory sample is a strong construction endpoint but is not a
required pass criterion: finite stochastic support can contain a lucky sample.
Failure to exceed it must be reported, not hidden.

## Statistical plan

All scenario means and paired seed effects use 5,000 deterministic bootstrap
replicates. The N=32 anchor determines the binary generic-learning classification.
Other population sizes describe scaling and do not retroactively change the floor.
No multiple-comparison-adjusted discovery claims are made.

## Freeze and execution

The machine-readable protocol locks scenario order, parameters, output directory,
seeds, thresholds, and SHA-256 hashes of every source/test file. Confirmation is
append-only and runs once into `results/exp005/frozen_generic_v1`. It is not a
confirmatory Grossberg experiment.

