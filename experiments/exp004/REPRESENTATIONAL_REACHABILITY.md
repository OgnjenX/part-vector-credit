# EXP004 representational reachability

## Exact update-history reconstruction

The clean model initializes every T coordinate to zero. For every update it archives category, selected and credited h, target vector, scalar outcome, value state, eligibility strength, effective rate, and T before/after.

For a pair receiving targets \(X_m\) and rates \(\eta_m\), the final expectation is exactly

\[
T_n=\sum_{m=1}^{n}
\left[\eta_m\prod_{\ell=m+1}^{n}(1-\eta_\ell)\right]X_m,
\]

with residual coefficient \(\prod_m(1-\eta_m)\) on the zero initial vector. Because all rates are in [0,1], T lies in the convex hull of zero and its actual targets and in their linear span.

EXP004 independently replays every selected evaluation pair and reports reconstruction RMSE, minimum eta, residual initial coefficient, and target count. RMSE above \(10^{-8}\) is R4/unexplained structure and is treated first as a bug or undocumented mechanism.

## Copy versus construction metrics

For each dominant category–h pair and context/action phase, record:

- corr(T,c) globally and on the effective phase mask;
- corr(T, the selected h's initial soma pattern);
- corr(T, every target and the simple target average);
- T alignment minus the best initial pattern alignment;
- T alignment minus the best individual target alignment;
- target-alignment variance and number of targets;
- distance among category-specific T vectors for the same h.

### R1 — copy/storage

Preregistered when mean corr(T, selected initial soma) is at least 0.95 and T does not improve on the best individual target by 0.10.

### R2 — outstar construction

Requires a role-alignment gain of at least 0.10 over every individual target, exact reconstruction, and multiple experienced targets. Merely having new numeric coordinates is insufficient.

### R3 — category factorization

Requires distinct same-h T vectors (normalized distance at least 0.10) plus an ART behavioral benefit of at least 0.10 beyond the fixed/contextual comparison with CI above zero.

### R4 — unexplained structure

Any T not reconstructed from the archived update history within RMSE \(10^{-8}\). This is initially a failure of implementation/theory accounting.

## Outcome-information counterfactuals

Two controls distinguish geometry from causal information:

1. **Online outcome-shuffled:** each current trace receives a randomly sampled prior outcome, preserving the empirical outcome range while breaking current action–outcome correlation and altering future policy.
2. **Frozen-visitation replay:** actual category/h/target visitation is held fixed, episode outcomes are permuted, and T is reconstructed offline. This isolates outcome-dependent scalar weighting from outcome-dependent policy sampling.

A T copied from a lucky B can still embody genuine outcome-driven acquisition if causal outcome determines which B/T pair dominates. That contribution is reported separately from outstar vector construction.

## Frozen held-out result

The replay reconstructed every evaluated T exactly (reported RMSE 0.0). At controlled medium coverage, corr(T, selected-h initial soma)=0.999851 and corr(T, the simple target average)=0.999870. T role alignment was 0.298 below the best initial pattern and 0.0325 below the best individual target. Same-h category T distance was 0.0074.

Online outcome shuffling reduced T alignment by 0.302 [0.234, 0.368], proving that causal outcome shaped which representation dominated. With the actual visitation/targets frozen, permuting outcomes changed T alignment by only −0.000041 on average. Thus the neuron-specific coordinates came from the selected response; scalar outcome supplied information mainly by changing selection and occupancy; outstar supplied stable within-pair compression. This is R1, not R2/R3/R4.
