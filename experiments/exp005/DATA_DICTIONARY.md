# EXP005 raw-data dictionary

Each scenario archive contains keys prefixed by `seed_<seed>__`.

| Suffix | Shape | Meaning |
|---|---|---|
| `role_initial`, `role_remap` | `(N,)` | Hidden balanced roles; offline analysis only. |
| `weights_initial`, `weights_pre_remap`, `weights_final` | `(N,)` | Adaptive topology checkpoints. |
| `weights_trajectory` | `(blocks+checkpoints,N)` | Block-level topology trajectory. |
| `soma` | `(episodes,frames,N)` | Emitted RSC population activity. |
| `perturbation` | `(episodes,frames,N)` | Actual post-clipping local exploration. |
| `state` | `(episodes,frames+1)` | Closed-loop visible BCI state. |
| `episode_reward` | `(episodes,)` | True final scalar outcome. |
| `role_phase` | `(episodes,)` | 0 acquisition, 1 hidden remap. |
| `episode_alignment` | `(episodes,)` | Offline current topology/role alignment. |
| `update_delta` | `(updates,N)` | Every recorded topology change. |
| `update_eligibility` | `(updates,N)` | Local trace paired with outcome. |
| `update_assigned_reward`, `update_true_reward` | `(updates,)` | Learning reward and actual reward; differ only in shuffled control. |
| `update_advantage` | `(updates,)` | Assigned reward minus pre-update scalar baseline. |
| `update_episode` | `(updates,)` | Episode owning the update. |
| `sample_alignment_pre`, `sample_alignment_post` | `(episodes*frames,)` | Offline alignment of every exploratory sample. |

Soma, perturbation, state, and block trajectories use float32 to control archive
size. Weight deltas and eligibility retain float64 so exact update reconstruction is
independently testable. Every file is checksummed after creation.

