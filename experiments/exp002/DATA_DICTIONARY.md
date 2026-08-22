# Raw-data dictionary

Each condition has a compressed NPZ file under the run's `raw/` directory. Axis 0 is seed and axis
1 is BCI episode/trial. Data are float32 unless stated otherwise.

| Array | Shape after seed/episode | Meaning |
|---|---|---|
| `scalar` | `[10]` | episode, context, evaluation flag, reward, global improvement, final error, resonance fraction, reset count, final hypothesis, final category |
| `soma_frames` | `[8, N]` | lower-level somatic/output activity for each closed-loop frame |
| `dendrite_phase_means` | `[5, N]` | modeled dendritic activity averaged over frames at selection, action, sensory feedback, outcome, post-outcome timing bins |
| `topdown_frames` | `[8, N]` | emitted top-down pattern before common soma/network terms |
| `hypothesis_frames` | `[8]` int16 | selected higher-order hypothesis on every frame |
| `causal` | `[N]` int8 | hidden active causal role, saved for offline analysis only |

`summary.json` contains full seed-level metrics and initialization audits. `statistics.json`
contains preregistered paired seed-bootstrap comparisons. The abstraction records continuous
activity rather than Francioni's matched event magnitudes; its residual is therefore analogous,
not measurement-identical.
