# EXP003 theory audit — before implementation

Status: **pre-implementation checkpoint**. No EXP003 simulation has been written or run. This
document is not a frozen protocol.

## Audit decision

The hard stop is **not triggered at the level of the local cortical learning mechanism**.
Grossberg and Versace's SMART model explicitly contains the required causal chain:

1. a learned higher-area expectation reaches lower-area layer-5 apical dendrites;
2. folded top-down feedback produces a modulatory on-center/off-surround at lower cells;
3. matched cells enter synchronous gamma resonance while mismatched cells are delayed or
   suppressed;
4. postsynaptically gated STDP changes bottom-up synapses onto the matched lower cells; and
5. those weights alter postsynaptic conductance and hence future cellular responses.

That is a defensible `T -> selective participation -> local W change -> future soma change`
mechanism. It is not an invented dendritic teaching rule.

The scope limitation is decisive. SMART specifies this mechanism for visual thalamocortical and
corticocortical learning. Grossberg's pART account specifies how a causal representation is
selected, maintained across delay, and reinforced, but it does not publish an equation-complete
mapping from such a representation to arbitrary BCI motor neurons. EXP003 can therefore test a
**pART-inspired + SMART-derived mechanism-level composition**. It cannot test "pART alone," and
success cannot establish that the exact BCI pathway already appears in published pART.

## What EXP002 established — and did not establish

The frozen EXP002 result at commit `bc2e46f` remains unchanged.

EXP002 established that:

1. delayed scalar reinforcement selected useful distributed motor hypotheses;
2. an outstar-derived local association learned structured top-down expectations from initially
   uninformative weights;
3. those expectations aligned to the hidden causal roles and adapted after remapping;
4. a direct-copy baseline produced almost the same instantaneous alignment;
5. a contextual bandit matched the pART-inspired selector's behavior;
6. the primary model failed the preregistered Francioni longitudinal residual criterion; and
7. suppressing top-down learning changed the top-down readout but not behavior.

The reason for item 7 is architectural: EXP002's top-down variable did not influence a plastic
lower circuit. It tested `representation -> patterned readout`, not
`representation -> feedback -> local plasticity -> future somatic change`.

## Primary-source reconstruction

### 1. SMART: an exact cell-local plasticity law

Grossberg and Versace (2008), Methods section 4.3, Equation 5, define synaptic plasticity as

\[
\frac{dw_{jk}}{dt}=
\lambda f_G(V_k,\bar g_{jk})
\left[
\bar g_{jk} f_N(V_k)(\widehat w-\check w)+w_0-w_{jk}
\right].
\]

Here `j` and `k` are the pre- and postsynaptic cells, `V_k` is the postsynaptic voltage,
`\bar g_{jk}` is a synaptic conductance factor, `w_0` is the uncorrelated baseline, and the
hat/check parameters bound the weight. Equation 6 defines the spike-timing gate `f_G` around the
postsynaptic spike. The paper states that the gate permits change only when pre- and postsynaptic
cells are simultaneously active.

The same Methods section states that `w_jk` changes postsynaptic channel density and thereby the
conductance and current caused by a later presynaptic spike. Thus the model explicitly closes

\[
\Delta W_{jk}\longrightarrow\Delta I_k^{future}\longrightarrow\Delta S_k^{future}.
\]

SMART uses two relevant variants:

- postsynaptic gating for lower LGN-to-layer-4 adaptive weights, allowing winning layer-4 cells
  to learn the presynaptic spatiotemporal pattern;
- dual-AND gating for top-down adaptive weights terminating in specific thalamus and layer-1
  apical dendrites, so an active higher source can sample an active lower pattern.

These are different synaptic populations and must not be conflated.

### 2. SMART: how top-down feedback selects which lower synapses learn

The causal route is a circuit effect, not an extra `T_i` factor inserted into Equation 5.

Grossberg and Versace report that top-down feedback is matched against bottom-up input and helps
stabilize learning in bottom-up filters and top-down expectations. In their Figure 6 simulation,
the winning lower cell spikes a few milliseconds after its LGN input, inside the STDP window.
The on-center/off-surround circuit suppresses or delays neighboring cells, reducing or eliminating
their learning. A sufficient match supports gamma synchrony; mismatch produces beta/reset and
disables the relevant STDP timing.

The published causal chain is therefore:

\[
T\to V_k\text{ and spike timing}\to f_G(V_k,\bar g_{jk})\to\Delta w_{jk}.
\]

