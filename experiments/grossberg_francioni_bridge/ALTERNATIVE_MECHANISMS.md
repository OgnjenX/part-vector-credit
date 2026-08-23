# Alternative cellular-credit accounts

This comparison identifies information requirements and discriminating predictions. Literature alone does not select a winner.

| Account | Information reaching cell/synapse | Local information | Global information | Graded sign/magnitude? | Selective gate? | Timing prediction | Context/remap prediction | L1/NDNF prediction |
|---|---|---|---|---|---|---|---|---|
| Explicit neuron-wise vector credit | A cell-indexed \(\delta_i\) or behavioral derivative | Activation and assigned \(\delta_i\) | Objective/outcome used to calculate vector | Yes, by construction | Optional | Usually strongest after target/error information is available, unless prospective error is predicted | Vector sign follows new causal derivative as soon as it can be estimated | No necessary L1 prediction without an anatomical implementation |
| Dendritic target/error propagation | Basal/apical compartments receive predictions/targets whose mismatch approximates an error | Compartmental voltage, local conductance, dendritic prediction error | Teaching phase or higher target | Often graded and signed | May include gating | Error tied to target/feedback phase; model-specific prospective components possible | Context changes apical target/error; can reverse rapidly if target mapping is known | Apical compartment is central; specific NDNF role depends on model. Examples: [Guerguiev et al. 2017](https://elifesciences.org/articles/22901), [Sacramento et al. 2018](https://papers.neurips.cc/paper/8089-dendritic-cortical-microcircuits-approximate-the-backpropagation-algorithm.pdf) |
| Generic reward-gated Hebbian plasticity | Selected/pre-post activity plus scalar reward | Pre/post coincidence | Scalar reward | Direction mainly from local correlation; reward supplies global valence | Yes | Eligibility can precede delayed outcome, consolidation follows reward | Relearning depends on exploration and new local correlations | No necessary L1 or top-down-expectation prediction |
| Eligibility trace + global neuromodulator | Local eligibility tag plus broadcast reward-prediction signal | Pre/post timing, decaying eligibility | Dopamine/reward prediction error | Can be signed through neuromodulator and timing, but not a supplied neuron-wise derivative | Strong | Local trace precedes delayed global outcome. [Izhikevich 2007](https://doi.org/10.1093/cercor/bhl152) | Relearns if new actions create distinct eligibility | No necessary NDNF dependence |
| Grossbergian representation/resonance selective plasticity | Category-specific learned expectation and match-dependent center/surround state | Pre/post conductance, voltage, timing | Structural/temporal causal representation, motivated attention, global reinforcement | Local rule is graded/biphasic, but behavioral sign/magnitude mapping is under-specified | Core prediction: resonance selects which pattern/synapses learn | Patterned expectation may be active before final outcome; reward reinforces eligible H; local timing occurs during match | Context categories should select different T; remapping may require search/new category before local change | Predicts dependence on relevant learned cortical feedback/apical match; NDNF identity is a new anatomical hypothesis |

## Information-complexity comparison

An explicit vector algorithm pays for cellular specificity by transporting \(N\) signed values. Eligibility-trace and reward-Hebbian schemes transport a scalar outcome but depend on neuron-specific local histories. The Grossbergian account transports a category identity plus a learned distributed expectation; its central burden is explaining how that expectation acquires the right arbitrary neuron-level topology.

This leads to a useful diagnostic:

\[
\text{Does role information appear first in }H/T,
\text{ or only after outcome in a cell-indexed apical residual?}
\]

- If it appears in T before action/outcome and depends on category/context, representation feedback is favored.
- If it appears only after error feedback with magnitude proportional to a causal derivative, explicit cellular-error accounts are favored.
- If scalar reward plus local eligibility explains the same D→W→S chain without match, vigilance, or T, the result is generic three-factor learning rather than Grossberg-specific.

## Shared predictions that do not discriminate

All five accounts can, with appropriate implementation:

- produce cell-specific changes;
- use delayed reward;
- adapt after remapping;
- show apical activity correlated with later soma;
- be disrupted by a broad manipulation that suppresses both dendrites and somatic firing.

Therefore behavioral success, instantaneous D–role correlation, and broad NDNF perturbation are insufficient alone. The discriminating variables are source, timing, information content, category dependence, and whether local plasticity requires match-specific top-down influence.

## Fair claim boundaries

- A Grossbergian simulation succeeding with A1–A6 shows sufficiency of that composition, not that published pART already entailed it.
- A vector-credit positive control succeeding shows task/analysis sensitivity, not biological truth.
- A generic Hebbian baseline matching the primary model demotes the result to generic feedback-gated learning.
- Failure of one pART+SMART composition falsifies that composition under its regime, not the families of ART, pART, or SMART models.
