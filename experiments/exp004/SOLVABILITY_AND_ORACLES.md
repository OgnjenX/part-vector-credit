# EXP004 solvability and repertoire oracles

All oracles are environment-side offline analyses with hidden c. Their outputs are never passed to a learner.

## Best repeated-single oracle

For every context and frame, compute the deterministic initial causal score

\[
q_{f,h}=\mathrm{mean}_{c_i>0}S_{h,i}^{(f)}-
\mathrm{mean}_{c_i<0}S_{h,i}^{(f)}.
\]

The best-single oracle repeats one h for all action frames and evaluates the exact clipped state transition. It reports h, sequence, trajectory, final normalized state, and success.

## Best allowed-sequence oracle

The primary controller may select one h at each of three stepwise action frames after observing the updated state. No simultaneous mixture exists. The allowed-sequence oracle therefore selects the best h separately at every frame and runs that sequence through the same deterministic transition.

For the standard task, q is frame-invariant and this oracle reduces to repeating the best h. For phase-composition banks, q depends on the prespecified mask and the optimal allowed sequence may use several h. This is the only primary composition claim.

## Mathematical mixture bound

No convex-mixture oracle is used for classification because the primary controller cannot emit a simultaneous mixture. Any later mixture analysis must be labeled a mathematical bound, not an achievable action.

## Admission rule

Controlled LOW/MEDIUM/HIGH and phase-composition banks must have `best_allowed_success = 1` before they enter either development or confirmation. Phase-composition banks must additionally have an allowed-sequence advantage of at least 0.20. Uncontrolled random banks are not rejected when unsolvable; oracle failure is part of the bank-size result.

## Behavioral classifications

- **B1:** learned T is copy-like and standard behavior is explainable by selection of an existing h.
- **B2:** phase-composition behavior exceeds the repeated-single oracle by at least 0.15, has bootstrap CI above zero, and is within 0.10 of the allowed-sequence oracle.
- **B3:** an allowed oracle reaches at least 0.95 but the primary remains at least 0.15 below it under search-normalized experience.
- **B4:** a separately labeled motor-plasticity extension exceeds the fixed primary by at least 0.20 with CI above zero.

These flags are not mutually exclusive across task regimes. A model can demonstrate B2 where composition is expressible and B3 where its search/category architecture fails to discover an available sequence.