No reward or hidden causal role appears in this local equation.

### 3. SMART: learned top-down input reaches apical dendrites

SMART section 2.4 states that V2 layer-6II-to-V1 layer-1 connections learn by correlating the
higher-cell output with retrograde spikes from active V1 layer-5 dendrites. Later, the learned
connection can prime the associated lower layer-5 cell. The lower cell recruits layer 6I, whose
folded feedback supplies the layer-4 modulatory on-center/off-surround.

This supports `learned expectation -> apical input -> lower attentional selection`. It does not
mean that the apical synapse is itself the lower bottom-up weight whose later response is measured.
EXP003 must keep `T`, the measured dendritic current `D`, and the plastic lower weight `W_lower`
separate.

### 4. Canonical laminar account

Grossberg (2021) reiterates that top-down attention alone is modulatory, that bottom-up plus
top-down convergence allows matched features to win against the inhibitory surround, and that
learning occurs at bottom-up and top-down adaptive pathways during feature-category resonance.
This supports the SMART circuit interpretation but does not add a motor-credit equation.

### 5. pART: structural and temporal credit, not neuron-wise derivatives

Grossberg (2018), section 3.19, assigns temporal credit to sustained working-memory storage of the
causal ensemble and structural credit to selection of relevant causes. Reinforcing feedback then
increases the probability that predictive chunks are chosen. Now-Print signals are described as
broadly broadcast modulators of learning, while motivated attention amplifies expected valued
representations.

This is sufficient to motivate scalar outcome-dependent selection and sustained eligibility of
`H`. It does not identify a hidden neuron-wise causal derivative and does not specify the exact
pART-to-BCI apical projection used below.

### 6. Complementary motor systems do not solve the forbidden problem for free

Gaudiano and Grossberg's VAM/aVITE family uses target-versus-present difference vectors to tune
motor maps and gains. That is a legitimate Grossberg mismatch-learning system, but its vector is
available from task geometry. It does not justify deriving arbitrary hidden `P+`/`P-` neuronal
roles from scalar reward without a vector. VAM-like learning is therefore not the primary EXP003
mechanism. Any motor-basis plasticity probe must be separately labeled and may not receive hidden
`c`.

## Classification of the proposed composition

| Component | Classification | Reason |
|---|---|---|
| SMART Equation 5/6 gated STDP | Grossberg-derived | The local law and spike-time gate are explicit in the primary model. |
| Match/gamma enables STDP; mismatch/beta/reset disables it | Grossberg-derived | Explicit SMART circuit principle and simulation. |
| Learned higher-to-lower expectation via layer-1/L5 apical route | Grossberg-derived | Explicit SMART dual-AND learning and folded-feedback circuit. |
| pART causal representation retained over delay and reinforced by scalar outcome | pART-inspired | The functional mechanism is published; EXP003 will be a reduced algorithmic abstraction, not full pART equations. |
| `H_{k,h}` joining an ART category with a motor hypothesis | Grossberg-compatible extrapolation | ART categories own expectations, but this exact BCI category-hypothesis conjunction is not published. |
| Mapping BCI motor channels to SMART-like lower adaptive synapses | Grossberg-compatible extrapolation | The local circuit principle is published in visual cortex; this target system mapping is new. |
| Discrete frame BCI, finite random motor basis, numerical exploration schedule | Engineering convenience | Required to make the question executable, not claims about Grossberg anatomy. |
| Contextual bandit, direct copy, generic reward-gated Hebb | Non-Grossberg controls | Deliberately simpler alternatives. |
| Hidden-role/vector-error controller | Non-Grossberg positive control | Receives forbidden information only to establish learnability. |

## Proposed mathematical variables

All causal roles `c_i` are environment-only except during offline analysis and the explicit positive
control.

- `o_t`: visible context, BCI state, target, and other permitted sensory information.
- `k_t`: ART category recruited and selected from complement-coded `o_t`; it is learned rather
  than a hard-coded A/B slot.
- `h_t`: selected distributed causal/motor hypothesis.
- `H_{k,h}(t)`: activity/working-memory trace of the selected category-hypothesis conjunction.
- `B_{h,i}`: presynaptic drive of fixed random motor hypothesis `h` to lower neuron `i`.
- `T_{k,h,i}`: learned higher-to-lower expectancy weight, initialized independently of `B` and
  `c`, and learned only from coactive higher and lower states during permitted resonance.
- `D_i(t)`: modeled apical/top-down current caused by the active `H_{k,h}` through `T_{k,h,i}`;
  it is recorded independently of motor drive.
