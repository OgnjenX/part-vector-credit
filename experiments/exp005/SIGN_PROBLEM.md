# EXP005 cellular sign problem

Status: **PRE-IMPLEMENTATION**

## What must be learned

The environment assigns arbitrary intermingled roles `c_i in {-1,+1}`. A useful
stable control topology must promote activity in cells with positive roles and
reduce activity, or route control through an opponent channel, for cells with
negative roles. Scalar reward has no neuron index.

## What Grossberg supplies

- **Opponent ON/OFF and agonist/antagonist channels:** VITE/aVITE explicitly use
  push–pull representations so a signed desired or difference vector can increase
  one channel and inhibit the other.
- **On-center/off-surround competition:** ART/SMART/SOVEREIGN can enhance a selected
  population and suppress competitors.
- **Bidirectional adaptive traces:** gated steepest-descent weights can increase or
  decrease toward their sampled teaching activity; SMART-derived local plasticity
  can change with pre/post timing.
- **Mismatch/difference representations:** VAM and motor-control models compute
  signed coordinate errors and use them to calibrate adaptive maps.

## What is missing

Those mechanisms can *express* or *apply* signed information once a population,
coordinate, or target has been assigned. They do not infer the arbitrary BCI
partition from scalar reward. A nonspecific off-surround also cannot encode an
arbitrary intermingled P- subset: its suppression is defined by network geometry or
competition, not the hidden decoder.

The only audited Grossberg motor learners that clearly solve direction use a
structured desired/present mismatch. Giving that vector to EXP005 would be class E
oracle information.

## Minimal generic solution and its status

Signed node perturbation can estimate the direction without an explicit derivative:

`Delta A_Hi proportional to (R-b) xi_i`.

Positive covariance increases a coordinate; negative covariance decreases it. An
equivalent biological implementation could use opponent nonnegative synapses
`A_i+ - A_i-`, but the causal estimator remains the new ingredient. This is a
generic three-factor mechanism, not source-derived Grossberg theory in the audited
literature.

## Testable implication

If scalar reward learning exists biologically, trial-to-trial local RSC deviations
must leave a cell/synapse-specific trace whose interaction with later outcome
predicts subsequent signed change. Demonstrating only a global reward response,
on-center/off-surround modulation, or match-gated plasticity is insufficient.

