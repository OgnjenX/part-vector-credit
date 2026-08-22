# EXP001 theory-to-code mapping

This repository uses **pART-inspired mechanism-level abstraction**, never “a pART
implementation” or “SMART implementation.”

| Grossberg source | Theoretical role | EXP001 implementation | Known simplification / information limit |
|---|---|---|---|
| Grossberg (2018), §§3.19–3.20 | structural credit selects relevant causal features; temporal credit maintains their ensemble until feedback | selected hypothesis ID stored across distractors | discrete ID trace, not DLPFC Item-Order-Rank shunting dynamics |
| Grossberg (2018), §§2.2–2.3 | unexpected reward/non-reward evokes broad dopaminergic Now Print modulation | delayed scalar improvement gates value association for the active trace | bandit-style scalar association; not MOTIVATOR/BG equations |
| Grossberg (2018), CogEM/MOTIVATOR | incentive motivation amplifies task-relevant representations | reward-predictive hypothesis value scales top-down gain | no amygdala, OFC, LH, drive, or deprivation dynamics |
| Grossberg & Versace (2008) | top-down modulatory on-center/off-surround matching; resonance gates learning; mismatch causes reset/search | context prototype match, vigilance, candidate rejection, and uncommitted category recruitment | rate/discrete categories; no laminae, thalamus, spikes, ACh, gamma/beta, or STDP |
| Grossberg (2021), canonical circuit | bottom-up/horizontal/top-down pathways coordinate attention, prediction, working memory, and category learning | distinct observable context, category, top-down control, and outcome stages | functional decomposition only; no canonical laminar equations |
| Grossberg top-down attention plus observable task mismatch | selected feedback can be modulated by a global task-state change | scalar visual error change multiplies the selected feedback pattern in the dendritic measurement proxy | engineered composition; no published equation was found that derives this exact dendritic signal |
| Grossberg (2018), Masking Fields | predictive chunks compete; reinforcement increases probability of choosing successful chunks | random distributed control hypotheses compete by learned scalar value | patterns are engineered random motor hypotheses, not learned list chunks |
| Gaudiano & Grossberg (1991); Grossberg (2016) | VAM/aVITE motor mismatch learning calibrates sensory–motor vector maps using a difference vector | **not in Grossberg-only condition**; discussed as a boundary | the required neuron/motor-coordinate difference vector is not available from scalar BCI outcome |
| Grossberg outstar/spatial-pattern learning tradition | an active source can learn a distributed output pattern | optional plastic-basis probe consolidates its own executed soma pattern under a global gate | cannot rotate toward hidden causal signs; engineering probe, not evidence of de novo causal credit |
| none (non-Grossberg positive control) | demonstrate learnability with cellular credit | explicit hidden causal vector updates neuron-wise control weights | intentionally violates EXP001 information boundary |

## Theoretical assessment before simulation

The primary sources specify how an active causal representation can remain eligible
for later global reinforcement and how a predictive representation can win future
competition. They do not specify how scalar BCI outcome identifies the arbitrary,
experimenter-assigned causal sign of each neuron inside that representation.

Grossberg's complementary motor models do specify fine-grained vector mismatch
learning, but they assume an explicit target-versus-present difference vector in
the coordinates being calibrated. In EXP001, global visual error is observable;
the derivative mapping from each neuron's activity to that error is hidden. Treating
global error as though it were already routed with the correct neuron-specific sign
would reproduce the very credit signal under investigation.

Thus the scientifically defensible Grossberg-only route tested here is selection
from a pre-existing random distributed basis. Success supports hypothesis routing;
failure does not falsify the full biological theory, but identifies an unspecified
link between pART-level credit and cellular parameter change.

## Primary references

- Grossberg, S. (2018), *Brain and Neuroscience Advances*.
  https://doi.org/10.1177/2398212818772179
- Grossberg, S. & Versace, M. (2008), *Brain Research*.
  https://doi.org/10.1016/j.brainres.2008.04.024
- Grossberg, S. (2021), *Frontiers in Systems Neuroscience*.
  https://doi.org/10.3389/fnsys.2021.650263
- Gaudiano, P. & Grossberg, S. (1991), *Neural Networks*.
  https://doi.org/10.1016/0893-6080(91)90002-M
- Francioni, V. et al. (2026), *Nature*.
  https://doi.org/10.1038/s41586-026-10190-7
