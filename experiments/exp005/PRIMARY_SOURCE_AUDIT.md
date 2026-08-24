# EXP005 primary-source audit

Status: **SOURCE AUDIT / PRE-IMPLEMENTATION**  
Decision: **Outcome E — no Grossberg-explicit or Grossberg-derived-composition
candidate was found for the missing operation.**

## Question and decision rule

EXP005 asks whether a published Grossberg mechanism can change an initially
uninformative projection onto arbitrary retrosplenial-cortex (RSC) neurons using
only scalar behavioral consequence and locally available neural variables. A
candidate had to specify all of the following:

1. neuron-varying exploration or another neuron-varying eligibility;
2. a temporal bridge from that local variable to delayed outcome;
3. an outcome-dependent synaptic update;
4. bidirectional or opponent changes sufficient for arbitrary hidden signs; and
5. no hidden role, neuron-wise target, motor-error vector, or equivalent teacher.

The audit found Grossberg mechanisms for each *adjacent* function, but not a
published rule that composes them into the required local scalar-outcome credit
operation. In particular, combining an Endogenous Random Generator (ERG), scalar
reward, and outstar learning would still require a new synapse-specific operation
such as covariance between each local perturbation and reward. That operation is
not in the audited equations.

## Audited primary mechanisms

| Candidate | Source and exact mechanism | Information used | What it learns | Classification for EXP005 |
|---|---|---|---|---|
| ART category/template learning | Carpenter & Grossberg (1987), ART 2; Grossberg's ART learning laws. Resonance gates bottom-up and top-down adaptive weights; mismatch invokes reset/search. | Current feature pattern, category activity, match/vigilance state. | Stable recognition categories and expectations that sample presented features. | **GROSSBERG-EXPLICIT**, but it stores/categorizes active patterns; scalar reward does not identify arbitrary RSC neuron signs. |
| pART structural/temporal credit | Grossberg (2018), especially the pART circuit discussion of maintained causal representations, motivated attention, reinforcement, and Now Print-like timing. | Selected/maintained representations, outcomes, motivational signals. | Which representation or event is credited and reinforced across a delay. | **GROSSBERG-EXPLICIT** at representation level; no neuron-resolved RSC projection rule is specified. |
| CogEM conditioned reinforcement and incentive motivation | Grossberg & Seidman (2006), Fig. 4 and Appendix B. Conditioned-reinforcer weight: Eq. B4, a sensory-activity-gated trace tracking drive activity. Spectral timing: Eq. B8, local sampling signal `g_ij` makes `z_ij` approach the global Now Print signal `N`. | Presynaptic/sampling activity plus drive or Now Print activity. | Cue value, incentive motivation, and temporal prediction of reinforcement. | **GROSSBERG-EXPLICIT**. Local sampling differentiates timing channels, not causal contributions of simultaneously perturbed RSC neurons. |
| SOVEREIGN exploration and plan reinforcement | Gnadt & Grossberg (2008), Secs. 2.3, 2.5.7 and Appendix. ERG releases exploratory head/body movements; Eqs. 62/65 gate outstar/instar learning to winning motivational channels; reward reinforces stored plan items. | Random action release, active plan/category, drive/reward state, concurrent target representation. | Exploration, goal-oriented sequence/plan selection, conditioned reinforcement. | **GROSSBERG-EXPLICIT** for exploration and representation-level reinforcement. The ERG generates action choices/vectors; no equation correlates per-neuron ERG variation with scalar reward. |
| SOVEREIGN planned motor-map learning | Gnadt & Grossberg (2008), Eqs. 70–81 and 117–118. VAM weights are gated by GO/onset terms and learn by reducing explicit NET/difference activity. | Source activity, target/NET or mismatch activity, GO gate. | Spatial-to-motor and planned-to-reactive mappings. | **GROSSBERG-EXPLICIT**, but the neuron-specific teacher is a signed mismatch/difference representation, not scalar reward alone. |
| VAM/aVITE | Gaudiano & Grossberg (1991). The ERG samples workspace vectors; a copy of present position supplies target coordinates; a Difference Vector is the error that VAM learning zeros. | Local source activity plus neuron-resolved present/target difference; phase gate. | Sensory–motor maps and movement calibration. | **GROSSBERG-EXPLICIT** motor construction, but inapplicable to the clean BCI boundary because it requires the missing vector-valued teacher. |
| VITE/FLETE | Bullock & Grossberg (1991). Target Position Command minus Present Position Command forms a Difference Vector, gated by GO signals. | Explicit desired and present state vectors. | Trajectory generation and postural control. | **GROSSBERG-EXPLICIT** control dynamics, not scalar-reward topology learning. |
| Adaptive saccade outstar | Grossberg et al. (1997), Eq. 11: `dz_ij/dt = alpha n(X_i)[p(P_k G_{k-j}) - z_ij]`. The active source gates learning; each weight tracks a visually reactive peak-decay teaching pattern. | Source activity plus a distributed postsynaptic teaching signal. | Alignment of multimodal/planned and reactive spatial maps. | **GROSSBERG-EXPLICIT** distributed map learning; it requires a neuron-indexed target pattern and therefore cannot be the clean primary rule. |
| Classical outstar/instar | Grossberg (1986) and SOVEREIGN Eqs. 62/65. An active source samples a coactive target; weights move toward that target. | Presynaptic/category activity and postsynaptic target activity; optional global gate. | Associative expectation/storage of a concurrently active distributed pattern. | **GROSSBERG-EXPLICIT** storage. It can consolidate a useful pattern only after another process has produced that pattern; it does not evaluate each cell's causal contribution. |
| SMART lower adaptive filter/STDP | Grossberg & Versace (2008), Eqs. 5–6 as independently validated in EXP003a. Presynaptic conductance and postsynaptic voltage/spike timing determine a local plasticity gate under match/mismatch dynamics. | Pre/post local state and spike timing; top-down match changes those states. | Match-selective lower synaptic plasticity and future response. | **GROSSBERG-EXPLICIT** local plasticity. It selects which active synapses learn; it does not infer the arbitrary sign of each neuron's BCI contribution from scalar reward. |
| Cerebellar adaptive filtering | Contreras-Vidal, Grossberg, & Bullock (1997). Parallel-fiber activity is adjusted through climbing-fiber/error-related signals to compensate movement dynamics. | Distributed state basis plus error/correction channel. | Predictive motor compensation. | **GROSSBERG-EXPLICIT** motor learning, but requires a structured error/correction input rather than only scalar success. |
| SOVEREIGN2 system integration | Grossberg (2019), SOVEREIGN2 roadmap integrating pART, navigation, action, emotion, and reinforcement systems. | Multiple modeled subsystem signals. | Systems-level autonomous behavior. | **GROSSBERG-IMPLIED integration**, but the article describes a roadmap and does not add the missing neuron-level scalar-reward rule. |

