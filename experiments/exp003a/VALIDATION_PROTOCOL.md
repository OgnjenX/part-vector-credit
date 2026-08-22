# EXP003a validation protocol

## Question

Does the reduced spiking motif implement this causal chain without a direct
top-down teaching term?

\[
T\rightarrow V_i/\text{spike timing}\rightarrow f_G
\rightarrow\Delta W_i\rightarrow\Delta S_{i,future}.
\]

EXP003a is deterministic mechanism validation, not a held-out population-level
statistical experiment. Its operational gates were fixed for the final development
checkpoint, but were not preregistered before all calibration. All failures and
parameter changes must remain visible. No EXP003b work is authorized unless this
protocol produces Outcome A.

## Fixed comparisons

All cells begin at weight 0.60 and receive the same feedforward timing.

1. **Matched:** top-down on-center to cell 0 and surround inhibition to cell 1.
2. **Top-down ablated:** no top-down spike; motor/feedforward input is unchanged.
3. **Shuffled:** top-down center points to cell 1; cell 0 is the competitor.
4. **Mismatch:** matched top-down is present, followed by reset-like broad
   inhibition before the feedforward spike.

The protocol records lower-cell voltage, feedforward/top-down/inhibitory
conductances, lower and interneuron spikes, weight trajectories, STDP-window
occupancy, and learning-off future responses. The standalone pair protocol records
the final Eq. 5/6 timing curve; the per-step `f_N`, `f_G`, and derivative arrays are
available from `equation5_update` but are not duplicated in each condition archive.

## Mechanistic gates

The final-development classifier requires all ten gates for Outcome A:

| Gate | Frozen operational criterion |
|---|---|
| Matched update nonzero | selected-cell \(\Delta W\ge0.04\) |
| Competitor much smaller | \(|\Delta W_{competitor}|\le0.25|\Delta W_{matched}|\) |
| Top-down ablation removes advantage | maximum ablated \(|\Delta W|\le0.25|\Delta W_{matched}|\) |
| Mismatch suppresses learning | maximum mismatch \(|\Delta W|\le0.25|\Delta W_{matched}|\) |
| Matched timing in window | matched occupancy \(\ge0.80\) |
| Competitor timing suppressed | competitor occupancy \(\le0.25\) |
| Future response changes | post-learning matched-cell spike count exceeds prelearning count under the same feedforward-only probe |
| Surround circuit operates | surround interneuron spikes in matched trials |
| Reset circuit operates | reset interneuron spikes in mismatch trials |
| Top-down is modulatory alone | no lower-cell spike occurs between top-down and feedforward input |

STDP-window occupancy is the fraction of presentations with a postsynaptic spike
from 0 through 25.1 ms after the cell's feedforward presynaptic spike.

The shuffled condition is an identity control: the selective weight change and
future response must follow the supplied top-down center, not neuron index.

## Qualitative SMART timing check

The same Eq. 5/6 implementation is evaluated in a single-pair protocol over
post-minus-pre offsets from -30 to +30 ms. It should reproduce the relevant
qualitative SMART Figure 6a relationship: weak depression for post-before-pre
timing and potentiation when presynaptic conductance overlaps the post-spike
plasticity state. This is a qualitative check, not a numerical reproduction.

## Automated safeguards

Tests require:

- exact values at the Eq. 6 piecewise boundaries;
- nonzero matched update and a much smaller competitor update;
- suppressed mismatch and ablated updates;
- a weight-dependent future response;
- no top-down or teaching-vector argument in the local update;
- identical local spike histories producing identical updates; and
- top-down input remaining subthreshold without feedforward input.

## Decision rule

- **A — VALIDATED:** all mechanistic gates pass and the timing relationship is
  qualitatively consistent with the source mechanism.
- **B — PARTIALLY VALIDATED:** some qualitative behavior works, but at least one
  important timing or future-response property fails.
- **C — FAILED:** cell-selective learning requires an artificial condition gate,
  direct teaching term, or mechanism inconsistent with the source.

Outcome A permits discussion of EXP003b but does not automatically start it.
