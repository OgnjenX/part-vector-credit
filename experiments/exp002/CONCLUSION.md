# EXP002 conclusion

## Outcome C — falsified for this mechanism

The frozen held-out experiment does **not** support the strong Grossbergian top-down explanation.
It supports a narrower decomposition:

1. delayed scalar reinforcement can select a useful distributed motor hypothesis;
2. a Grossberg outstar-derived associative rule can learn the soma pattern that repeatedly occurs
   under that selected hypothesis and later express it as cell-specific top-down feedback;
3. this feedback tracks hidden remapping because selection changes which motor patterns recur;
4. nevertheless, it is a readout of successful selection, not the Francioni-like instructive
   signal tested here.

The exact source of the modeled dendritic pattern was local outstar sampling
`T_h += eta(S_tilde-T_h)`. But direct bandit copying of `B_h` to apical activity produced the same
behavior and essentially the same hidden-role alignment. Nothing specifically pART/SMART was
needed for that result.

Neither mechanism reproduced the learning-dependent soma-conditioned residual. The primary's
longitudinal effect was negative before remapping and indistinguishable from zero afterward. By
contrast, the explicitly neuron-indexed positive control showed the preregistered positive
longitudinal effect and an outcome-timed dendritic vector.

After hidden remapping, the old expectancy was poorly aligned with the new roles (0.056) and a new
selected expectancy became aligned (0.287), while behavior recovered to 0.397. This demonstrates
representational adaptation, but context opposition remained weak (0.135) and the cellular
criterion still failed.

Apical-learning suppression eliminated learned top-down alignment without changing behavior at
all. Expression suppression eliminated the modeled apical pattern without erasing the already
learned motor command, as intended. The branch was therefore neither mechanically confounded with
motor output nor causally necessary for learning in this implementation.

The warranted theoretical conclusion is limited but substantive: **pART-inspired structural and
temporal credit plus an ART outstar expectancy is not sufficient, in this tested composition, to
explain Francioni's vectorized longitudinal dendritic teaching signature.** A separate fine-grained
credit mechanism is more strongly motivated. The experiment does not prove that biological
learning must use backpropagation or a literal gradient, and it does not falsify all possible
Grossberg circuits. It shows that selection plus learned top-down pattern completion, by itself,
does not do the required cellular-credit work.
