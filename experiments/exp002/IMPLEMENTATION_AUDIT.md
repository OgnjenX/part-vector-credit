# Implementation audit and EXP001 preservation

Commit `9f6807c` and every file under `results/exp001/frozen_v1/` are preserved byte-for-byte.
EXP002 imports no EXP001 module and writes only to `results/exp002/`.

## EXP001 issues retained as historical facts

- `plastic_basis_engineering_probe` was a mathematical no-op because `executed = basis[h]` and
  the update target was the same object. EXP001 remains unchanged. EXP002's separately named
  corrected probe targets centered executed soma and has a unit test requiring nonzero change.
- EXP001 generated all frames before feedback. EXP002 calls `environment.step(soma)` and feeds the
  returned visual state into the very next selection call.
- EXP001's learner did not observe a seven-bin evolving grating. EXP002 uses a continuous internal
  state but exposes a seven-bin one-hot visual observation after every frame.
- EXP001's full and random-basis-only labels shared a computation. EXP002 gives each mechanism a
  unique condition and direct test.
- EXP001 used the apical vector as motor drive. EXP002 soma reads only `motor_basis`; learned
  `topdown` is a separate projection. Expression suppression occurs only during plasticity-off
  evaluations, so it cannot mechanically remove the motor command.

## Leakage audit

The learner owns no causal-role attribute. Environment roles enter the controller only through
the explicitly named `active_causal_for_positive_control` argument and only when
`explicit_vector_error=True`. The main update target is observed executed soma. No statement in
the Grossberg path multiplies a scalar error/improvement by a neuron vector.

Seed spawning makes environment roles and learner initialization statistically independent.
Motor and top-down banks are also independently sampled. Tests inspect the boundary, enumerate
candidate correlations, run permutation decoding, and verify that motor output is invariant to
evaluation-only apical suppression.

## Causal interpretation limits

Suppressing the modeled apical branch blocks `T` learning or expression but does not reproduce
Francioni's NDNF manipulation exactly. Francioni activated layer-1 NDNF interneurons throughout
the task, preferentially inhibiting apical dendrites while also reducing somatic event rate. The
EXP002 branch-only perturbation is a computational isolation test and may be biologically cleaner
than the experiment, but it is less anatomically complete.
