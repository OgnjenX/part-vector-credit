# EXP005 mechanism classification

Status: **PRE-IMPLEMENTATION / SOURCE-CLASSIFICATION FREEZE CANDIDATE**

| Mechanism | Class | Reason | Eligible as Grossberg primary? |
|---|---|---|---|
| ART resonance, vigilance, reset/search, category recruitment | A — Grossberg-explicit | Primary ART equations specify match-gated category learning. | Only for representation ownership, not cellular topology credit. |
| pART working-memory causal trace and structural/temporal credit | A — Grossberg-explicit | Published pART assigns delayed outcomes to maintained causal representations. | Only for deciding which representation is eligible. |
| CogEM conditioned reinforcement, incentive motivation, Now Print timing | A — Grossberg-explicit | Published gated steepest-descent laws track drive/teaching activity. | Global/representation reinforcement only. |
| SOVEREIGN ERG exploratory action release | A — Grossberg-explicit | ERG is a published source of exploratory behavior. | No: its coupling to neuron-resolved reward covariance is absent. |
| Classical outstar storing a concurrent RSC population pattern | A — Grossberg-explicit as an associative operation | The source unit gates weights that track a postsynaptic target. | No: it assumes the spatial target pattern rather than deriving its causal signs. |
| pART + ERG + outstar with no new local reward-covariance term | B — Grossberg-derived composition | Each component is explicit and their composition is new. | No: still lacks a rule that makes reward affect cells differently. |
| pART + ERG + reward-modulated local perturbation eligibility + outstar | C/D — Grossberg-compatible extrapolation plus generic control | The missing `reward x local perturbation` operation is not source-derived. | **No.** This is the generic comparator. |
| SMART timing plasticity | A — Grossberg-explicit | Local spike timing and conductance determine plasticity. | No: arbitrary behavioral sign is not inferred from scalar reward. |
| VAM/aVITE adaptive maps | A — Grossberg-explicit | Learns with explicit Difference Vector/present-target signals. | No under the clean information boundary. |
| Cerebellar adaptive filter | A — Grossberg-explicit | Learns from error/correction channels. | No under the clean information boundary. |
| Opponent ON/OFF channels | A — Grossberg-explicit representational device | Supports signed encoding and push–pull control. | No: assignment of arbitrary neurons to channels is missing. |
| Node perturbation / REINFORCE / reward-modulated Hebbian eligibility | D — generic biological / ML control | Uses local variation and scalar outcome to estimate causal contribution. | No, unless future primary-source evidence changes the classification. |
| Direct `Delta w_i proportional to c_i` | E — hidden-vector/oracle | Receives the forbidden causal vector. | Never; oracle only. |

## Classification consequence

There is no class A or complete class B candidate for EXP005's critical adaptive
topology operation. The hard stop is active. Any executable learning comparison in
this stage must be named `generic_node_perturbation`, not `grossberg_*`, and cannot
be interpreted as confirmatory evidence for Grossberg.

