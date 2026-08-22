# EXP003 failure log

## Theory-audit limitations identified before implementation

1. pART does not provide an equation-complete causal-representation-to-arbitrary-BCI-apical
   pathway. EXP003's cross-system composition is therefore Grossberg-compatible, not faithful pART.
2. SMART's verified local-plasticity mechanism is visual thalamocortical. Generalizing its lower
   adaptive-filter role to BCI motor/output neurons is an explicit extrapolation.
3. VAM/aVITE motor learning uses an observable vector mismatch and cannot silently solve hidden
   neuronal credit from scalar reward.
4. A category-indexed lower weight bank would make context reversal easier but lacks sufficient
   source justification for the primary model; the audit proposes shared per-motor-channel lower
   weights instead.
5. Exact discrete integration of SMART's spike-timing rule is not yet validated.

These are limitations, not post hoc excuses. They remain part of the interpretation even if the
eventual model succeeds.

## Computational failures

None. No EXP003 code or simulation exists at this checkpoint.
