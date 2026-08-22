# EXP003b implementation and information-boundary audit

## Architecture

Each seed creates eight learner-exchangeable lower neurons and an environment-only
balanced random causal vector `c`. Context B uses `-c`; at episode 120 the
environment secretly remaps the base vector. Sixteen independent random motor
hypotheses are initialized as eight antithetic pairs. Their labels, indices and
statistics contain no systematic causal information.

The closed loop is executed frame by frame:

1. visible context/state is complement-coded and categorized;
2. category-conditioned hypothesis competition selects a motor basis row;
3. `T[k,h]` supplies a separate modulatory top-down profile;
4. the cached Brian2 SMART motif produces lower soma/spikes and a local `W` update;
5. the hidden causal environment advances its state and returns the next visible observation;
6. after three action frames, four distractors intervene before scalar outcome learning.

No full trajectory is generated open-loop.

## Leakage safeguards

- Hidden role is sampled after independent RNG streams are split for environment,
  learner and audit.
- Motor basis and `T` initialization do not receive the role.
- Lower weights are identical at initialization.
- Context/category codes contain only visible context and task state.
- Candidate correlations and leave-one-neuron-out decoding with 300 label
  permutations are recorded before learning.
- The antithetic basis has exactly zero mean signed correlation across candidates,
  while chance alignment of individual candidates remains visible and is reported.
- `SmartResponseCache.frame` has no causal-role, reward, error or target argument.
- A test replays the same local inputs after changing offline `c` and requires
  bitwise-identical local results.

The positive control is explicitly exempt and isolated.

## Francioni-style measurement

Raw records keep soma, modeled dendrite at six event phases, learned `T`, local
weights, voltages, conductances, spikes, latency, hypothesis/category, reward,
error improvement, and offline hidden role separately.

For each neuron, dendrite is regressed on that neuron's soma and population-mean
soma. The residual signal is the error-improving minus error-worsening mean.
Longitudinal endpoints are computed within the most frequently sampled fixed
hypothesis so policy switching cannot alone create cellular change:

- `corr(D_residual_early, W_late-W_early)`;
- `corr(D_residual_early, S_probe_late-S_probe_early)`; and
- `corr(delta_W, delta_S_probe)`.

The future-soma probe freezes learning and top-down input and applies identical
feedforward drive before and after the training window. The primary model uses
the pre-action expectation phase. The vector positive control is evaluated at
sensory feedback, where its deliberately supplied outcome vector occurs.

## Causal perturbations

- `primary_t_to_smart_blocked`: `T` is learned and measured, motor output remains,
  but the local motif receives a zero top-down profile.
- `primary_post_learning_apical_suppressed`: normal acquisition/reacquisition;
  `T` expression is zero only in learning-off evaluation.
- `primary_shuffled_topdown`: the learned vector is permuted across neurons.
- No-resonance-gate and no-reset/search conditions are distinct even if ordinary
  task dynamics later reveal that a gate was rarely engaged.

## Known abstractions

This is not full SMART or pART. The local motif is a frozen grid cache of the
validated EXP003a Brian2 circuit. The selector is an ART/pART-inspired algorithm,
not a laminar prefrontal simulation. `T` samples centered soma through a discrete
outstar rule. The apical measurement is a modeled current with common soma/network
components, not a calcium-imaging forward model. Results therefore decide only
the tested composition.
