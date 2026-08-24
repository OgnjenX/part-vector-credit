# EXP004 statistical analysis plan

## Unit and intervals

The hidden mapping/bank seed is the unit of replication. All primary means and paired differences use 5,000 seed bootstrap resamples. Nested M rows are resampled as whole seed clusters.

## Bank-size mediation

For each experience regime and learner separately:

\[
A_{single}=a_0+a\log_2M,
\]

\[
behavior=c_0+c\log_2M,
\]

\[
behavior=d_0+c'\log_2M+bA_{single}.
\]

Report a, b, total c, indirect \(ab\), direct-model R², and cluster-bootstrap intervals. Mediation is descriptive because M changes search dimensionality as well as coverage.

## Controlled coverage

At M=16 report LOW/MEDIUM/HIGH A/Q distributions, coverage–behavior and coverage–T correlations, and paired HIGH–LOW behavior. The preregistered repertoire-limitation effect is HIGH–LOW normalized behavior ≥0.15 with CI above zero.

## Oracles and composition

Report learner minus best repeated-single and allowed-sequence minus learner. B2 requires composition advantage ≥0.15 with CI above zero and oracle gap ≤0.10. Random-bank oracle-solvable failures are reported independently as B3/search limitation.

## ART contribution

At identical medium coverage, compare full ART to contextual bandit, fixed categories, no recruitment, and no modification for behavior, success, T, category count, prototype change, reset, and same-h T factorization. No ART-specific support is claimed from unpaired scenario differences.

## Information-source decomposition

Report:

- actual primary minus online outcome-shuffled behavior/T;
- primary minus random credited-h control;
- actual T versus frozen-visitation outcome-permutation T;
- selected-initial alignment versus final T;
- exact T reconstruction and target-average similarity.

Outcome contribution and repertoire geometry may both be positive; effects are not forced to sum linearly.

## Classifier

The exact implementation in `statistics.py` and thresholds in `FROZEN_PROTOCOL.json` are authoritative. Behavioral and representational flags are separate and may coexist. R4 or failed bank solvability forces A2 non-diagnostic before theoretical interpretation.
