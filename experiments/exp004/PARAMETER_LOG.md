# EXP004 parameter log

All changes below used development seeds only. No held-out result has been viewed.

## Initial choices

- N=32 permits balanced sign patterns with several exact coverage levels while keeping the suite inexpensive.
- Motor entries 0.35/0.65 give identical geometry and causal score \(Q=0.30\,corr(B,c)\).
- Three action frames preserve closed-loop sequence selection.
- Target 0.30 makes LOW coverage 0.375 oracle-solvable by repeated use without making one frame sufficient.
- Vigilance 0.86 lets close continuous state observations resonate while context/large phase mismatches can recruit.
- Fixed 512 episodes and normalized 16M episodes separate practical budget from per-h opportunity.
- T starts exactly zero to remove random topology and enable target-only reconstruction.

## Development repairs

1. **Composition metric:** global corr(T,c) was inadequate when only a phase-specific cell mask was causally active. Added effective masked alignment while retaining global alignment. No model parameter changed.
2. **High-coverage construction:** rare-vector rejection failed. Replaced only the exact anchor generator with a balanced analytical flip construction. Geometry and coverage criteria stayed fixed.
3. **Generic motor-plasticity rate:** development sweep 0.08–8.0 selected 4.0, the best development success before degradation. This affects only the non-Grossberg secondary control. Full sweep is preserved in `FAILURES.md`.

## Frozen model parameters

| Parameter | Value |
|---|---:|
| N | 32 |
| action frames | 3 |
| contexts | 2 |
| target / success tolerance | 0.30 / 0.02 |
| action noise SD | 0.012 |
| delay steps | 4 |
| vigilance / choice alpha | 0.86 / 0.01 |
| category learning rate | 0.15 |
| value learning rate | 0.22 |
| outstar learning rate | 0.10 |
| exploration start/end | 0.65 / 0.05 |
| WM persistence / eligibility decay | 0.90 / 0.82 |
| generic motor control rate | 4.0 |
| explicit vector-control rate | 0.18 |

Development v2 fixed the calibration choices. Development v3 is the source-matched, compact-archive rerun used for freezing; its scientific results are identical to v2. No final criterion was lowered in response to weak performance.

## Confirmation

The protocol and source hashes were pushed at `a1d8aee`. `frozen_v1` then ran once on seeds 7000–7015 with the values above. There were no post-freeze parameter changes and no rerun.
