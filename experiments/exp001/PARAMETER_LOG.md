# EXP001 parameter decision log

## Initial development configuration — 2026-08-22

The preregistered development run used 32 random hypotheses, vigilance 0.80,
attention gain 1.0, working-memory persistence 0.96, reinforcement rate 0.12,
exploration 0.20, ten balanced neurons, five action frames, four distractors, and
1,000 trials with remapping at trial 600. Criteria were frozen beforehand.

Result: the full abstraction improved from 0.293 to 0.525 success before remapping
and from 0.317 to 0.514 afterward, but failed the ≥0.70 behavioral criterion. The
explicit-vector positive control reached 1.000. This run remains in
`results/exp001/exp001_development.*`.

The prespecified one-factor robustness sweep found that reinforcement rate 0.30 was
the only tested single change that met both pre-remap learning (0.716) and post-
remap late success (0.802) on development seeds. Rates 0.04 and 0.12 reached 0.401
and 0.514 post-remap, respectively. No multi-parameter search was performed.

## Frozen confirmatory configuration

For held-out seeds 1000–1029, reinforcement rate is changed to **0.30**. Every other
default, condition, analysis, and success threshold remains unchanged. This choice
was made using development seeds only. Confirmatory results will not trigger a
threshold or parameter revision.

