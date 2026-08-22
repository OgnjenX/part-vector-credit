# EXP001 result data dictionary

JSON files contain configuration, condition summaries, and every seed-level metric.
NPZ files contain deterministic trial records for reanalysis.

For each condition, scalar raw arrays have shape `[seed, trial, 8]` with columns:

1. trial index;
2. binary reward/success;
3. global visual-error improvement;
4. final absolute task error;
5. selected hypothesis index;
6. selected observable-context category;
7. resonance indicator; and
8. number of resets during search.

Primary-condition neural arrays have shape `[seed, trial, 4N]`, concatenating:

1. mean somatic activity for each neuron across action frames (`0:N`);
2. mean dendritic proxy activity (`N:2N`);
3. environment-only causal contribution used only for analysis (`2N:3N`); and
4. the hidden causal role vector (`3N:4N`).

The latter two blocks are never passed to a Grossberg-inspired learner. Their
presence in result artifacts enables leakage audits and causal-role analyses.

NPZ keys encode their nested JSON path. For example,
`primary__conditions__grossberg_inspired_full___raw` is the full condition's
scalar trial record. Development additionally contains raw sweep/probe arrays;
confirmation contains primary and capacity arrays.