- `V_i(t)`: lower-cell state resulting from motor/feedforward drive, existing lower weights, and
  modulatory on-center/off-surround feedback.
- `R(t)`: match/resonance state, including category match and the local bottom-up/top-down match;
  matched gamma permits appropriate spike timing, while reset/beta blocks it.
- `W_{h,i}^{lower}`: plastic lower synaptic efficacy from motor channel `h` to cell `i`. It
  determines later somatic response. It is shared across contexts; context dependence enters
  through selection of `h` and `T_{k,h}`. A category-indexed `W_{k,h,i}` would be an additional
  engineering extrapolation and is not the primary proposal.
- `S_i(t)`: somatic/output activity sent to the BCI environment.

## Proposed causal equations

The top-down expectation is emitted only by the active learned representation:

\[
D_i(t)=H_{k_t,h_t}(t)\,T_{k_t,h_t,i}.
\]

In a reduced folded-feedback abstraction, `D` changes the lower postsynaptic state through a
modulatory on-center/off-surround:

\[
V_i(t)=F\!\left(
W^{lower}_{h_t,i}B_{h_t,i},
\alpha[D_i(t)]_+,
-\beta\,\mathrm{surround}_i(D(t)),
\text{sensory drive},\text{noise}
\right).
\]

`D` is not a motor command and is not added directly to the BCI action. The lower weights change
only by a discrete integration of SMART's local law during a permitted resonant state:

\[
\Delta W^{lower}_{h_t,i}
=
\mathbf{1}[R(t)=1]\,\Delta t\,\lambda
f_G\!\left(V_i(t),\bar g_{h_ti}(t)\right)
\left[
\bar g_{h_ti}(t)f_N(V_i(t))(\widehat w-\check w)
+w_0-W^{lower}_{h_t,i}
\right].
\]

The future soma is then computed from the changed lower weight:

