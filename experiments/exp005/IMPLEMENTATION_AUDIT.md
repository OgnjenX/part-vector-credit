# EXP005 implementation and leakage audit

Status: **PRE-FREEZE**

## Separation of privilege

`GenericNodePerturbationLearner` has no method argument containing role, causal
label, target vector, derivative, or coverage. Its only outcome-learning inputs are
the scalar reward and its internally retained local eligibility. The hidden role is
used by the environment to compute BCI drive and by offline analysis.

`HiddenVectorOracle` is a distinct class with a plainly named
`privileged_update(hidden_role, ...)` method. Tests assert that this method does not
exist on the generic class.

## Information flow

| Operation | Inputs | Hidden information? |
|---|---|---|
| Emit RSC population | current `A_i`, local RNG perturbation | No |
| Environment transition | emitted `S`, hidden `c` | Environment only |
| Eligibility | locally emitted perturbation and decay | No |
| Generic update | eligibility, scalar outcome, scalar baseline | No |
| Outcome-shuffled update | same quantities with reward pairing permuted | No |
| Evaluation | learned weights and hidden role | Offline only |
| Oracle update | hidden `c_i` | Yes; isolated class-E control |

Neuron indices, initialization distribution, perturbation distribution, amplitude,
and learning rate are exchangeable. Roles are independently permuted for every seed
and remap. The population-size gain uses only public `N`, not role geometry.

## Reconstruction

Every perturbation, eligibility, assigned scalar reward, advantage, and recorded
weight delta is archived. Starting from the initial weights, analysis replays the
exact centering and bound operations using only those legal variables. A separate
cumulative-delta reconstruction guards serialization/history completeness.

## Known engineering simplifications

- one adaptive source projection rather than categories or multiple contexts;
- rate-coded RSC activity rather than spikes;
- independent Gaussian cell perturbations;
- a scalar exponential reward baseline;
- batched updates to make the shuffled control exact;
- population-size learning-gain normalization;
- bounded signed abstract weights rather than explicit opponent nonnegative
  synapses;
- deterministic stable-pattern evaluation without an RSC biophysical model.

All are class-D comparator assumptions. None is represented as pART, SMART, CogEM,
or a Grossberg-derived cortical mechanism.

## Automated checks

Tests cover role randomization/balance, absence of privileged arguments, separation
of the oracle, exact local update reconstruction, zero learning without exploration
or eligibility, de novo acquisition/remapping in a smoke run, and absence of
“Grossberg” condition names.

