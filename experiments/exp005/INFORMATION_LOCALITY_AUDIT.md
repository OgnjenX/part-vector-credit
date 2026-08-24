# EXP005 information-locality audit

Status: **PRE-IMPLEMENTATION**

## The missing computation

For projection weight `A_Hi`, the same delayed reward reaches every neuron. A legal
rule needs a local quantity that differs across `i`; otherwise all weights receive
the same update and cannot learn arbitrary hidden signs.

| Quantity | Where available? | Grossberg source status | Permitted in clean learner? |
|---|---|---|---|
| Source/category activity `H` | Pre-synaptic/local to projection | Explicit in outstar and ART pathways | Yes |
| RSC activity `S_i` | Post-synaptic/local | Generic and explicit in associative rules | Yes |
| Local perturbation `xi_i` | Local if a neuron retains its own deviation | ERG supplies exploration at action/vector level; neuron-level retained perturbation is not specified | Only in generic comparator; archived |
| Eligibility `e_Hi` retaining `H * xi_i` | Synapse-local | Not found for this outcome-credit operation | New assumption; generic comparator only |
| Scalar reward/outcome `R` | Diffuse/modulatory | Reinforcement/drive/Now Print signals are explicit | Yes |
| Reward baseline `b` | Global or representation-specific | Not identified as the relevant local rule in audited sources | Generic comparator assumption |
| Category identity | Present at active source synapses | Explicit through source activity; no address broadcast is needed | Yes |
| Hidden `c_i`, P+/P- label | Environment only | Not learner information | **Forbidden** |
| `partial R / partial S_i` | Oracle only | Not learner information | **Forbidden** |
| Desired neuron-wise RSC target | Oracle/teacher | VAM/outstar motor maps often do receive structured targets | **Forbidden** in clean primary |

## Equation audit

### Source-derived outstar

The generic Grossberg outstar form is

`dA_Hi/dt = eta H (S_i - A_Hi)`.

Two weights differ because their coactive postsynaptic targets `S_i` differ. Reward
can gate *whether* the active pattern is stored, but without a local causal
eligibility it cannot say whether an elevated `S_i` caused the reward. This is
associative storage, not arbitrary cellular credit.

### Generic comparison (not Grossberg)

A minimal node-perturbation comparison would use

`e_Hi(t+1) = lambda e_Hi(t) + H(t) xi_i(t)`

`Delta A_Hi = eta (R - b) e_Hi`.

`A_H1` and `A_H2` differ because `xi_1` and `xi_2` differ locally, even though
`R-b` is global. This equation directly answers the locality question, but its
critical multiplication of outcome by a stored neuron-specific perturbation was
not found in the audited Grossberg sources. It is class D.

### VAM comparison

VAM weights differ because each postsynaptic coordinate receives a different
Difference Vector or target-position component. That is a valid local motor-learning
solution in its original task but imports precisely the structured teacher that
EXP005 withholds.

## Hard conclusion

Grossberg's published mechanisms specify local variables and scalar motivational
gates, but the audit did not find the required synaptic conjunction of delayed
scalar outcome with a neuron-varying exploratory eligibility. That conjunction is
the minimal additional assumption.

