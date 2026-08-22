# Validation report

> **POST HOC / FAILURE LOCALIZATION — NOT CONFIRMATORY EVIDENCE**

## Overall assessment: share with caveats

The arrow-localization calculations are reproducible and support classification A
as a diagnostic. Sparsity, float precision and the absence of time-aligned current
traces prevent stronger or confirmatory inference.

## Evidence and grain

- Controlling source: committed `results/exp003b/frozen_v1` at final EXP003b
  commit `f1a509a`.
- All 23 frozen evidence files matched their original SHA-256 manifest before the
  post-hoc arrays were read.
- Final output contains 48 fixed-hypothesis units: 12 seeds × two contexts ×
  pre/post remap; exactly four units per seed.
- `per_seed.csv` contains 12 rows. All numeric values in `per_unit.csv` are finite.
- `results_v3/SHA256SUMS.json` verifies all six final diagnostic artifacts.
- No file under `src/part_credit/exp003b`, `results/exp003b`, or
  `experiments/exp003b` was changed.

## Calculation checks

- Fixed-hypothesis selection, windows and error-conditioned residual were copied
  from the frozen definitions.
- The held-hypothesis future-soma probe is reconstructed by inferring the exact
  discrete motor-cache coordinate from recorded `g_ff_peak` and querying the
  already committed response cache with learning/top-down off. No Brian2 run occurs.
- Pre-remap raw reconstruction matches every frozen seed correlation to `6e-7`.
- Post-remap reconstruction matches 10/12 seeds to `1e-6`; one seed differs by
  more than 0.1 because raw `weight_before/after` were archived as float32 while
  the frozen metrics used in-memory float64 snapshots. Raw values were not
  replaced post hoc.
- Headline correlations are means of within-eight-neuron fixed-h correlations,
  then averaged across units within seed. Confidence intervals resample seeds,
  not neurons or frames.

## Material caveats

1. The net-current measure uses recorded peak envelopes. Separate `g_td_peak`,
   `g_inh_peak`, and `V_peak` are not time-aligned. It is equation-derived but not
   an instantaneous or integrated current.
2. Plasticity is highly sparse: 92.97% of fixed-h neuron endpoints are zero in the
   archived arrays. Full-vector effects primarily diagnose gate selection.
3. Engaged-only magnitude analyses have too few cells and are explicitly
   exploratory; they cannot support a positive mechanism claim.
4. These endpoints were chosen after seeing frozen Outcome C. Confidence intervals
   quantify sampling variation but do not convert post-hoc analysis into
   confirmation.
5. Classification A localizes the tested implementation failure to its readout;
   it does not show that biological Francioni residuals discard the same signal.

## Visual review

Both figures use zero-referenced correlation/fraction axes, seed-bootstrap
intervals, explicit labels and no hidden subsetting. The localization figure
shows the loss at `D_residual`; the sparsity figure keeps absolute fractions on a
zero baseline. Rendered PNGs were inspected for clipping and sign integrity.
