# EXP005 model architecture

Status: **PRE-REGISTERED GENERIC DIAGNOSTIC; NOT A GROSSBERG PRIMARY MODEL**

## Source gate

The primary-source audit returned Outcome E. The executable architecture therefore
does not contain a condition named “Grossberg adaptive topology.” Its purpose is to
locate the missing operation by testing whether one explicit generic assumption is
sufficient in principle.

## Task loop

For each seed, the environment samples balanced independent hidden role vectors
`c` and `c'`. During each of three action frames:

```text
adaptive source-to-RSC weights A
  + locally generated perturbation xi
  -> RSC soma S = clip(0.5 + A + xi, 0, 1)
  -> hidden BCI drive = 2 (S - 0.5) dot c / N
  -> visible scalar BCI state
```

The final state is the scalar delayed outcome. The learner never receives `c`, the
P+/P- partition, or a neuron-wise target.

## Generic three-factor comparator

The learner retains an episode eligibility

`e_i <- lambda e_i + xi_i / sigma^2`

and, after delayed outcome, updates

`A_i <- A_i + eta_N (R - b) e_i`,

followed by preregistered bounds and population centering. Here `b` is an
exponential scalar baseline. `eta_N = eta * N / 32` compensates for the explicitly
normalized BCI population mean; it carries no hidden role information.

The implementation applies updates in blocks of 16 episodes. In the normal
condition rewards retain their episode pairing. In the outcome-shuffled control,
the exact same reward multiset is randomly permuted within each block before being
paired with eligibility. The batching therefore gives the shuffle control an exact
yoked comparison.

This rule is class D generic node perturbation. The neuron-varying factor is local
`xi_i`; the common factor is scalar `R-b`. It is deliberately isolated from every
Grossberg attribution.

## Hidden-vector oracle

The class-E oracle uses `A_i <- A_i + eta_oracle c_i`. It is implemented in a
separate class whose privileged method is absent from the generic learner. It is a
task sensitivity bound, not a biological model.

## Conditions and scaling

The complete frozen suite contains generic, outcome-shuffled, and hidden-vector
oracle conditions at `N = 8, 16, 32, 64`. At the N=32 anchor it additionally tests
plasticity disabled, temporal eligibility disabled, exploration removed, and a
zero-topology random/no-learning controller. Historical EXP004 supplies the fixed-
repertoire comparison; it is not rerun or altered.

No ART, pART, SMART, category, or dendritic observation model is included. That is
intentional: the source gate found no justified Grossberg cellular rule to which
those mechanisms could be attached.

