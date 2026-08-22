# EXP003 theory-to-implementation mapping

Status: proposal only. Code symbols and line links will be added after implementation. A missing
code link means the mechanism has not yet been implemented.

| Source | Equation or circuit principle | Role in EXP003 | Proposed implementation | Classification | Known simplification or risk |
|---|---|---|---|---|---|
| Grossberg & Versace 2008, Eq. 5–6 | Bounded synaptic law gated by pre/post activity and postsynaptic spike timing | Change lower weights that control future soma | Discrete validated integration of Eq. 5 for `W_lower` | Grossberg-derived | Frame-level BCI requires a reduced within-frame spike/trace simulation. |
| Grossberg & Versace 2008, §§1.1, 2.1–2.4 | Match/gamma places winning cells inside STDP window; off-surround delays/suppresses competitors; mismatch/beta/reset blocks learning | Make top-down pattern causally cell-selective without `c_i` | `T` alters local voltage/timing; resonance permits `W_lower` integration | Grossberg-derived principle | Lower BCI neurons are not literal LGN/V1 cells. |
| Grossberg & Versace 2008, Fig. 6d and §2.4 | Dual-AND top-down learning associates higher output with active lower L5/apical target | Learn patterned `T` independently of motor basis | Resonance-gated local outstar/dual-AND update of `T_{k,h}` | Grossberg-derived principle | Exact conductance dynamics are reduced. |
| Grossberg 2021, §§3.1–3.6 | Modulatory on-center/off-surround matching and feature-category resonance | Translate `D` into priming/suppression rather than motor drive | Center/surround modulation of lower state before local STDP | Grossberg-derived principle | Discrete normalized surround rather than full laminar equations. |
| Grossberg 2018, §3.19 | Sustained causal ensemble plus later reinforcement solves structural/temporal credit | Assign delayed scalar outcome to selected `H` | Working-memory/eligibility trace and scalar hypothesis competition | pART-inspired | Reduced selector, not equation-complete pART/CogEM/BG circuitry. |
| Grossberg 2018, §§2.9, 3.19 | Motivated attention and broad Now-Print modulation strengthen predictive representations | Bias recurrence/gain of successful `H` | Scalar source gain and value update only; no neuron-vector multiplication | Grossberg-compatible abstraction | Generic scalar learning must be compared directly with bandit. |
| ART category learning/search | Learned category prototype, vigilance match, reset, and uncommitted recruitment | Discover context/state categories instead of hard-coded A/B feedback slots | Complement-coded observation category `k`; `H_{k,h}` reads `T_{k,h}` | Grossberg-compatible composition | Category×motor conjunction is not a published pART BCI circuit. |
| SMART visual adaptive filter mapped to BCI output population | Lower learned weights alter future postsynaptic conductance | Create `D -> Delta W -> Delta S` chain | `W_lower[h,i]` scales future motor-channel input to soma `i` | Grossberg-compatible extrapolation | Cross-system mapping is the central inferential limitation. |
| Gaudiano & Grossberg 1991 VAM/aVITE | Target-present vector mismatch calibrates a movement map | Separate corrected motor-basis plasticity probe | No hidden `c`; only observable target/state mismatch if used | Grossberg-compatible control | Not the main scalar-credit mechanism; exact VAM vector is unavailable for hidden roles. |
| Standard contextual bandit | Scalar reward updates action value with eligibility | Strong non-Grossberg behavioral comparator | Same bank, opportunities, delays, exploration, contexts | Non-Grossberg control | No ART category/search machinery. |
| Standard reward-gated Hebbian learning | Successful pre/post activity consolidates local weights | Test generic feedback sufficiency | Bounded local Hebb gated by scalar success, without `T` or resonance | Non-Grossberg control | Must not be described as Grossberg-specific. |
| Direct motor-pattern copy | Selected `B_h` is exposed as `D` | Detect a routing/readout confound | No learned `T`, no causal dendrite-to-plasticity route | Non-Grossberg diagnostic | Expected to reproduce some instantaneous alignment only. |
| Hidden role / neuron-wise derivative | Explicit cellular target | Positive-control learnability | Only explicitly named vector-credit condition may access `c` | Non-Grossberg positive control | Forbidden in all primary/ablation conditions. |

## Claim boundary

The local SMART mechanism is source-derived. Joining pART-style outcome-selected representations
to that mechanism in a hidden-causal BCI is a Grossberg-compatible cross-system composition. Any
success supports the sufficiency of that composition; it does not show that pART already contains
the complete motor/cellular rule.
