# EXP003a failure log

Negative and invalidated runs are retained because successful output alone would
overstate the validation.

## F0 — Brian2 wiring error

The first implementation attempted to connect one-to-one feedforward synapses
with an invalid Brian2 `connect(i=..., j=...)` usage. Tests failed before producing
scientific output. The connection was repaired to `connect(j="i")`.

## F1 — Feedforward-only saturation

With feedforward gain 1.80, both lower cells spiked without top-down input. The
top-down-ablated condition consequently learned, and initial probe responses were
already saturated. This violated the modulatory premise and the future-response
test. The gain was reduced before the next stored run.

## F2 — `development_v1` invalid conductance correspondence

`development_v1` passed its then-current operational gates, but inspection found
that Brian2 used a single-exponential feedforward current while the offline Eq. 5
update used a dual-exponential presynaptic trace. The two computations therefore
did not share the exact same \(\bar g\), weakening the causal interpretation.

This run is invalid as mechanism validation. Its raw outputs remain under
`results/exp003a/development_v1/`; they were not overwritten or relabeled.

## F3 — `development_v2` reporting deficiencies

The corrected shared-conductance model passed nine mechanistic gates, but missing
latencies were serialized as non-standard JSON `NaN`. The classifier also relied
on, but did not explicitly test, the premise that top-down input alone is
subthreshold. No dynamic parameter changed for v3. `development_v2` remains as a
superseded successful development run rather than the canonical checkpoint.

## Remaining scientific failure modes

Outcome A does not remove the following unresolved risks:

- `f_G=f_N**2` is a reduced post-spike proxy, not SMART's raw-voltage gate.
- The model supplies the top-down expectation and mismatch signal; it does not
  learn or infer either one.
- Total suppression of the competitor and mismatch cells is a stronger regime
  than merely delayed spiking. It validates selective timing through the circuit,
  but does not span the original SMART dynamics.
- The motif was calibrated, not fitted to or quantitatively validated against a
  published SMART trace.
- No BCI, reward, pART, hidden causal role, or Francioni analysis exists here.

These limits are why the result is “validated reduced motif,” not “SMART
validated” or support for the larger Grossbergian account.
