# Primary-source audit: Grossberg–Francioni bridge

Status: theory analysis only. This stage does not change or rerun EXP000–EXP003b, and it does not introduce a cellular-credit mechanism.

## Evidence labels

- **SOURCE-DERIVED**: directly stated, modeled, or measured in the cited primary source.
- **INFERENCE**: a bounded interpretation of source-derived facts.
- **CROSS-SYSTEM EXTRAPOLATION**: combines mechanisms that Grossberg proposed in different architectures or anatomical systems.
- **NEW HYPOTHESIS**: required by the proposed Francioni explanation but not supplied by the cited theory.

For bridge arrows, `EXPLICITLY GROSSBERG-DERIVED`, `GROSSBERG-IMPLIED`, `CROSS-SYSTEM EXTRAPOLATION`, `GENERIC NEUROBIOLOGY`, and `NEW HYPOTHESIS` have their literal meanings. Compatibility with Grossberg is not authorship by Grossberg.

## A. What Francioni et al. require explaining

| Phenomenon | Primary-source result | Claim boundary |
|---|---|---|
| Arbitrary causal roles | **SOURCE-DERIVED.** Eight to ten imaged retrosplenial-cortex L5 neurons were randomly assigned to P+ and P−. The difference of their mean activities controlled a seven-position visual grating; reward followed reaching the target. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | The learner was not given an anatomical P+/P− label. This creates a hidden, experimenter-defined causal mapping. |
| Longitudinal somatic change | **SOURCE-DERIVED.** P+ and P− had similar initial transient frequencies, then differentiated across training: P+ maintained activity while P− was downregulated. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | This establishes role-related change, not the unique learning algorithm that caused it. |
| Soma-conditioned dendritic signal | **SOURCE-DERIVED.** The paper fit coincident dendritic event magnitude from somatic event magnitude and analyzed the signed somato-dendritic residual: positive residuals denote dendritic amplification and negative residuals attenuation. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | The residual is an observation statistic, not identical to membrane voltage, synaptic current, calcium influx, or a mathematical gradient. |
| Opponent, causal-role structure | **SOURCE-DERIVED.** During epochs in which task error decreased, P+ and P− residuals changed in opposite directions; the pattern reversed with the neuron's task role. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | The authors relate this to an error derivative. They do not establish that the signal equals \(\partial E/\partial y_i\) or a backpropagated gradient. |
| Timing relative to outcome | **SOURCE-DERIVED.** Residual activity carried task-outcome information both before and after final outcome; pre-outcome activity weakly decoded successful versus unsuccessful trials. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | A purely post-reward account is incomplete. Pre-outcome information is compatible with expectation, evolving sensory feedback, recurrent state, or prospective teaching; timing alone does not choose among them. |
| Early signal predicts later change | **SOURCE-DERIVED.** Cell-specific dendritic residuals early in learning were associated with later neuron-specific activity changes. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | The paper explicitly leaves open how much the signal is moment-to-moment modulation versus an instruction for synaptic change. Association is not a demonstrated synaptic update equation. |
| Layer-1 NDNF+ involvement | **SOURCE-DERIVED.** Activating L1 NDNF+ interneurons reduced dendritic residual/event measures, abolished task/reward-related and vectorized residual structure, and impaired learning. It also substantially reduced somatic event rates. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | This is causal evidence for the pathway, but not a compartment-selective manipulation. It does not identify SMART's modeled inhibitory surround with NDNF circuitry. |
| Remapping | **SOURCE-DERIVED.** The reported longitudinal experiment retained the assigned P+/P− roles across training. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7) | Hidden-role reversal and multi-context remapping are discriminating future tests, not reported empirical facts. |

The minimum target is therefore not “a gradient.” It is a neuron-specific, opponent, task-role-related apical calcium statistic, linked longitudinally to later somatic change and causally sensitive to a layer-1 manipulation.

## B. What Grossberg actually provides

### pART: representation-level structural and temporal credit

