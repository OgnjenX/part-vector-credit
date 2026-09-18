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
