# EXP003b raw-data dictionary

Each condition has one compressed NPZ under `results/exp003b/<run>/raw/`. The
leading dimension is seed; then episode, action frame and (where applicable)
phase/neuron. `summary.json` holds configuration, seed metrics and aggregate
metrics; `statistics.json` holds paired tests and the frozen classifier.

| Array | Meaning |
|---|---|
| `soma` | Lower-cell output used by the BCI environment |
| `dendrite_phases` | Modeled dendritic measurement at six frozen event phases |
| `topdown` | Learned/raw top-down expectancy emitted by selected `H[k,h]` |
| `weight_before`, `weight_after` | Local lower weights around each action frame |
| `v_peak_mv` | Brian2-derived peak lower-cell membrane voltage |
| `g_ff_peak`, `g_td_peak`, `g_inh_peak` | Brian2-derived conductance peaks |
| `spike_count`, `first_latency_ms` | Actual motif spikes and first-spike latency |
| `counterfactual_no_t_spike_count`, `counterfactual_no_t_latency_ms` | Same motor/weight/reset state replayed with local top-down set to zero |
| `hypothesis`, `category`, `resonant` | Selected representation and ART state |
| `error_improvement` | Visible frame-to-frame reduction in task error |
| `causal` | Environment-only hidden causal role, saved solely for offline analysis |
| `episode_scalar` | Episode, context, evaluation flag, reward, global improvement, final error, WM strength and category count |

`causal` must never be read by primary/baseline learner code. Only the explicit
vector-credit condition may receive a copy during learning.

`SHA256SUMS.json` hashes every result artifact except itself. Figures are derived
from the frozen summaries; raw results remain the authoritative record.
