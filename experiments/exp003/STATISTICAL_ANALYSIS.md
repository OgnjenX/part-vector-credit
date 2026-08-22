# EXP003 statistical analysis — draft

No statistical result has been computed.

Planned principles:

- seed is the independent unit for confirmatory inference;
- all condition contrasts are paired by environment mapping and initialization;
- confidence intervals use a frozen seed-level bootstrap procedure;
- leakage decoding is judged against a frozen label-permutation null;
- longitudinal residual definitions are fitted/cross-fitted without later endpoints;
- pre/post-remap and context endpoints are separate, not pooled after inspection;
- within-hypothesis analyses hold `h` fixed;
- the joint Outcome-A endpoint requires behavior, `D -> Delta W`, `D -> Delta S`, remap,
  context, and causal-ablation criteria together;
- multiplicity handling, window definitions, exclusions, and minimum event counts will be selected
  on development data and frozen before confirmation;
- effect size and uncertainty, not only `p` values, determine classification.

Candidate minimum effect floors are recorded in `THEORY_AUDIT.md`; they are not frozen thresholds.
