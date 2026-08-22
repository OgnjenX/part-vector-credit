# EXP002 preregistration: learned top-down expectancy

Status at creation: **development draft; confirmatory execution is software-blocked until
`FROZEN_PROTOCOL.json` is committed.** EXP001's `frozen_v1` data at commit `9f6807c` are
historical inputs only and will not be rerun or modified.

## Question and claim boundary

Can pART-inspired structural/temporal selection plus a Grossberg outstar-derived learned
top-down expectancy generate Francioni-like neuron-specific dendritic signals without a
neuron-wise causal derivative? This is a mechanism-level sufficiency test. It is not a faithful
implementation of pART, SMART, MOTIVATOR, or the Francioni circuit.

The primary chain is:

`scalar outcome -> reinforced hypothesis H -> repeated resonant lower pattern -> learned T_H -> apical expression`.

The outstar equation is Grossberg-derived. Connecting a pART-inspired causal hypothesis to the
modeled BCI population by this equation is **Grossberg-compatible extrapolation** because the
primary sources do not specify this exact cross-system BCI pathway.

## Information boundary

The environment alone stores the random balanced causal vector `c`. Context B uses `-c`.
After each action frame, the learner receives a one-hot observable context, one of seven visual
state bins, and the fixed target bin. After five distractors it receives scalar global
improvement and binary reward. It never receives `c`, a P+/P- label, a causal derivative, or a
scalar multiplied by a neuron pattern. Only the explicitly named positive control receives `c`.

Motor bases and initial top-down weights are sampled independently of `c`, centered, and
exchangeable over neurons. Every seed reports all candidate correlations and a label-permutation
decoder. The confirmatory group must have absolute mean signed correlation below 0.05 for both
banks; decoder accuracy must be within 0.15 of its permutation-null mean. Chance alignment of an
individual random motor pattern is expected and reported.

## Closed-loop task and schedule

There are 10 neurons, 48 random motor hypotheses, 8 action frames per episode, and two observable
contexts. Every frame is genuinely closed loop:

`soma y(t) -> hidden mean(P+) - mean(P-) -> visual state s(t+1) -> seven-bin observation -> y(t+1)`.

The preregistered schedule is 220 acquisition episodes, 40 plasticity-off evaluation episodes,
a complete hidden remap, 220 reacquisition episodes, and 40 plasticity-off evaluation episodes.
Contexts alternate, so the same neurons have opposite roles in adjacent episodes. Outcomes arrive
after five irrelevant distractors. Development seeds are 20-27. Confirmatory seeds are 2000-2029
and may be run once only after freezing this document, code, parameters, metrics, and tests.

## Primary learning rule

For selected resonant hypothesis `h`, centered executed soma `S~`, and source/memory gain `g`:

`T_h <- T_h + eta_T g (S~ - T_h)`.

This is the outstar sampling principle. Reward does not multiply `S~`. Outcome changes the scalar
hypothesis value, which changes later selection and motivated source gain. The motor command is
always read from separate weights `B_h`, never from `T_h`.

The corrected plastic-basis probe separately applies `B_h <- B_h + eta_B g (S~ - B_h)`. Unlike
EXP001's invalid no-op, its target differs from the current basis. This is an exploratory
Grossberg-compatible consolidation probe, not part of the primary claim.

## Fixed comparison suite

1. frozen/no learning;
2. random controller;
3. contextual bandit with an explicit delayed eligibility trace;
4. bandit plus direct selected-motor-pattern copy to apical activity;
5. pART-inspired selection without learned expectancy;
6. pART-inspired selection plus outstar expectancy (primary);
7. primary without structural credit;
8. primary without working-memory retention;
9. primary without motivated attention/reinforcement;
10. primary without reset/search;
11. primary without resonance gating;
12. primary with a fixed neuron shuffle on top-down expression;
13. primary with top-down learning suppressed;
14. primary with apical expression suppressed only during plasticity-off evaluation;
15. corrected plastic-basis/outstar probe;
16. explicit neuron-wise vector-error positive control.

All conditions share seed-derived environments, initial motor bases, initial top-down weights,
exploration schedules, delays, contexts, remaps, and evaluation opportunities. ART search uses
complement-coded visible observations, vigilance 0.88, rejection, and uncommitted category
recruitment. Its actual reset and recruitment rates will determine whether search belongs in the
explanation.

## Frozen primary analyses

Windows are the first/last 50 acquisition or reacquisition episodes (25 per context) and all 40
plasticity-off evaluation episodes. We report behavior, selected `T` alignment to hidden `c`, old
`T` alignment immediately after remap, context-A/B opposition, resonance/reset/recruitment, and
the change norms of `B` and `T`.

`early_selected_topdown_alignment` is measured after the first 25 episodes per context and is not
an initialization measure. Zero-information-at-initialization claims use only the independently
computed full-bank initialization audits.

For each neuron and timing bin, dendrite is regressed on its soma and population-mean soma. The
residual signal is mean residual on above-median error-improvement frames minus the complement.
The five timing bins are selection, action, visual feedback, outcome, and post-outcome. The
longitudinal metric is the across-neuron correlation between the early residual signal and
late-minus-early mean soma. Seed means and 95% seed-bootstrap intervals are frozen analyses.

This is analogous to, not identical with, Francioni's event-magnitude residual: the abstraction
has continuous model activity rather than matched calcium events and branch-specific imaging.

## Preregistered support/falsification thresholds

Strong support (Outcome A) requires all of the following on held-out seeds:

- primary pre- and post-remap evaluation success at least 0.35 and paired improvement over both
  frozen and random at least 0.10 with a 95% paired-bootstrap interval above zero;
- initial leakage limits above;
- primary selected-top-down alignment at least 0.25 before and after remap and an increase of at
  least 0.20 over the corresponding initial-bank mean signed correlation;
- post-remap alignment exceeds old-pattern/new-mapping alignment by at least 0.20;
- context top-down opposition at least 0.25;
- pre- and post-remap longitudinal correlations at least 0.15 with 95% intervals above zero, and
  paired differences above frozen and random with intervals above zero;
- suppressing top-down learning reduces post-remap alignment by at least 0.15 and behavioral
  success by at least 0.05; expression suppression reduces the dendritic signature while changing
  already learned evaluation behavior by less than 0.05;
- the vector-error control learns, establishing task learnability.

Outcome B is assigned if direct-copy bandit meets the behavioral and longitudinal criteria and is
within 0.10 of the primary longitudinal effect, so the result supports generic routing but not a
specifically Grossbergian account. Outcome C applies if selection learns behavior but the primary
fails the cellular/longitudinal criteria while vector error succeeds. Outcome D applies if the
source mapping proves indefensible. Outcome E applies if primary and non-learning/random controls
are non-discriminating or residuals are dominated by engineered covariance.

No threshold or analysis will be changed after held-out inspection. Any post-confirmatory work is
labeled exploratory and receives new seeds/versioning.
