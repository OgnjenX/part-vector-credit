# EXP003b theory-to-code mapping

## Claim boundary

EXP003b is a **pART-inspired + SMART-derived mechanism-level composition**. It is
not a full pART or SMART implementation. The experiment asks whether the already
validated EXP003a local motif can connect a learned top-down expectation to later
cellular change in a delayed, remapped BCI task. It cannot establish that this
exact cross-system composition appears in Grossberg's published architecture.

The historical EXP003 audit is preserved. One notation error there must not be
propagated: SMART Equation 6 defines the post-spike signal `f_N`, not `f_G`.
EXP003a's source reconstruction and code use this corrected reading.

## Source → mechanism → implementation → simplification

| Classification | Primary source and mechanism | Role | EXP003b implementation | Limitation |
|---|---|---|---|---|
| Grossberg-derived | [Grossberg & Versace 2008](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf), Eq. 5/6 and matched timing | Local bounded, spike-timing-dependent lower-synapse learning | The unchanged EXP003a `equation5_update` is evaluated on Brian2-generated pre/post histories in `spiking_cache.py`; runtime lookup receives only local drive, weight, top-down state and reset state | SMART-derived reduced STDP: EXP003a uses `f_N²` as a reduced local gate, not the full compartmental voltage implementation |
| Grossberg-derived | Grossberg & Versace 2008 top-down modulatory on-center/off-surround | Make matched lower cells spike in the plasticity window while competitors/reset states do not | Explicit Brian2 top-down center, spiking surround interneuron and spiking reset interneuron are tabulated over the full local input grid | A cached two-cell motif replaces the full laminar/thalamic network; nearest-grid evaluation is an engineering approximation |
| Grossberg-derived | ART top-down expectancy/outstar learning, summarized in [Grossberg 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7330174/) | An active resonant category samples a coactive distributed lower pattern | `T[k,h] += eta * source_gain * eligibility * (centered_soma - T[k,h])` | Discrete outstar abstraction; the BCI lower population is an extrapolated target system |
| pART-inspired | [Grossberg 2018](https://journals.sagepub.com/doi/10.1177/2398212818772179), structural/temporal credit, motivated attention and Now-Print reinforcement | Preserve the chosen causal representation across distractors and reinforce it after delayed scalar outcome | ART category × motor-hypothesis trace; decaying working-memory eligibility; scalar outcome updates `Q[k,h]`; positive value scales top-down source gain | Tabular reinforcement and eligibility replace the interacting PFC, amygdala, basal-ganglia and motivational circuits |
| Grossberg-derived principle | ART complement coding, choice, vigilance, reset and uncommitted-category recruitment | Represent observable context/state and search after mismatch | Complement-coded visible observation prototypes; vigilance 0.88; choice/reset loop; up to 18 categories | Fuzzy-ART-style abstraction, not SMART laminar search equations |
| Grossberg-compatible extrapolation | Composition of ART category-owned expectations with SMART lower plasticity | Test `H[k,h] → T[k,h] → timing → W_lower → future soma` | Context/category-specific `T[k,h,i]`; hypothesis-specific, context-shared `W_lower[h,i]` | No primary source specifies this exact pART-to-arbitrary-BCI-neuron projection |
| Engineering convenience | Finite random motor repertoire and closed-loop BCI | Provide hidden causal directions without leaking them to the learner | Independent antithetic random motor basis; three action frames with visual state returned after every frame | Antithetic pairs guarantee repertoire symmetry and make this a basis-selection test, not de novo discovery of arbitrary neuronal signs |
| Non-Grossberg control | Contextual bandit | Test whether `Q(context,state,h)` suffices | Same motor bank, exploration, delay and scalar outcome | Algorithmic baseline |
| Non-Grossberg control | Direct selected-pattern copy | Test generic routing | Copy centered selected motor vector into measured apical readout, with no SMART influence or local plasticity | Deliberately minimal confound baseline |
| Non-Grossberg control | Scalar-gated local Hebbian consolidation | Test generic feedback-gated learning | Successful selected soma locally changes `W_lower` without ART match, expectancy or SMART timing | Reward gates a vector-valued local update; included only as a comparator |
| Non-Grossberg positive control | Hidden neuron-wise causal vector | Validate task and longitudinal analysis | Only this isolated condition receives `c_i`, changes its motor vector/weights toward `c`, and adds `error_improvement*c` at sensory feedback | Forbidden information; never shared with primary or ablation conditions |

## What is and is not supplied

Every non-positive-control learner may observe visible context, current continuous
BCI state/error, target, category match, scalar improvement and reward. It never
receives `c_i`, `dE/dy_i`, or an equivalent neuron-indexed target. Hidden causal
roles are used only by the environment and offline analysis.

The proposed pathway is therefore locally lawful:

\[
T_{k,h}\rightarrow V_i,\,t_i^{post}\rightarrow \Delta W_{h,i}
\rightarrow S_i^{future}.
\]

However, scalar outcome selects/reinforces `H[k,h]`; it does not enter SMART
Equation 5/6. Top-down learning samples the executed centered soma regardless of
the sign of outcome. This is a stringent test of whether representation selection
plus resonant local timing contains enough information by itself.

## Francioni interpretation boundary

[Francioni et al. 2026](https://www.nature.com/articles/s41586-026-10190-7)
conditioned dendritic activity on soma/network state, related the residual to
task-error change and later somatic plasticity, and causally perturbed the layer-1
pathway. Their paper does not by itself decide whether the signal is a propagated
gradient or a learned patterned expectation. EXP003b mirrors that logic at an
abstract computational level; it does not reproduce their anatomy, calcium
measurement process, or optogenetic intervention exactly.
