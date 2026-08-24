# EXP004 data dictionary

Each run directory contains `summary.json`, `statistics.json`, figures, hashes, and one compressed NPZ per scenario. Within an NPZ, every key is prefixed `seed_<seed>__`; variable-length event histories therefore remain lossless without padding across seeds.

## Initialization and oracle arrays

| Suffix | Meaning |
|---|---|
| `initial_motor_bank` | Every fixed B_h before learning |
| `initial_soma_response` | Deterministic prelearning S_h with no action noise |
| `hidden_role` | Environment-only c, saved for offline evaluation |
| `pairwise_similarity` | Full centered bank similarity matrix |
| `row_norms`, `row_means`, `row_variances` | Leakage/matching geometry |
| `phase_masks` | Effective-cell masks; all ones in the standard task |
| `oracle_frame_scores_context0/1` | Exact q_{f,h} used by allowed-action oracles |

## Episode/frame arrays

| Suffix | Meaning |
|---|---|
| `observation` | Learner-visible context, phase, normalized state |
| `soma` | Executed noisy population pattern |
| `perturbation` | Soma minus motor command; used only by generic motor control |
| `hypothesis`, `category`, `resonant` | Selected structural-credit state |
| `state_before`, `state_after`, `causal_score` | Closed-loop trajectory |
| `context`, `evaluating`, `reward` | Episode state |
| `actual_outcome`, `credited_outcome` | True versus shuffled/controlled scalar credit |
| `category_count` | Number of committed ART categories after each episode |

## Category events

`category_event_episode/frame/category/event_code/after/delta_norm` preserve every fixed initialization, bootstrap, recruitment, and resonant modification. The prior prototype is the preceding `after` state for that category (or uncommitted for its first event), avoiding redundant archival. Event-code mappings are sorted alphabetically and recoverable from the condition/source.

## Value events

`value_update_*` stores selected and credited h, category, actual/credited outcome, eligibility strength, and scalar value before/after for every maintained trace item.

## Top-down events

`topdown_update_*` stores selected and credited h, category, actual/credited outcome, strength, exact eta, and target vector. T starts at zero, so the ordered event stream independently reconstructs every intermediate and final T without archiving redundant before/after vectors.

## Motor events

`motor_update_*` exists only in the generic scalar motor-plasticity extension and stores h, scalar advantage, and B after each update; the previous state is the initial bank or prior event. The clean primary has an empty event array and zero motor-bank change.

## Final state

`final_topdown`, `final_values`, and `final_prototypes` archive all active memory slots. Summary rows include coverage, oracle, ART, structural-credit, reachability, T, sequence, behavior, and leakage metrics per seed.

Raw c/oracle arrays must never be loaded by primary learner code. Their presence is solely for independently recomputable evaluation.