\[
S_i(t'>t)=G\!\left(W^{lower}_{h_{t'},i}B_{h_{t'},i},\text{other local inputs}\right).
\]

Implementation may use an explicitly validated discrete/trace approximation of `f_G`, but it may
not replace this route with `Delta error * action_i`, `reward * T_i`, or any neuron-indexed target.
The exact discretization must be documented and tested before development runs.

## Why this contains no hidden vector

`c_i`, `delta_i`, and `dE/dS_i` are absent from every primary-model expression. Neuron `i` changes
differently only because its independently initialized `B`, learned `T`, local voltage, pre/post
timing, and match state differ. Scalar reward can alter which `H` is retained and how often it is
selected; it must not be multiplied by a neuron vector in the local update.

Required boundary tests will fail if the main controller owns `c`, if any initial bank decodes `c`
above its permutation null, or if perturbing `c` while replaying the same observations/local states
changes a Grossberg-condition update.

## How `D_early -> Delta W -> Delta S` could arise

The mechanism predicts a mediated longitudinal relation, not merely instantaneous role alignment:

1. reinforcement makes a successful `H_{k,h}` recur;
2. its learned `T_{k,h}` produces cell-specific `D` before/during action;
3. `D` primes matched lower cells and suppresses competitors;
4. matched cells spike in the local STDP window during resonance;
5. their `W_lower` changes;
6. when the same `h` is evaluated later, changed `W_lower` changes soma even if hypothesis identity
   is held fixed.

EXP003 must test the mediation explicitly:

\[
D^{early}_{residual,i}\rightarrow
\Delta W^{lower}_i\rightarrow
\Delta S_i
\]

and must report changes within the same `h`, so hypothesis switching cannot manufacture the result.

## Context-specific expectation without hard-coded vector slots

Observable context and BCI state enter an ART category layer. Complement-coded category prototypes
compete; vigilance can accept a match, reset a mismatch, or recruit an uncommitted category. The
active learned category `k` and selected hypothesis `h` jointly activate `H_{k,h}` and therefore
read `T_{k,h}`.

Context A and B are not array indices supplied to `T`. They are observable inputs that may be
compressed into different learned categories. If ART learns separate categories and reinforcement
selects suitable hypotheses, the same lower cell may receive opposite `D_i` under two active
`T_{k,h}` rows. The primary lower weights remain indexed by motor channel rather than by declared
context; conditionality must be earned by category/hypothesis selection.

## Difference from the generic Hebbian control

The generic control uses the same environment, random basis, scalar reward, and opportunities, but
omits ART categories, vigilance, match/reset, learned expectations, folded feedback, and
resonance-dependent spike timing. A global scalar success gate consolidates the selected local
pre/post pattern using a standard bounded Hebbian update.

It therefore asks whether any reward-gated local consolidation is enough. If it matches the
primary model on behavior, remapping, longitudinal `D -> W -> S`, and ablation signatures, the
warranted result is Outcome B, not Grossberg-specific support.

## Proposed outcome criteria — not yet frozen

The logical criteria are fixed now; numerical cutoffs will be calibrated on development seeds and
committed before confirmatory seeds are instantiated. Candidate minimum effect floors below prevent
development calibration from choosing trivial thresholds:

1. **Behavior:** primary late success exceeds frozen and random by paired mean `>= 0.10`, with a
   seed-bootstrap 95% confidence interval above zero, before and after remap.
2. **No initial vector:** mean signed initial correlation of every `B`, `T`, and `W` bank with `c`
   is near zero; decoder accuracy must fall inside a preregistered 95% label-permutation interval.
3. **Expectation emergence:** selected `corr(T,c)` increases early-to-late by at least `0.20` and
   its bootstrap interval excludes zero; context-reversal expectations have opposition at least
   `0.25`.
4. **Synaptic longitudinal effect:** seed-level
   `corr(D_residual_early, W_late-W_early)` has mean at least `0.20` and a 95% interval above zero,
   both before and after remap.
5. **Somatic longitudinal effect:** the analogous `D_residual_early` to within-hypothesis
   `S_late-S_early` correlation has mean at least `0.20` and a 95% interval above zero.
6. **Mediation ordering:** `D` precedes `Delta W`, and `Delta W` precedes held-fixed-hypothesis
   `Delta S`; instantaneous `corr(D,c)` alone never passes.
7. **Causal specificity:** blocking `T -> local plasticity` reduces both longitudinal effects by
   at least `0.15` with paired 95% intervals above zero, while leaving immediate motor output
   matched at the perturbation onset.
8. **Expression separation:** post-learning apical suppression removes measured `D` but changes
   already-consolidated motor performance by no more than `0.05` in the immediate fixed-policy
   probe.
9. **Remap:** old alignment initially becomes inappropriate; late new alignment, `W`, and soma
   each improve toward the new causal mapping by at least `0.20` in their registered metrics.
10. **Specificity versus controls:** frozen, random, plain bandit, and direct-copy conditions fail
    the full `D -> Delta W -> Delta S` chain. Strong Outcome A additionally requires the generic
    Hebbian control to be materially weaker on the preregistered joint endpoint.
11. **Positive-control validity:** the explicit vector controller must pass behavior and both
    longitudinal endpoints, or the suite is non-diagnostic rather than evidence against the
    primary model.

After development, every threshold, window, aggregation rule, multiplicity decision, seed list,
source hash, and outcome classifier will be frozen in `FROZEN_PROTOCOL.json`. Until then no
confirmatory seed may be touched.

## Audit conclusion

Published SMART does contain a real top-down-controlled local-plasticity mechanism, so Outcome D
is not forced. But the proposed pART-to-SMART-to-BCI composition is partly a cross-system
extrapolation. EXP003 can legitimately test whether that composition is sufficient. It must not be
reported as an already-published pART solution to hidden cellular credit.

## Primary references

- Grossberg, S. & Versace, M. (2008). [Spikes, synchrony, and attentive learning by laminar
  thalamocortical circuits](https://doi.org/10.1016/j.brainres.2008.04.024), especially pp. 3,
  18–21, and Methods pp. 38–39 (Equations 5–6).
- Grossberg, S. (2018). [Desirability, availability, credit assignment, category learning, and
  attention](https://doi.org/10.1177/2398212818772179), especially sections 2.9 and 3.19.
- Grossberg, S. (2021). [A canonical laminar neocortical circuit whose bottom-up, horizontal, and
  top-down pathways control attention, learning, and prediction](https://doi.org/10.3389/fnsys.2021.650263),
  especially sections 3.1–3.6.
- Gaudiano, P. & Grossberg, S. (1991). [Vector associative maps: Unsupervised real-time error-based
  learning and control of movement trajectories](https://doi.org/10.1016/0893-6080(91)90002-M).
- Francioni, V. et al. (2026). [Vectorized instructive signals in cortical dendrites](https://doi.org/10.1038/s41586-026-10190-7),
  especially Figures 1, 5, Extended Data 11–15, and Methods.