## The candidate composition requested in EXP005

The most favorable source-based composition is:

```text
active H
  -> adaptive H-to-RSC projection
  -> ERG-like exploratory variation
  -> behavior and scalar reward
  -> pART temporal/structural credit keeps H eligible
  -> outstar consolidates a postsynaptic RSC pattern
```

The sources provide `H` selection/maintenance, ERG exploration, delayed
representation-level credit, and outstar storage. They do **not** provide the
essential arrow:

```text
(local exploratory deviation xi_i, delayed scalar outcome R)
    -> signed local eligibility/update for H-to-RSC synapse i.
```

An equation such as

`Delta A_Hi = eta (R - baseline) xi_i`

would solve the information problem in principle, but it is generic node
perturbation / a three-factor policy-gradient estimator. It is **GENERIC
BIOLOGICAL / ML CONTROL** under the preregistered classification, not a
Grossberg-derived rule. Multiplying an outstar target by reward would have the same
problem unless a source specifies why its neuron-varying target is an unbiased
causal estimator. None of the audited sources does.

## Why nearby Grossberg mechanisms are insufficient

- **Reward and Now Print are scalar/global gates.** They can mark *when* and *which
  representation* learns. Alone they cannot make two simultaneously active RSC
  synapses update in opposite causal directions.
