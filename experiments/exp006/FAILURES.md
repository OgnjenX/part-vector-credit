# EXP006 development failures

## development_v0_oracle

The vector oracle and random null were run on development seeds 601--608 before
any ordinary learner was inspected. The task separated their behavioral and
role-vectorization endpoints. The oracle reached alignment and late success of
1.0, while the null did not learn.

The run nevertheless failed as an endpoint-sensitivity calibration. The oracle
updated its privileged topology at every action frame and therefore succeeded on
all trials. Successful-versus-unsuccessful decoding was undefined and returned its
specified fallback of 0.5. Its within-trial convergence also made the prospective
early-to-late activity endpoint insensitive.

Prospective correction: the oracle update is moved to one update per completed
trial. The cell-wise feedback signal remains available during the trial. The
post-outcome oracle signal is signed by success versus failure so the observation
layer has a positive sensitivity control for outcome decoding. No ordinary model
or ordinary-model result was inspected before this change.

## development_v1_oracle

Moving the oracle update to the trial boundary restored endpoint sensitivity for
pre-outcome decoding (mean balanced accuracy 0.915) and post-outcome decoding
(1.0). The prospective activity endpoint remained near zero because its baseline
was defined as mean activity across the full early quarter. The oracle had already
learned during that interval, so baseline regression removed the role-dependent
change that the endpoint was intended to predict.

Prospective correction: baseline activity is now measured in the first, genuinely
prelearning trial of each phase. The early residual signal still uses the first
quarter, and the later activity target still uses the last quarter. This definition
is closer to comparing early teaching signals with subsequent change from initial
activity. No ordinary learner had been run when this correction was made.

## development_v3_core

The first ordinary-model run compared ART repertoire selection, local eligibility,
and the hybrid on seeds 601--608. ART selected the best available pattern before and
after remapping: its final alignments exactly matched mean best-bank coverage (0.65
and 0.75). It nevertheless had zero late success in both phases.

This was not interpretable as a behavioral failure of representation selection.
Given motor amplitude 0.20, state gain 0.12, and 28 frames, the acquisition pattern
with alignment 0.65 could not move the latent state far enough to reach the target
display bin even under perfect repeated selection. State gain was an explicitly
open development parameter and is increased to 0.18 for the next run. The change is
applied identically to every condition.

The uncalibrated run also showed that local eligibility acquired the first mapping
(alignment 0.932, late success 0.877) but incompletely reversed the established
topology during the equal-length remap phase (alignment 0.455). The hybrid showed a
similar remap limitation. No learning rate is changed until the common state-gain
correction is evaluated.

## development_v5_controls (interrupted; no dataset)

The first control-suite attempt was manually interrupted during the first shuffled
ART scenario. Sampling from the growing history of modulators used
`Generator.choice` directly on a Python list. NumPy converted the full list to an
array on every frame, making the run progressively slower. The command had not
finished any scenario and therefore wrote no result dataset.

The implementation now draws an integer history index and reads that single list
element. This preserves the intended sampling distribution without repeatedly
copying the history. No scientific endpoint from the interrupted attempt was
inspected.

During the same implementation audit, the hybrid's ART observation signal was found
to receive its declared gain twice. The first scaling happened when the action was
created and the second when ART and eligibility feedback were combined. This did not
change the hybrid's behavior or learning, but it incorrectly attenuated the synthetic
dendritic signal. The first scaling is removed, so each component is now combined
exactly once. ART, eligibility, and vector-oracle components are also archived
separately for direct attribution. Previously archived development runs are retained.

Failures, abandoned calibrations, and protocol amendments are append-only.
