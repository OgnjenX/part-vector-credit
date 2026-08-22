# EXP003b failure log

Failures are evidence and are retained; no failed output is relabeled as frozen
confirmation.

1. **Initial cache build stalled.** NaN-filled no-spike histories compared unequal,
   producing a huge number of apparent unique timing histories. The run was
   interrupted before an output was written. Cache construction now uses a
   negative sentinel only for deterministic uniqueness, restores NaNs before the
   unchanged local update, and has regression tests.
2. **Initial causal task was behaviorally too weak.** At causal strength 1.35,
   scalar-outcome models obtained no successes. A development-only task-strength
   sweep was performed and recorded in the parameter log; 2.2 was fixed before
   confirmation.
3. **Development v1 evaluation leaked learning.** Values and top-down expectancies
   continued updating during purported frozen evaluation. The entire
   `development_v1` directory is preserved as invalid. The runner was corrected
   so all outcome learning is disabled during evaluation; `development_v2` is the
   canonical development result.
4. **Primary development longitudinal chain failed.** Although top-down feedback
   advanced matched spike timing and changed lower weights, the within-hypothesis
   dendritic residual did not predict later weight or future-soma change at the
   frozen effect floors. No mechanism or threshold was changed to rescue it.
5. **Context opposition was weak in development.** Primary mean opposition was
   0.167 versus the frozen 0.25 floor. This was not tuned.
6. **Expression perturbation was not behaviorally inert.** The motor projection
   remained present, but suppressing apical input during frozen evaluation changed
   post-remap behavior by more than the 0.05 separation floor. This shows that the
   apical branch is physically separate yet still modulates current local output.
7. **Ordinary resonance was saturated.** The primary development run resonated on
   every selected frame. Reset/search recruited categories and rejected candidates,
   but the no-resonance-gate condition cannot establish an ordinary-trial causal
   role when the gate is never closed. This limitation will be reported, not hidden.

The held-out run remains untouched at protocol freeze.
