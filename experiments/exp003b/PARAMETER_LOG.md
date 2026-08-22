# EXP003b parameter and decision log

## Locked inheritance

The EXP003a motif, Eq. 5/6 reduction and canonical parameters were inherited
unchanged from commit `00d66cc`. An independently run ±10% gain and ±0.5 ms timing
robustness check passed 9/9 qualitative cases before BCI calibration. It did not
select any BCI parameter.

## Development-only decisions

1. Started with 8 cells, 16 hypotheses, 3 action frames and 4 distractors to keep
   the Brian2-backed paired suite feasible while retaining neuron-level analysis.
2. Used antithetic random motor pairs to guarantee a symmetric repertoire without
   observing hidden roles. This changes the claim to selection from a pre-existing
   random repertoire; it does not provide neuronal signs.
3. The initial environment causal strength 1.35 produced zero successful episodes
   in scalar-outcome conditions. A development-only sweep tested 1.8, 2.2, 2.6 and
   3.0. The least value permitting nontrivial behavior, 2.2, was fixed.
4. Acquisition/reacquisition were lengthened to 100/120 episodes, with 20-episode
   learning-off evaluations and 40-episode analysis windows, to provide remapping
   and fixed-hypothesis samples.
5. The success-error threshold remained 0.25. Scientific effect floors were not
   lowered after weak development results.
6. Development seeds 41–44 were used for all calibration. Confirmation seeds
   3100–3111 were defined in code and not inspected during development.

## Final parameters

The exact dataclass serialization is in `FROZEN_PROTOCOL.json`. Key values:
vigilance 0.88; category LR 0.12; reinforcement LR 0.24; outstar LR 0.09;
exploration 0.38→0.05; WM persistence 0.90; eligibility decay 0.82; motivated
gain 0.70; initial `T` scale 0.02; target `T` scale 0.45; transition noise 0.012.

No post-confirmation parameter change is permitted in EXP003b.
