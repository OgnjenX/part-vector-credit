# EXP006 model-comparison contract

Status: **LOCKED BEFORE IMPLEMENTATION**

## Fairness rule

Every non-oracle model receives the same environment trajectory variables and the
same opportunity to act. Shared random-number streams are used for hidden roles,
initial motor repertoires, observation noise, and evaluation episodes whenever the
mechanism permits. Model-specific exploration is archived rather than forced to be
numerically identical.

Models are not forced to have the same parameter count. The comparison concerns
information and mechanism, not parameter efficiency. Parameter counts, update
equations, privileged inputs, and tuned quantities are reported explicitly.

## ART representation learner

The ART learner uses complement-coded observations containing displayed visual
state, within-trial phase, and the most recent visible state change. Fuzzy matching,
vigilance, reset/search, category recruitment, value learning, and outstar
expectancy learning follow the already audited EXP004 implementation unless a
prospective amendment explains a necessary task-interface change.

Its action is selected from a fixed, hidden-role-independent balanced repertoire.
No role-dependent motor coordinate may be inserted into that repertoire. Repertoire
coverage is measured offline. Any learned top-down expectancy is replayed exactly
from experienced targets.

## Local eligibility learner

The learner emits a deterministic cell-wise bias plus zero-mean local perturbation.
It stores each cell's perturbation in a decaying trace. Visible within-trial
improvement and delayed reward are scalar modulators. The hidden role never enters
the update. All clipping, centering, baselines, and update timing are replayed from
archived legal variables.

## Hybrid learner

The ART component selects a repertoire action. A separately identified adaptive
cell-wise correction is added before clipping. Only the correction is updated by
local eligibility. ART variables and eligibility variables are stored separately.
The hybrid is not attributed to Grossberg.

## Vector oracle

The oracle is the only learner permitted to receive the hidden role. Its purpose is
to establish that the task, observation model, and endpoints can express the
expected sign structure. Oracle success cannot establish biological plausibility.

## Disallowed shortcuts

- passing P+/P- labels to an ordinary learner;
- constructing a role-aligned motor bank;
- choosing observation-layer signs from the hidden role;
- selecting only successful cells or trials after inspecting confirmation;
- tuning a model on confirmatory mappings;
- interpreting a fixed-repertoire success as de novo topology learning;
- treating simulated dendritic residual as a directly measured biological error.
