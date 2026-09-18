# EXP006 confirmatory result

Status: **FROZEN PRIMARY RESULT AND PREDECLARED SECONDARY CHECK**

The primary result used untouched seeds 12000--12031 with `N=10`. The protocol,
parameters, scenario order, source hashes, and classification floors were committed
before those seeds were accessed. Values below are scenario means.

## Primary classification

| Model | Behavior | Topology | Francioni-like signature | Full bridge |
|---|---:|---:|---:|---:|
| Vector oracle | pass | pass | pass | pass |
| ART repertoire | pass | pass | fail | fail |
| Local eligibility | pass | fail | fail | fail |
| ART plus eligibility | pass | pass | fail | fail |
| Random no learning | fail | fail | fail | fail |

Only the privileged vector oracle passed the full bridge. This establishes that the
task and observation analysis can express the frozen target. It does not establish
that cortex receives such a vector.

## What each ordinary model showed

The ART repertoire learner reached late success of 0.675 in acquisition and 0.744
after remapping. Its topology correlations were 0.613 and 0.663. Its latent
role-by-direction scores were 0.513 and 0.613, and its measured residual scores were
0.030 and 0.039. Those residual effects survived the soma-matched analysis. Outcome
decoding also passed. However, the early residual did not predict later activity in
the acquisition phase. The prospective score was -0.203, with a 95% interval from
-0.396 to -0.010. The learner therefore failed the frozen Francioni-signature rule.
Its final topology was also below the best pattern already present in its fixed
bank. The result supports learned selection of pre-existing population patterns,
not de novo cellular credit.

The local eligibility learner reached acquisition success of 1.000 and remap success
of 0.656. It learned a strong new acquisition topology, with correlation 0.985, but
the remap correlation was 0.489 and changed-cell sign reversal was 0.673. Both were
below their frozen floors. Its latent and measured role-by-direction signals were
near zero, and outcome decoding remained close to chance. Local perturbations plus
scalar feedback were sufficient for substantial neuron-specific learning, but this
particular internal update drive did not reproduce the measured dendritic signature.

The hybrid reached acquisition success of 1.000 and remap success of 0.905. Its
topology correlations were 0.878 and 0.763. It therefore passed behavior and
topology. It nevertheless failed the dendritic criteria. The combined latent scores
were -0.119 and -0.088, and measured residual scores were -0.018 and -0.013. Component
archiving showed why: the ART component was positive (0.555 and 0.591), while the
eligibility component was negative (-0.127 and -0.096). Combining two useful
behavioral operations did not automatically produce the Francioni-like signal.

## Controls

All five frozen primary control comparisons passed. Outcome shuffling abolished ART
success and greatly reduced eligibility learning. Removing exploration or the
temporal trace abolished local eligibility learning. Enabling eligibility in the
hybrid improved acquisition success by 0.323 and acquisition topology by 0.278 over
the same hybrid with eligibility plasticity disabled. Component reconstruction error
was zero in every scenario.

## Secondary N=8 check

The secondary check was run only after the primary classification was written. The
ordinary-model pattern was similar: every ordinary learner failed the frozen
Francioni-signature rule, while ART's soma-matched residual was preserved and the
hybrid's combined signal retained the opposite sign.

The secondary check is not a valid full-bridge replication under the primary floor
because even the vector oracle missed the pre-outcome decoding threshold (0.543
versus 0.58). It is therefore sensitivity-limited for that composite classification.
It also has unusually high repertoire coverage: a bank of 64 balanced patterns
nearly exhausts the 70 possible balanced patterns for eight cells. ART's high N=8
behavioral and topology scores consequently provide weaker evidence about general
repertoire selection than the N=10 primary result. The hybrid eligibility
acquisition-control floor also failed at N=8 because the fixed repertoire condition
was already near ceiling.

## Conclusion

EXP006 does not show that ART-style representation selection and conventional
neuron-specific error learning are two descriptions of the same computation. It
shows that they can solve different parts of the same closed-loop task. ART-style
selection can learn which available population pattern to use and can produce a
role-structured dendritic-like residual. Local eligibility can create a new
cell-specific topology from scalar feedback. In the tested implementations, neither
ordinary mechanism nor their direct hybrid reproduced the complete combination of
behavior, remapping, topology, outcome decoding, and prospective dendritic
prediction.

The strongest supported interpretation is therefore complementary but unresolved:
population-level selection and cellular credit are computationally distinguishable,
and a successful biological account may require both. The present hybrid is not yet
that account. This is a model-specific sufficiency result and does not identify the
mechanism used in the Francioni experiment or rule out other ART formulations.
