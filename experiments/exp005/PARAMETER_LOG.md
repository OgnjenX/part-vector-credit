# EXP005 parameter log

All entries precede held-out confirmation.

| Development stage | Decision | Evidence and disposition |
|---|---|---|
| v1 | `eta=0.0015`, acquisition/remap 640/640, no N normalization | Acquisition topology aligned, but N=64 remap alignment was 0.686. Oracle empty-correlation warnings exposed a diagnostic edge case. Preserved; not confirmed. |
| v2 | Tested `eta=0.0020` | Did not improve N=32/64 remapping. Rejected; thresholds unchanged. |
| v3 | Restored `eta=0.0015`; remap 1,280 | N=32/64 post-remap alignments improved to 0.894/0.869. This established reversal cost. |
| v4 | Full suite at v3 settings | Verified all initial controls and exposed N-dependent control magnitude caused by the explicit `1/N` BCI drive. |
| v5 | Added `eta_N = eta N/32` | Equalized deterministic control magnitude across N without role information. Retained as transparent class-D normalization. |
| v6 | Equalized acquisition/remap at 1,280/1,280 | Acquisition passed, but remap fell to 0.63–0.71 because old topology first had to be undone. Preserved as a failed calibration. |
| v7 | Remap 2,560, acquisition 1,280 | N=32/64 post-remap alignment 0.953/0.946 and stable control 0.941/0.945. Retained. |
| v8 | Full final development suite | All required code paths completed; N=32 generic-vs-shuffled post-remap effect 0.676, CI `[0.533, 0.820]`. Ready to freeze. |

## Frozen numerical parameters

| Parameter | Value |
|---|---:|
| base learning rate | 0.0015 |
| learning-rate reference population | 32 |
| oracle learning rate | 0.012 |
| perturbation SD | 0.10 |
| initial topology SD | 0.008 |
| weight bound | 0.30 |
| eligibility decay | 0.80 |
| baseline rate | 0.08 |
| shuffle/update block | 16 episodes |
| acquisition episodes | 1,280 |
| remap episodes | 2,560 |
| action frames | 3 |
| state gain | 0.65 |
| success threshold | 0.60 |

