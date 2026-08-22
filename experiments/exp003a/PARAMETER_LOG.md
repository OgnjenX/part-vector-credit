# EXP003a parameter and development log

This log is append-only scientific history. EXP003a is a mechanism-validation
stage, so development calibration is allowed; it is not presented as held-out
confirmation.

## Starting point

- Historical theory-audit checkpoint:
  `aa3323a5da1715c5ee4c18c81fe8caa179243fdf`.
- EXP000, EXP001, EXP002, and `experiments/exp003/` were not modified.
- Brian2 was added to the existing uv-managed environment.

## Calibration changes

| Step | Change | Reason known before next run | Scientific status |
|---|---|---|---|
| Initial motif | Feedforward gain 1.80 | First automated run showed feedforward alone was suprathreshold, so the ablated condition learned and the future-response probe was saturated | Failed calibration; not evidence for the mechanism |
| Early calibration | Feedforward gain reduced to 1.45 | Enforce the intended modulatory boundary: neither feedforward nor top-down alone should spike | Led to `development_v1` |
| Audit after v1 | Brian2 single-exponential feedforward was replaced by the exact same normalized dual-exponential trace used by Eq. 5 | v1 passed operational gates but neural current and plasticity did not use the same presynaptic conductance | Scientifically consequential repair; v1 invalidated and preserved |
| Corrected conductance calibration | Feedforward gain 0.60; rise/fall 0.5/30 ms; cycle 80 ms; Eq. 5 rate 0.02 ms\(^{-1}\) | The longer trace qualitatively recovered SMART Figure 6a's timing relationship; gain/rate were reduced to prevent saturation and isolate future response | Produced `development_v2` |
| Reporting-only repair | Nonfinite JSON values changed from `NaN` to `null`; explicit “top-down alone is modulatory” gate added | Make raw summaries standards-compliant and turn a documented assumption into an automated criterion | Produced canonical `development_v3`; no dynamic parameter changed |

No threshold was lowered after seeing a held-out result; there was no held-out
phase in EXP003a. The complete v3 parameter set is in
`results/exp003a/development_v3/summary.json` and [IMPLEMENTATION.md](IMPLEMENTATION.md).