**SOURCE-DERIVED.** pART describes temporal credit as maintaining the relevant event representation across a delay, and structural credit as selecting causally relevant features among competing representations. Dorsolateral prefrontal working memory, competition, reinforcement, motivated attention, and basal-ganglia gating support this process. Match supports resonance and learning; mismatch triggers arousal, reset, and search. [Grossberg 2018](https://doi.org/10.1177/2398212818772179)

**SOURCE-DERIVED.** CogEM/MOTIVATOR-style sensory–amygdala–orbitofrontal interactions provide conditioned reinforcement and incentive motivation; “Now Print” reinforcement is a broadly distributed modulatory signal that can strengthen or weaken eligible associations. [Grossberg 2018](https://doi.org/10.1177/2398212818772179)

**Claim boundary.** pART identifies and maintains a causal representation. It does not specify a neuron-wise derivative for an arbitrary experimenter-defined subset of RSC L5 cells. A global reinforcement signal plus an eligible representation is not, by itself, the map \(H_j\rightarrow T_{j,i}\) required here.

### ART: category-owned learned expectations

**SOURCE-DERIVED.** ART categories learn bottom-up adaptive filters and top-down expectations. A sufficiently close bottom-up/top-down match supports resonance and stabilizes learning; mismatch resets the active category and initiates search. [Carpenter & Grossberg 1987](https://doi.org/10.1364/AO.26.004919), [Grossberg 2018](https://doi.org/10.1177/2398212818772179)

**SOURCE-DERIVED.** Grossberg's outstar principle lets an active source representation learn the distributed pattern coactive at its targets. The original outstar is associative and normalized; it is not a neuron-indexed behavioral error. [Grossberg 1972](https://sites.bu.edu/steveg/files/2016/06/Gro1972MathBioSci_I.pdf)

**Claim boundary.** Category-owned patterned expectations are explicit in ART. It is **CROSS-SYSTEM EXTRAPOLATION** to identify a pART-selected causal representation with the higher category that owns a SMART feedback expectation onto the exact RSC BCI neurons.

### SMART: laminar match, learned top-down feedback, and local timing plasticity

**SOURCE-DERIVED.** SMART models a visual LGN–V1–pulvinar–V2 circuit. Higher cortical layer 6II projects to lower layer 1, where it contacts apical dendrites of layer-5 cells, and to specific thalamus. Folded layer-5/6 feedback creates a modulatory on-center/off-surround at lower representations. [Grossberg & Versace 2008](https://doi.org/10.1016/j.brainres.2008.04.024)

**SOURCE-DERIVED.** The higher-to-lower pathway can learn an expectation using a dual-coincidence timing rule: higher output and retrograde dendritic spikes associated with an active lower L5 pattern jointly support the top-down synapse. Learned feedback later primes the associated lower population. [Grossberg & Versace 2008](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf)

**SOURCE-DERIVED.** SMART Equation 5 changes a local synaptic weight using presynaptic conductance, postsynaptic voltage/timing gates, bounds, and passive decay. Equation 6 defines the spike-associated voltage gate used by that local rule. Matching feedback changes membrane/spike timing; mismatch changes synchrony and supports reset. [Grossberg & Versace 2008](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf)

**Claim boundary.** SMART supplies a concrete local arrow from matched state through timing to plasticity in a sensory hierarchy. It does not show that scalar BCI success trains arbitrary, intermingled P+/P− signs, nor that its off-surround is the NDNF-mediated signal measured by Francioni.

### Canonical laminar extension

**SOURCE-DERIVED.** Grossberg's canonical laminar account generalizes higher-layer-6 to lower-layer-1 feedback, a lower L5→L6→L4 folded loop, and a modulatory on-center/off-surround. Top-down excitation alone is balanced by inhibition; combined bottom-up and matching top-down input selectively enhances matched cells. [Grossberg 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8102731/)

**Claim boundary.** This argues that the circuit motif may recur across cortex. It does not anatomically establish the precise higher source, targets, or learned topology in the Francioni RSC preparation.

### Complementary motor mismatch systems

**SOURCE-DERIVED.** VAM/aVITE motor models learn transformations using an explicitly represented target-position difference vector and local adaptive pathways. [Gaudiano & Grossberg 1991](https://doi.org/10.1016/0893-6080(91)90002-M)

**Claim boundary.** These models show that Grossberg assigns fine control to complementary systems rather than ART category weights alone. But their observable geometric difference vector does not solve inference of arbitrary hidden P+/P− roles from scalar reward. Importing it would change the information available in the Francioni problem.

## System-by-system inventory

| Mechanism | Original architecture/system | What it supplies | What it does not supply here |
|---|---|---|---|
| Structural/temporal credit, working memory | pART/prefrontal cognitive-emotional circuit | Chooses and maintains a causal representation across delay | Neuron-resolved RSC role derivative |
| Conditioned reinforcement, incentive motivation, Now Print | CogEM/MOTIVATOR/basal ganglia compositions in pART | Global/representation-selective reinforcement and action release | Arbitrary cellular sign topology |
| Category competition, vigilance, reset/search | ART | Stable hypothesis selection and mismatch-driven search | The correct P+/P− pattern unless that pattern is learnable/available |
| Learned top-down expectation/outstar | ART; SMART visual hierarchy | A category-owned distributed lower-level expectation | Proof that pART's causal H owns the relevant RSC expectation |
| Laminar on-center/off-surround | SMART/canonical cortical circuit | Match-selective enhancement and competitor suppression | A demonstrated NDNF or signed behavioral-credit mapping |
| Equation 5/6 local timing plasticity | SMART visual adaptive filters | Timing-dependent local weight change and future response | Behavioral sign/magnitude assignment from scalar reward |
| Difference-vector motor learning | VAM/aVITE | Fine adaptive control when a target vector is explicitly represented | Discovery of hidden BCI cellular roles |

## Audit conclusion

**INFERENCE.** Grossberg provides most *types* of components in the proposed chain: representation selection, delayed credit, learned expectations, laminar feedback, match-dependent timing, and local plasticity. Published theory does not provide their complete binding for this task.

**NEW HYPOTHESIS.** The central missing content is that a pART-selected causal representation can learn a sufficiently fine, context-specific feedback topology onto arbitrary intermingled RSC neurons, and that the resulting center/surround dynamics determine the behaviorally correct direction—not merely permission—of lasting cellular change.

## Primary sources

- Francioni et al. (2026), *Vectorized instructive signals in cortical dendrites during learning*. [Nature article and Methods](https://www.nature.com/articles/s41586-026-10190-7).
- Grossberg (2018), *Desirability, availability, credit assignment, category learning, and attention*. [Brain and Neuroscience Advances](https://doi.org/10.1177/2398212818772179).
- Grossberg & Versace (2008), *Spikes, synchrony, and attentive learning by laminar thalamocortical circuits*. [Brain Research](https://doi.org/10.1016/j.brainres.2008.04.024); [author-hosted PDF](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf).
- Grossberg (2021), *A path toward explainable AI and autonomous adaptive intelligence*. [Frontiers in Neurorobotics](https://pmc.ncbi.nlm.nih.gov/articles/PMC8102731/).
- Carpenter & Grossberg (1987), *ART 2: self-organization of stable category recognition codes for analog input patterns*. [Applied Optics](https://doi.org/10.1364/AO.26.004919).
- Grossberg (1972), *A neural theory of punishment and avoidance, I: qualitative theory*. [Author-hosted PDF](https://sites.bu.edu/steveg/files/2016/06/Gro1972MathBioSci_I.pdf).
- Gaudiano & Grossberg (1991), *Vector associative maps: unsupervised real-time error-based learning and control of movement trajectories*. [Neural Networks](https://doi.org/10.1016/0893-6080(91)90002-M).
