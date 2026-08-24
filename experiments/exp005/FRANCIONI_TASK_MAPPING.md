# EXP005 Francioni task mapping

Status: **TASK SPECIFICATION; NOT YET EXECUTED**

## Biological target

EXP005 models an arbitrary decoder over intermingled layer-5 RSC pyramidal neurons,
not a conventional motor output vector. The environment alone samples a balanced
hidden role vector `c in {-1,+1}^N`. Population activity drives a visible BCI state
through the normalized opponent contrast

`u_t = mean(S_i : c_i=+1) - mean(S_i : c_i=-1)`.

The learner may observe the evolving visual/BCI state, context when explicitly
provided, delayed scalar improvement/reward, and its own local neural variables. It
must not observe `c`, group labels, a neuron-wise target, a derivative, coverage, or
an oracle action.

## Clean initialization

Any adaptive source/category-to-RSC projection starts near zero or weak random with
prelearning `corr(A_H, c)` and emitted-pattern alignment measured before learning.
There is no fixed EXP004-style bank of candidate RSC vectors in the clean topology
test.

Stochastic exploration is not “coverage-free”: it creates an implicit support over
population states. Every perturbation must therefore be archived, and final
alignment must be compared with the best single experienced sample.

## Required acquisition and remap logic

1. Acquire control of one hidden mapping from initially uninformative topology.
2. Secretly remap to an independently sampled balanced `c'` without announcing
   which neurons changed.
3. Measure old alignment with `c'`, relearned alignment, per-cell sign reversals,
   and sample efficiency.
4. In a secondary observable-context version, test preservation and selection of
   separate learned topologies.

## Abstraction limits

This task does not model dendritic calcium or SMART dynamics. A successful generic
comparator would establish only that derivative-free scalar-reward learning can
construct arbitrary population topology in this abstraction. It would not show
that RSC uses the rule, that dendrites carry a gradient, or that Grossberg published
the missing mechanism.