- **Outstars inherit their spatial information from the sampled target.** They can
  denoise or average multiple target patterns, but the learner still needs a legal
  process that makes successful target coordinates systematically different for
  hidden P+ and P- neurons.
- **ERG supplies variation, not its credit assignment.** In SOVEREIGN/aVITE it
  explores actions or workspace vectors. The adaptive motor map is then taught by
  present/target difference information, not by reward–perturbation covariance.
- **VAM and cerebellar systems solve sign by carrying structured error.** Importing
  that error into EXP005 would violate the no-hidden-vector boundary.
- **SMART supplies local selectivity, not the missing behavioral sign.** Its timing
  gate can determine which synapses change during a match, but scalar outcome does
  not make that gate an estimator of an arbitrary neuron's causal BCI derivative.
- **Opponent channels represent signed quantities once defined.** They do not
  discover which arbitrary RSC cells belong to the positive or negative channel.

## Hard-stop decision

No audited rule satisfies all five candidate requirements. EXP005 therefore stops
the Grossberg-primary path at **Outcome E**. No confirmatory experiment will be run
under a label such as “Grossberg adaptive topology.” A generic reward-modulated
node-perturbation learner may be implemented only as a separately preregistered
diagnostic showing whether scalar reward is sufficient *in principle* under a new
local eligibility assumption. A hidden-vector learner may be used only as an oracle
sensitivity check.

This conclusion is narrower than “ART cannot explain learning.” It says that the
audited published systems do not specify the particular arbitrary, neuron-resolved
scalar-outcome operation required by bridge assumption A2.

## Primary references

- Carpenter, G. A., & Grossberg, S. (1987). ART 2: Self-organization of stable
  category recognition codes for analog input patterns. *Applied Optics, 26*,
  4919–4930. https://doi.org/10.1364/AO.26.004919
- Contreras-Vidal, J. L., Grossberg, S., & Bullock, D. (1997). A neural model of
  cerebellar learning for arm movement control. *Progress in Brain Research, 114*,
  371–391. https://sites.bu.edu/steveg/files/2016/06/ConGroBul97.pdf
- Gaudiano, P., & Grossberg, S. (1991). Vector associative maps: Unsupervised
  real-time error-based learning and control of movement trajectories. *Neural
  Networks, 4*, 147–183. https://doi.org/10.1016/0893-6080(91)90002-M
- Gnadt, W., & Grossberg, S. (2008). SOVEREIGN: An autonomous neural system for
  incrementally learning planned action sequences to navigate toward a rewarded
  goal. *Neural Networks, 21*, 699–758.
  https://doi.org/10.1016/j.neunet.2007.09.016
- Grossberg, S. (1986). The adaptive self-organization of serial order in behavior.
  In *Pattern Recognition by Humans and Machines*.
  https://sites.bu.edu/steveg/files/2016/06/Gro1986SchwabNusbaum.pdf
- Grossberg, S. (2018). Desirability, availability, credit assignment, category
  learning, and attention. *Brain and Neuroscience Advances, 2*.
  https://doi.org/10.1177/2398212818772179
- Grossberg, S. (2019). SOVEREIGN2: An autonomous neural system for incrementally
  learning planning, navigation, and adaptive behaviors. *Frontiers in
  Computational Neuroscience, 13*, 36. https://doi.org/10.3389/fncom.2019.00036
- Grossberg, S., Roberts, K., Aguilar, M., & Bullock, D. (1997). A neural model of
  multimodal adaptive saccadic eye movement control by superior colliculus. *Journal
  of Neuroscience, 17*, 9706–9725.
  https://sites.bu.edu/steveg/files/2016/06/GroRobAguBulJN1997.pdf
- Grossberg, S., & Seidman, D. (2006). Neural dynamics of autistic behaviors.
  *Psychological Review, 113*, 483–525.
  https://sites.bu.edu/steveg/files/2016/06/GroSei2006PsychRev.pdf
- Grossberg, S., & Versace, M. (2008). Spikes, synchrony, and attentive learning by
  laminar thalamocortical circuits. *Brain Research, 1218*, 278–312.
  https://doi.org/10.1016/j.brainres.2008.04.024

