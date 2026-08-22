# EXP003a → EXP003b integration contract

## Locked local mechanism

EXP003b imports the validated EXP003a plasticity without editing it.

| File | Required SHA-256 |
|---|---|
| `src/part_credit/exp003a/motif.py` | `9f14f6daab5781da5d229fad4a89c85888e1d333d632a30f6f113689a4790604` |
| `src/part_credit/exp003a/plasticity.py` | `a9ef090dc204391c5d54bbdebc93c91c620132f89b64ca542c31b381dd50c755` |

The EXP003a validation checkpoint is
`00d66cceb696a097a03f65b8a64b29250d04361b`.

## Runtime boundary

The BCI runtime calls the response cache with exactly:

`motor/feedforward drive, current W_lower, top-down profile, reset state, plasticity on/off`.

The cache returns Brian2-derived voltage/conductance/spike measures and the
unchanged EXP003a local Eq. 5/6 weight update. Reward, task error, context, ART
category, hypothesis value and hidden causal role are absent from this API.

An automated replay test changes the offline hidden role while holding all local
inputs fixed and requires identical local outputs and updates.

## Cache construction

One vectorized Brian2 network evaluates 20,412 independent local motifs over:

- 9 motor/feedforward levels;
- 21 lower-weight levels;
- 9 cell-specific top-down levels;
- 6 global top-down/surround levels; and
- reset absent/present.

The response cache records real spike count/time, peak voltage and peak
feedforward/top-down/inhibitory conductance. The unchanged EXP003a update is
tabulated for each unique postsynaptic spike history and interpolated only along
the current-weight axis at runtime. All other axes use nearest-grid lookup.

This preserves the validated local causal mechanism while making the full paired
suite tractable. It is not a rate-model replacement. Its limitations are grid
quantization, no trial-to-trial membrane carry-over, and single-presentation local
cycles.

## Non-negotiable separation

`T[k,h,i]` is a learned apical/expectancy projection. `B[h,i]` is the motor drive.
`W_lower[h,i]` is the locally plastic lower synapse. Suppressing `T→SMART` leaves
the selected motor pattern unchanged; suppressing expression during frozen
evaluation does not erase either motor weights or learned policy values.

The explicit vector-credit positive control is a separate code branch. Its hidden
vector is passed only to `learn_outcome` when that condition flag is true.
