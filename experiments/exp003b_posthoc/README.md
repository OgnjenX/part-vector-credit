# EXP003b post-hoc failure localization

> **POST HOC / FAILURE LOCALIZATION — NOT CONFIRMATORY EVIDENCE**

This directory diagnoses the already frozen EXP003b Outcome C using only committed
held-out arrays and the committed frozen response cache. It does not change,
rerun, or reinterpret EXP003b and introduces no new learning mechanism.

The analysis traces signed learned `T` through clipped excitation, recorded
top-down excitation/inhibition, membrane-current envelope, spike changes, local
weight change, held-hypothesis future soma, and the existing Francioni residual.

Run once into the append-only output directory:

```bash
uv run python experiments/exp003b_posthoc/analyze.py
```

The script verifies the frozen evidence manifest and checks reconstruction of the
four frozen longitudinal seed metrics before computing any new post-hoc result.
`results/` and `results_v2/` preserve the initial diagnostic passes. `results_v3/`
is the complete arrow-by-arrow analysis, additionally separating mean modeled
apical input from error-improvement contrast and soma-conditioned contrast. None
of these analyses reruns EXP003b.

The diagnostic classification is **A with explicit sparsity/precision caveats**:
cell-specific information survives through local SMART plasticity and the
held-hypothesis future response, then is lost by the current soma-conditioned
Francioni readout. This does not alter frozen EXP003b Outcome C. See
[REPORT.md](REPORT.md) and [VALIDATION.md](VALIDATION.md).
