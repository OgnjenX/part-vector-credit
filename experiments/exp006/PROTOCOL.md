# EXP006 Francioni-matched mechanism benchmark

Status: **DESIGN LOCKED FOR IMPLEMENTATION; CONFIRMATORY RUN FORBIDDEN**

## Question

Can an ART-style population-selection mechanism reproduce the behavioral and
cell-role-dependent dendritic signatures reported by Francioni et al. without an
explicit neuron-wise error vector? If it cannot do so alone, does local eligibility
supply a complementary cellular operation?

EXP006 is a computational sufficiency and discrimination study. It cannot identify
the biological mechanism used by cortex.

## Relation to the frozen record

EXP000--EXP005 remain unchanged. They established routing, repertoire selection,
learned expectancy, a local SMART-inspired motif, the inherited-topology boundary,
and the sufficiency of generic local eligibility in a delayed scalar-outcome task.
EXP006 changes the information structure to match the motivating experiment more
closely. In particular, every non-oracle learner receives continuous visual-state
feedback during each trial as well as delayed reward.

## Primary task

- Primary population: `N = 10`, balanced into five hidden P+ and five hidden P-
  cells.
- Secondary population: `N = 8`, analyzed only after the primary classification.
- Trial length: at most 28 one-second action frames.
- Visual display: seven equally spaced angle bins from 0 to 90 degrees.
- Continuous latent state: `x in [0,1]`, with displayed angle obtained by binning
  `90*x`.
- Opponent drive:

  `u_t = mean(S_i : c_i=+1) - mean(S_i : c_i=-1)`.

- State transition:

  `x_(t+1) = clip(x_t + g*u_t, 0, 1)`.

- Success: the target bin is reached during the 28-frame action period.
- Reward: binary reward is delivered after a one-frame post-success delay.
- Acquisition: 14 blocks of 64 trials (896 trials).
- Hidden remap: an independently sampled balanced role vector, followed by another
  14 blocks of 64 trials.
- The hidden role vector is available only to the environment, offline analyses,
  and the explicitly labeled vector oracle.

The exact state gain, exploration scale, and learning rates are development
parameters. They may be calibrated only on development seeds and must be recorded
in `PARAMETER_LOG.md` before confirmation.

## Information available to ordinary learners

At every frame, ordinary learners may observe:

- the current displayed visual bin;
- normalized within-trial time;
- the previous displayed visual bin and state change;
- their own somatic activity;
- their own model-local top-down, perturbation, or eligibility variables;
- delayed binary reward after success or timeout.

They may not observe P+/P- labels, the hidden role vector, a neuron-wise target,
coverage, an oracle action, or an externally supplied cell-wise gradient.

## Primary model classes

1. `vector_oracle`: privileged sensitivity control with an explicit cell-wise
   teaching direction. It is not a biological claim.
2. `art_repertoire`: Fuzzy-ART-style category formation, hypothesis selection,
   value learning, and learned top-down expectancy over a fixed random balanced
   motor repertoire. It has no adaptive cell-wise motor correction.
3. `local_eligibility`: an explicitly non-Grossberg node-perturbation learner that
   combines local perturbations with visible improvement and delayed reward.
4. `art_eligibility_hybrid`: the ART selector supplies context/state-dependent
   representation selection while local eligibility learns a cell-wise correction.
5. `random_no_learning`: yoked null model.

Primary controls are outcome shuffling for ART and eligibility, removal of
exploration, removal of temporal eligibility, and a hybrid with its eligibility
update disabled. A simulated apical-feedback perturbation is secondary because no
single abstraction of NDNF activation is mechanism-neutral.

## Common dendritic observation layer

Behavioral success is not treated as evidence of a Francioni-like signal. Each
model must expose its genuine cell-indexed feedback quantity `F_i(t)`:

- vector oracle: its explicit teaching quantity;
- ART: the selected learned top-down expectancy;
- eligibility: the local eligibility-by-modulator update drive;
- hybrid: separately archived ART and eligibility components and their declared
  combination;
- null: zero feedback.

The common synthetic observation model is

`D_i(t) = alpha*S_i(t) + beta*standardize(F_i(t)) + noise_i(t)`.

For each neuron, a linear soma--dendrite relation is fitted on development-defined
calibration events. The residual is the observed dendritic magnitude minus the
value predicted from soma. The observation layer never receives the hidden role.
Its coefficients and noise scale must be identical across models and frozen before
confirmation. Latent `F`, simulated soma, simulated dendrite, and residual are all
archived so measurement failure can be separated from algorithmic failure.

## Primary endpoints

### Behavior and topology

- acquisition and post-remap success rate;
- trials to a frozen success criterion;
- deterministic topology--role correlation;
- correct-sign fraction and remapped-cell sign reversal;
- final topology minus the best single experienced population sample;
- exact update and legal-variable replay error.

### Francioni-like signatures

- role-by-error-direction residual score:

  `mean_i,t[c_i * sign(delta_x_t) * residual_i(t)]`;

- the same interaction in latent feedback before the calcium observation layer;
- cross-validated decoding of successful versus unsuccessful trial states from the
  residual population vector, both before and after outcome;
- prospective prediction of later cell activity change from early role-conditioned
  residuals, controlling for baseline activity;
- preservation of these signatures after restricting to matched somatic activity;
- change in learning and signal expression under the preregistered model-specific
  apical perturbation.

The model-side `D -> delta-W -> delta-S` chain is a stronger mechanistic extension,
not a direct reproduction of the Francioni assay. It is reported separately from
the Francioni-like endpoints.

## Development and confirmation

- Development seeds: 601--608.
- Reserved confirmatory seeds: 12000--12031.
- Development may use shortened trial counts for deterministic tests and profiling.
- Primary model definitions, available information, endpoint formulas, and
  direction of effects may not change after implementation begins without an
  append-only protocol amendment.
- Numerical pass floors will be selected from task sensitivity and null-control
  behavior on development seeds, then frozen before any confirmatory seed is used.
- The confirmation command must refuse to run without a machine-readable frozen
  protocol containing source hashes, scenario order, parameters, and untouched
  held-out status.

## Interpretation matrix

- ART alone passes: ART-style selection is sufficient in this implementation.
- Hybrid passes but ART alone fails: representation selection and cellular credit
  are complementary.
- Only the vector oracle passes: the tested ordinary mechanisms lack required
  structured information.
- Eligibility and hybrid pass: explicit centrally routed vector error is not
  computationally necessary in this task.
- Several mechanisms reproduce all signatures: the Francioni observables do not
  uniquely identify the learning algorithm.

No outcome is allowed to support a claim about all ART models or the biological
origin of the measured dendritic signal.

## Pre-confirmation analysis amendment: matching identifiability

Development showed that exact soma matching can be undefined when role groups have
no common somatic support. This occurs in the vector oracle because its activity is
deliberately separated by hidden role. An empty match is not assigned a score of
zero. The score is reported as unidentified, together with the matched-sample
count. Preservation after matching is classified only when both phases contain a
mean of at least 100 matched samples per seed. This rule was added before any
confirmatory seed was accessed.
