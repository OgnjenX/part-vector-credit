# Initial experiment protocol

## Question and hypotheses

Can a pART/SMART-inspired system produce population-opposed apical modulation in an
artificial P+/P- task when reward is scalar and there is no neuron-indexed error?

- **H1 (computational sufficiency):** the full model reaches at least 70% late-task
  accuracy and has a positive opposition index, with P+ and P- modulation having
  opposite signs in at least 80% of seeds.
- **H0:** either learning or the modulation criterion fails.
- **Mechanistic prediction:** shuffling top-down feedback should destroy the
  opposition signature. Removing working memory should impair temporal/structural
  credit. Removing motivated attention should reduce modulation magnitude.

These criteria were fixed in code before the confirmatory 30-seed run. They are
operational tests of this implementation, not a claim of statistical equivalence
to the mouse data.

## Conditions

The suite runs the full model, removals of motivated attention, reset, and working
memory, a shuffled-feedback control, and an explicit-vector-error positive control.
It also includes a high-vigilance (0.90) mismatch stress test because ordinary
task inputs may not exercise reset; this stress test is diagnostic, not primary.
All conditions use identical seed numbers and task distributions. Measurements use
the final 300 of 1,200 trials to reduce contamination by initial transients.

The primary cellular proxy is

`opposition index = mean(P+ target-0 minus target-1 apical activity) - mean(P- equivalent)`.

This deliberately tests sign and selectivity, not calcium-imaging kinetics, distal
tuft biophysics, or the exact regression analysis of Francioni et al.

## Falsification and interpretation

The strong claim is falsified if the full model misses either preregistered
criterion. If it succeeds but shuffled feedback also succeeds, the proposed
on-center/off-surround mechanism is not identified. If learning succeeds without
opposition, the architecture is computationally adequate on this toy task but does
not explain dendritic vectorization. If opposition occurs without learning, it is
an architectural pattern rather than learned credit assignment.

Any result is evidence only about this abstraction. A stronger test requires the
published task contingencies and analysis, a laminar spiking implementation, and
parameter robustness rather than a single hand-set regime.
