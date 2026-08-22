# EXP003b statistical analysis plan

The unit of replication is the hidden-mapping seed (`n=12` confirmation seeds),
not a neuron, frame or episode. Condition contrasts are paired by seed because all
conditions share environment mappings, motor initialization and opportunities.

Means and 95% confidence intervals use 5,000 nonparametric seed-level bootstrap
resamples. Individual longitudinal intervals use RNG seed 80303; paired contrasts
use 90303. These choices and all classification predicates are executable in
`src/part_credit/exp003b/statistics.py` and frozen by SHA-256 before confirmation.

The key analysis is within a fixed hypothesis. For each context/window, the most
frequently sampled hypothesis across early and late records is selected. Its
early soma-conditioned dendritic signal is correlated across eight neurons with
its own later weight change and its learning-off feedforward-only future response
change. This guards against a false longitudinal result caused only by switching
from one pre-existing motor basis row to another.

Correlations with insufficient events or zero variance are defined as zero before
seed aggregation. This conservative convention was fixed during development.
No multiplicity-adjusted discovery claims are made: this is a conjunction test
with preregistered floors, and failure of any required item blocks Outcome A.

The temporal analysis reports role-alignment of the residual separately for:
category selection, pre-action expectation, action execution, sensory feedback,
outcome and post-outcome. The primary Grossberg composition is evaluated at
pre-action expectation; the explicit positive control at sensory feedback.

## Frozen confirmation result

The executable classifier returned `C_COMPOSITION_FAILS_LONGITUDINAL_CHAIN`.
Behavior, no-initial-vector, expectation-emergence, top-down-timing, remap, and
positive-control criteria passed. Longitudinal-chain, `T→SMART` specificity,
expression-separation and context-opposition criteria failed. The generic full
chain was false. Exact paired estimates and predicates are preserved in
`results/exp003b/frozen_v1/statistics.json`; no post hoc test changed classification.
