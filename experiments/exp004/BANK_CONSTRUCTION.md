# EXP004 bank construction and leakage audit

## Common geometry

All clean banks contain 32-cell balanced sign directions \(d_h\in\{-1,+1\}^{32}\) with 16 signs of each kind. Motor/soma patterns are

\[
B_h=0.5+0.15d_h.
\]

Every row therefore has exactly the same mean, variance, L2 norm, amplitude, and number of high/low cells. Every direction has an antithetic partner. Rows are permuted in controlled banks so the oracle direction is not identified by index or pair position.

The learner receives the motor patterns because they are its action repertoire. It never receives hidden role c, coverage label, coverage score, oracle identity, or construction metadata.

## Random nested banks

One maximum 128-row interleaved antithetic bank is generated per seed. The M=2,4,8,… prefixes contain complete antithetic pairs and are exact subsets of all larger M banks for that seed. This makes changes with M attributable to additional candidate directions rather than regenerated smaller banks.

The random generator is independent of c. Before learning, EXP004 archives B, the deterministic initial soma response, c for offline analysis, every row alignment and causal score, pairwise similarities, norms, means, and variances.

## Controlled coverage at M=16

Coverage is the maximum behaviorally signed correlation of an initial soma pattern with c. Exact anchor correlations are:

| Band | A_single anchor | Initial causal Q for amplitude 0.15 | Repeated-three-frame oracle |
|---|---:|---:|---:|
| LOW | 0.375 | 0.1125 | Solvable |
| MEDIUM | 0.625 | 0.1875 | Solvable |
| HIGH | 0.875 | 0.2625 | Solvable |

An exact anchor is built by starting from c and flipping equal numbers of P+ and P− coordinates, preserving balance. Other directions are sampled below the band's maximum. Antithetic partners make both observable contexts equally expressible.

The original near-perfect rejection sampler failed during development and is preserved in `FAILURES.md`. Exact construction is now deterministic in criterion but random in flipped-cell identity and row placement.

## Low-single-coverage composition banks

The composition condition uses three disjoint, balanced six-cell phase masks. The experimenter constructs low-global-alignment directions with phase-specific useful components, then admits a bank only if:

1. global \(A_{single}\le0.25\);
2. the exact allowed sequence succeeds;
3. its normalized behavior exceeds the best repeated-single oracle by at least 0.20.

The learner observes action phase but not masks, c, or oracle actions. This condition asks whether state/category-dependent selection can compose existing directions. It does not claim the repertoire lacks useful components—the phase-specific basis is intentionally pre-existing.

## Leakage checks

Automated tests establish:

- random-bank nesting and antithetic completion;
- exact LOW/MEDIUM/HIGH coverage;
- matched row means/norms/variances across coverage classes;
- composition solvability under the learner's actual action operations;
- no role/coverage/oracle parameter in selection or frame-recording APIs;
- zero motor-bank change in the clean primary.

Pairwise geometry can differ by chance across controlled banks and is archived. The label cannot be decoded from row norm, mean, variance, amplitude, or index, but the behaviorally relevant correlation is intentionally different; removing that difference would remove the manipulation.
