# EXP000 — Prestructured vector-routing sanity check

EXP000 is preserved without rewriting its run history. Its corrected run showed
that selective top-down routing of a pre-existing opponent code can produce
Francioni-looking P+/P− modulation without explicitly computing a vector error.
It did **not** test de novo neuron-level credit assignment.

The positive result was structurally favored because:

1. hidden P+/P− identity was the visible even/odd neuron index;
2. both initial category templates encoded that same opponent partition;
3. the task sampled somatic activity conditional on the correct target;
4. the selected prototype directly generated the reported apical vector;
5. prototype learning was unnecessary for the classification;
6. corrected ordinary trials had 100% resonance and zero reset;
7. working memory did not bridge a real causal delay; and
8. the task was classification, not closed-loop causal control.

The frozen-template baseline was absent from the original suite. A preserved post
hoc reanalysis set both category and value learning rates to zero and obtained
0.978 mean late accuracy across 30 seeds—essentially identical to Run 2. Its script
is `experiments/exp000/frozen_reanalysis.py` and raw seed metrics are in
`results/exp000_frozen_reanalysis.json`. EXP001 removes all visible population
identity. Original source and outputs remain in place.
