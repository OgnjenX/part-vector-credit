# Post-hoc analysis log

> **POST HOC / FAILURE LOCALIZATION — NOT CONFIRMATORY EVIDENCE**

1. The first launch was accidentally made from the isolated writable staging
   mirror. It stopped before locating or reading the held-out manifest and wrote
   no output.
2. The first real launch stopped at an exact-parity assertion. Investigation
   showed a data-precision limitation: archived weights are float32, whereas the
   frozen summary used in-memory float64 snapshots. The assertion was replaced by
   an explicit parity report; frozen metrics were not substituted into new raw
   analyses.
3. `results/` preserves the first complete diagnostic pass. `results_v2/` adds
   intermediate arrow correlations. `results_v3/` adds the decisive separation of
   modeled apical input, error-improvement contrast and soma-conditioned residual.
   Earlier outputs were not overwritten or relabeled.
