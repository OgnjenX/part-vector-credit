# Cellular sign analysis

## Four different meanings of “sign”

The proposed bridge contains four signs that are not interchangeable:

1. **Behavioral causal sign:** increasing cell \(i\) moves the BCI state toward or away from target.
2. **Circuit-current sign:** top-down excitation depolarizes a target; recruited inhibition hyperpolarizes or shunts it.
3. **Plasticity sign:** a local synapse potentiates or depresses according to conductance, voltage, and pre/post timing.
4. **Measurement sign:** a dendritic event is amplified or attenuated relative to a soma-conditioned prediction.

Francioni directly establishes (1) by task assignment and observes role-related structure in (4). The hypothesis must supply credible arrows through (2) and (3); equality among these signs cannot be assumed.

## What the Grossberg circuit naturally supplies

**SOURCE-DERIVED.** In ART/SMART, a learned expectation supplies a focused on-center and a broader inhibitory off-surround. Feedback alone is modulatory; matching bottom-up input plus the center selectively enhances matched cells, while the surround suppresses competitors. [Grossberg & Versace 2008](https://doi.org/10.1016/j.brainres.2008.04.024), [Grossberg 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8102731/)

This naturally supplies a relative opponent computation:

\[
I_i^{TD}=I_{i,\mathrm{center}}^{exc}-I_{i,\mathrm{surround}}^{inh}.
\]

But its neuron specificity is inherited from the learned/topographic expectation and the geometry of competition. The circuit does not infer that an arbitrary intermingled cell is P+ or P−. Thus center/surround is an *expression mechanism* for a signed pattern, not yet an account of how the hidden sign pattern was discovered.

## “Who may learn?” versus “how should it change?”

| Question | Grossberg support | Limitation for Francioni |
|---|---|---|
| Which representation is eligible? | **SOURCE-DERIVED.** Match, resonance, motivated attention, working-memory causal traces, and reinforcement select an eligible representation. | This is structural/temporal credit at category or active-pathway scale. |
| Which lower cells participate? | **SOURCE-DERIVED.** Learned expectations and on-center/off-surround favor matched lower populations and suppress competitors. | Requires T already to have the relevant cell topology. |
| Does a local synapse change? | **SOURCE-DERIVED.** SMART Eq. 5/6 uses local presynaptic conductance and postsynaptic voltage/spike timing. | Match can create a plasticity gate without encoding behavioral derivative magnitude. |
| In which direction and by how much? | **GROSSBERG-IMPLIED** only insofar as the biphasic timing rule yields potentiation or depression from local timing. | **NEW HYPOTHESIS:** behavioral P+/P− sign must reliably produce the needed timing sign and magnitude. This mapping is not supplied by scalar reward alone. |

**INFERENCE.** Published SMART most clearly predicts selective, timing-dependent participation in learning. It can yield graded local weights because Eq. 5 is continuous and bounded, but it does not establish that the gradient of a behavioral objective is represented by that magnitude.

## Is the surround sufficiently specific?

SMART's surround suppresses alternatives defined by its visual/topographic representation. The Francioni populations are experimenter-assigned, intermingled cells. A broad spatial surround could suppress nearby P+ and P− cells indiscriminately. To explain the data, the effective surround must instead be patterned by learned feature/category connectivity at near-cell resolution.

That requirement is **NEW HYPOTHESIS A2/A3**, not a consequence of the phrase “off-surround.” Quantitative anatomical and functional mapping is required.

## Does SMART predict potentiation and depression?

**SOURCE-DERIVED.** SMART's local rule is timing/voltage dependent and contains both weight growth and decay/bounding terms. Different timing can therefore produce different signed weight changes. [Grossberg & Versace 2008](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf)

**INFERENCE.** A matched center is likely to increase the probability of a postsynaptic event inside the plastic window; a competitor may instead miss the window. This robustly predicts “more versus less learning.” It does not, without further timing structure, guarantee “potentiate P+ and depress P− in proportion to causal benefit.”

This is consistent with the frozen evidence:

- EXP003a validated a supplied match → timing → local plasticity → future-response motif.
- EXP003b post-hoc found raw T/net top-down state predicted sparse ΔW, but the data did not establish a smooth cell-wise T → ΔW magnitude law or the confirmatory dendritic-residual longitudinal endpoint.

Those findings test one reduced local transform. They neither prove nor disprove SMART outside that implementation.

## Discriminating sign measurements

A decisive study should measure, in the same cells and trials:

1. learned higher-source axon activity;
2. distal apical excitatory current;
3. NDNF-mediated/local inhibitory current;
4. net voltage and spike/plateau timing;
5. local synaptic potentiation/depression;
6. later somatic change;
7. the published calcium residual.

If causal role is present in T but absent in current/timing, A3 fails. If present in timing but absent in ΔW sign, A4 fails. If present through ΔW and future soma but absent in the residual, A6—not cellular credit—is the limiting bridge.
