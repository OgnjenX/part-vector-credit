# EXP004 conclusion — A2 is weakly supported but repertoire-limited

## Bottom line

The tested ART/pART-inspired abstraction can use scalar delayed outcome to discover **which pre-existing neuron-resolved population responses are useful**, assign them to learned category–hypothesis memories, and compose several fixed actions across closed-loop frames. It did **not** construct a T topology that was better than its individual experienced targets, and ART category proliferation did not outperform a plain contextual bandit.

The frozen two-axis result is:

- **Behavior: B1 + B2 + B3.** Ordinary learning is largely single-repertoire selection; a specifically solvable task demonstrates sequential composition; large banks expose a search/architecture limitation.
- **Representation: R1.** T is selected-pattern storage/compression, not R2 outstar generalization or R3 category-dependent factorization.
- **Bridge A2: A2-SUPPORTED-IN-WEAK-FORM and A2-REPERTOIRE-LIMITED.** Scalar outcome genuinely supplies information through selection statistics, but the neuron-wise coordinates come primarily from fixed repertoire geometry.

This is not a failure of category learning in general, and it is not evidence that ART is a lookup table. Categories were recruited and modified. The negative result is narrower: under the tested T[k,h] ownership and local outstar target rule, those category operations did not synthesize arbitrary topology across hypotheses.

## Direct answers

1. **Frozen EXP003b dependence on lucky coverage:** substantial before remap. Best initial soma coverage predicted acquisition success at r=0.681 [0.296, 0.894], while selected-h initial soma geometry predicted final T at r=0.958 pre-remap and 0.866 post-remap. Its T was almost exactly the sampled-target average.

2. **Does larger M help mainly by adding better candidates?** It adds better candidates: A_single rose from 0.117 at M=2 to 0.437 at M=128. Mediation through coverage was positive (0.097 fixed; 0.074 search-normalized), but larger action sets also made search harder, so raw performance was non-monotonic.

3. **Does fixed-M coverage predict behavior?** Yes. At M=16, LOW/MEDIUM/HIGH behavior was 0.765/0.882/0.962; HIGH−LOW was 0.197 [0.137, 0.255]. Coverage correlated 0.581 with behavior and 0.657 with T.

4. **Can a valid sequence be discovered when no single hypothesis is good?** Yes. On the phase-composition task, primary behavior was 0.980 and success 0.928 despite best repeated-single behavior 0.667.

5. **Does behavior exceed the best-single oracle?** In the composition condition, by 0.313 [0.260, 0.374]. Not in ordinary controlled banks, where a repeated single could already solve the noiseless oracle.

6. **How close is behavior to the allowed-composition oracle?** Within 0.020 [0.007, 0.043] in the composition condition.

7. **What do ART categories add beyond a contextual bandit?** No held-out performance benefit in this implementation: behavior difference 0.001 [-0.080, 0.064], T difference 0.015 [-0.028, 0.055]. The bandit also solved composition (0.977 versus primary 0.980).

8. **Do new categories permit different T memories?** They allocate distinct T slots, but the learned same-h vectors were not substantively distinct: normalized distance 0.0074, below 0.10. R3 was not supported.

9. **Is final T mostly a copy?** Yes. corr(T, selected initial soma)=0.999851 and corr(T, its target mean)=0.999870.

10. **Is T a multi-pattern generalization?** Numerically it averages many noisy soma samples, but scientifically it is R1 compression of one h's response, not an R2 cross-pattern construction.

11. **Can T exceed every initial B/S pattern?** It did not. At medium coverage T alignment was 0.298 below the best initial pattern and 0.0325 below the best individual target.

12. **Is T completely explained by permitted learning?** Yes. Replay from the exact targets and effective rates reproduced final T with RMSE 0.0. There is no unexplained topology.

13. **Initial-geometry contribution:** it supplied the cellular coordinates and bounded attainable action quality. Controlled coverage caused a 0.197 behavior difference, and selected initial geometry nearly equaled final T geometry.

14. **Scalar-outcome contribution:** it supplied causal information by changing values, hypothesis selection, and future trajectory occupancy. Breaking current outcome association reduced T alignment by 0.302 [0.234, 0.368].

15. **Category-formation contribution:** categories learned context/state partitions and owned separate V/T memories, but proliferation offered no incremental held-out benefit and often fragmented evidence. The two-category no-recruitment model outperformed full ART.

16. **Outstar contribution:** it locally consolidated the outcome-selected soma samples into a stable T. Frozen-visitation outcome permutation changed T alignment by only -0.000041, so rate weighting contributed negligible topology compared with which h/targets were visited.

17. **Was a new motor pattern required?** No for the demonstrated tasks. The clean motor bank changed by exactly zero. New categories and T memories are new representations, not new motor actions.

18. **Is there a repertoire bottleneck?** Yes. Controlled coverage strongly affected behavior, and at M=64/128 an allowed oracle of 1.0 coexisted with much lower search-normalized primary behavior (0.641/0.725), showing both coverage and discovery limitations.

19. **Which added plastic mechanism succeeds?** Only the explicit hidden-vector positive control cleanly solved LOW coverage. The generic scalar perturbation rule improved behavior by 0.070 [0.022, 0.120], below the frozen 0.20 criterion, so no biologically acceptable added mechanism has yet been established.

20. **What does this imply for A2?** A2 is supported only in the weak sense that scalar outcome plus structural credit can learn a neuron-resolved expectation by selecting and consolidating experienced distributed states. It is repertoire-limited and does not show acquisition of an arbitrary causal topology absent useful basis structure.

21. **How should EXP003b be interpreted?** Mainly **lucky repertoire selection plus genuine scalar-outcome structural credit**. EXP004 also establishes that behavioral composition is possible in a purpose-built condition, but neither EXP003b nor EXP004 supports strong ART-style construction of T across motor hypotheses.

22. **Strongest claim and unresolved issue:** neuron-specific T does not require a neuron-wise error to be *stored or selected* when useful distributed population patterns already exist. Still unresolved is how a biological system acquires or adapts a repertoire fine enough to span arbitrary, remapped intermingled P+/P− roles without neuron-specific causal teaching.

## Claim boundary

EXP004 falsifies, for this specified fixed-bank/T[k,h] abstraction, the strong claim that ART category learning plus its outstar automatically constructs arbitrary neuron-level causal topology from scalar outcome. It does not falsify ART, pART, SMART, adaptive motor systems, or other Grossberg architectures. It also does not prove that an explicit gradient or neuron-wise error is necessary: a richer pre-existing repertoire, sequential composition, or a separately justified local plastic mechanism could suffice.

The next justified computational experiment is not another dendritic residual fit. It is a preregistered topology-learning study with a theoretically sourced motor/adaptive-filter mechanism that can alter the action basis, compared against the present fixed-repertoire result and the generic scalar perturbation control. Until such a mechanism is specified from primary sources, the correct conclusion is that the Grossberg–Francioni representation-to-cell topology bridge remains under-specified.
