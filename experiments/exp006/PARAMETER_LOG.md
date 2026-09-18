# EXP006 parameter log

Status: **DEVELOPMENT OPEN; CONFIRMATORY PARAMETERS NOT FROZEN**

## Locked before code

- Primary neurons: 10.
- Secondary neurons: 8.
- Action frames: 28.
- Visual bins: 7.
- Trials per block: 64.
- Acquisition blocks: 14.
- Hidden-remap blocks: 14.
- Development seeds: 601--608.
- Reserved confirmation seeds: 12000--12031.
- ART repertoire size: 64 balanced patterns unless a prospective development
  amendment documents a computational or identifiability failure.

## Still to calibrate on development seeds

- state gain and success tolerance;
- action and observation noise;
- ART vigilance and learning rates for the longer within-trial sequence;
- eligibility perturbation scale, decay, baseline, and learning rates;
- relative scale of ART and eligibility actions in the hybrid;
- common dendritic observation coefficients;
- confirmatory numerical pass floors.

Every change will be appended with the reason, affected development run, and whether
the change was made before inspecting the relevant endpoint.

## 2026-09-18: state gain after development_v3_core

The initial state gain was 0.12. In `development_v3_core`, the ART learner selected
the best available acquisition pattern (mean alignment 0.65) but obtained zero
success. This was a reachability failure: with motor amplitude 0.20, alignment 0.65,
28 frames, and gain 0.12, the maximum expected state was below the target display
bin. The result therefore could not test whether selected representations support
behavior.

State gain is changed prospectively to 0.18. At this gain a repertoire direction
with alignment above approximately 0.46 can reach the target, while a random or
near-orthogonal direction cannot. No model-specific parameter is changed. The
oracle/null sensitivity run and all three core development results remain archived.

## 2026-09-18: final implementation audit before freezing

No learning-rate, vigilance, exploration, eligibility, observation-noise, or hybrid
action parameter was changed after the state-gain calibration. The audit made two
measurement/control corrections that do not alter primary-model behavior:

- shuffled modulators now sample one element from prior history by index, avoiding
  repeated conversion of a growing list and ensuring that the current outcome is
  never assigned to itself;
- the hybrid observation signal now applies each declared component gain once and
  archives ART, eligibility, and vector components separately. Earlier hybrid
  behavior is unchanged because the error was confined to the synthetic dendritic
  readout.

Soma-matched scores are declared unidentified when role-by-direction groups have no
overlapping somatic samples. The minimum identifiable mean is 100 matched samples
per seed in each phase.

## 2026-09-18: confirmatory floors selected from development controls

The following scenario-mean floors are fixed before accessing seeds 12000--12031.

- Behavioral pass: acquisition and remap late success are each at least 0.60.
- Topology pass: acquisition and remap role correlation are each at least 0.55;
  acquisition and remap correct-sign fractions are each at least 0.75; changed-cell
  sign reversal is at least 0.70.
- Francioni-signature pass: latent vectorization is at least 0.10 and measured
  residual vectorization is at least 0.01 in both phases; pre- and post-outcome
  decoding balanced accuracy are each at least 0.58; prospective activity
  prediction is at least 0.20 in both phases.
- Identifiable soma-matched preservation requires a residual score of at least
  0.005 in both phases. It is an additional requirement only when the matching
  count passes the identifiability floor.

Control-effect floors and the exact machine-readable rules are stored in
`FROZEN_PROTOCOL.json`. Classification uses scenario means. Confidence intervals
are reported but do not replace the frozen rule.
