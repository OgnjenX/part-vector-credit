# EXP003 raw-data dictionary — draft

No data have been generated. Planned raw records must include enough state to recompute every
metric without hidden mutable state.

| Field | Shape/level | Meaning | Learner-visible? |
|---|---|---|---|
| `seed`, `condition`, `episode`, `frame`, `phase` | identifiers | Exact opportunity and circuit phase | yes except aggregate labels |
| `context_observation`, `visual_state`, `target` | frame | Observable task input | yes |
| `hidden_causal_role` | seed/context/neuron | Environment role `c_i` | **offline only** |
| `category_id`, `category_match`, `category_committed` | decision | Learned ART state | yes |
| `hypothesis_id`, `H_activity`, `wm_trace` | decision/frame | Structural/temporal credit state | yes |
| `motor_basis` | hypothesis/neuron | Initial/current `B_h` | yes |
| `topdown_weight` | category/hypothesis/neuron | Learned `T_{k,h,i}` | yes |
| `apical_activity` | phase/neuron | Modeled dendritic `D_i` | yes/local |
| `lower_weight` | hypothesis/neuron | Plastic `W_lower` controlling future soma | yes/local |
| `pre_trace`, `post_trace`, `local_voltage` | phase/neuron | Inputs to SMART-derived update | yes/local |
| `resonance`, `reset`, `search_count`, `gamma_gate` | phase/decision | Match and learning gate | yes |
| `soma` | frame/neuron | Output `S_i` sent to BCI | yes |
| `counterfactual_same_h_soma` | evaluation/neuron | Soma under held hypothesis for longitudinal test | analysis probe |
| `bci_control`, `state_next`, `task_error`, `delta_error` | frame | Environment transition | state/error visible as preregistered; control derivative hidden |
| `reward`, `outcome`, `now_print_scalar` | outcome | Scalar feedback and global modulation | yes |
| `delta_topdown`, `delta_lower_weight` | plasticity/neuron | Auditable local changes | yes/local |
| `perturbation_mask` | phase/branch | Exact causal manipulation | experimental control |

The frozen dictionary will specify dtype, units, storage format, compression, missing-value rules,
and whether each analysis field is recorded or derived.
