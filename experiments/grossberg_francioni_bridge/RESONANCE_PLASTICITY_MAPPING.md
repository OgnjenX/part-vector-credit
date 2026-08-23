# Resonance-to-plasticity mapping

“Learning during resonance” refers to several distinct learning sites. Treating them as one rule obscures the cellular-credit question.

## Three plasticity classes

| Class | Synapses that change | Local information | Role of resonance/mismatch | Reward input | Sign/magnitude content |
|---|---|---|---|---|---|
| A. Category/template learning | Bottom-up adaptive filter into a category and its top-down expectation/template | Active lower feature pattern, active category, match state | Match stabilizes a resonance in which category/template learning occurs; mismatch resets and searches. [Carpenter & Grossberg 1987](https://doi.org/10.1364/AO.26.004919) | Not intrinsically required for unsupervised ART category learning | Stores/coarsens the matched pattern; does not encode a behavioral derivative. |
| B. Top-down expectation learning | Higher category→lower feature/apical pathway | Coactive higher output and lower target/retrograde dendritic activity | SMART's dual-coincidence timing associates the higher category with an active lower pattern. [Grossberg & Versace 2008](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf) | Not part of the local SMART timing rule; pART reinforcement may select which H is active | Learns what pattern to expect. The origin of a behaviorally correct lower pattern remains crucial. |
| C. Lower adaptive-filter/STDP learning | Feedforward/local synapses onto lower neurons | Presynaptic conductance, postsynaptic voltage/spike timing, bounds/decay | Matching feedback changes timing and thereby plasticity; mismatch disrupts synchrony and may reset the category. SMART Eq. 5/6. | No reward or hidden causal role appears in Eq. 5/6 | Produces local potentiation/depression from timing, not directly from behavioral error. |

## Equation-level boundary

In SMART Equation 5, a local weight \(w_{jk}\) evolves as a function of presynaptic conductance, a postsynaptic voltage/timing gate, weight bounds, and decay. Equation 6 supplies the spike-associated postsynaptic gate. [Grossberg & Versace 2008](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf)

The important causal fact is:

\[
T \rightarrow V_k/\text{spike timing}\rightarrow f(V_k)\rightarrow \Delta w_{jk},
\]

not \(T_i\rightarrow\Delta w_i\) by direct assignment. EXP003a validated this reduced motif.

## What resonance determines

**SOURCE-DERIVED:** resonance determines which coherent representation remains active long enough for stable learning; feedback can change lower-cell gain and timing; mismatch can reset the active category.

**INFERENCE:** this is a strong account of *eligibility* or “who is allowed to learn.” It may indirectly affect sign and magnitude through the biphasic timing window, but those quantities are local consequences of spike timing—not values supplied by structural credit.

**NEW HYPOTHESIS:** arbitrary behavioral P+/P− role causes precisely the pre/post timing needed for the behaviorally appropriate signed future change in each cell.

## Does SMART predict gating or a smooth credit magnitude?

SMART's continuous dynamics permit graded effects, but its core match/mismatch contrast is often categorical: matched cells synchronize and learn; mismatched alternatives are suppressed/reset. The paper does not demonstrate that a smooth behavioral causal derivative is encoded in local update magnitude.

The frozen EXP003b post-hoc results are consistent with a sparse-gate reading:

- raw T and conductance-derived net top-down influence predicted local ΔW;
- top-down changed spike count in only about 1.7% of cell-frames;
- nonzero ΔW occurred in about 2.0% of cell-frames;
- roughly 93% of neuron weights were effectively unchanged;
- the confirmatory Francioni-style longitudinal residual endpoint remained near zero.

This is **diagnostic evidence about the reduced implementation**, not a claim that published SMART must be sparse at those parameter values. It suggests that the tested motif conveyed participation more reliably than a smooth role-proportional update.

## Where reinforcement can enter

pART/CogEM/Now Print can:

1. preserve the causal H across delay;
2. reinforce the H or its eligible associations;
3. increase the chance that H and its expectation recur;
4. modulate broadly which currently eligible synapses consolidate.

No cited Grossberg rule inserts scalar reward into SMART Eq. 5 as \(rT_i\). Doing so would be a new hybrid. Therefore a faithful bridge must show that selection and recurrence of H create appropriate local coactivity/timing without disguising a neuron-indexed teaching signal.

## Falsification logic

- If H/T determines which cells cross the timing gate but not the role-correct sign of ΔW, A4 fails for the Francioni explanation even though resonance learning remains intact.
- If ΔW changes future response under replay but the calcium residual does not track it, the plasticity bridge is intact and the measurement bridge fails.
- If learning remains equally role-specific when match/resonance is disrupted but reward and local activity are preserved, the proposed Grossberg-specific contribution is unnecessary.
