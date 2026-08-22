# pART-inspired credit assignment versus dendritic vectorization

This project asks a deliberately narrow question: can a mechanism-level
pART/SMART-style architecture produce opposite P+/P- dendritic/apical modulation
in a Francioni-like neurofeedback task **without an explicit vectorized error
signal**?

It is an exploratory computational model, not a faithful reproduction of the full
pART or SMART equations and not a reproduction of the animal experiment. The most
important limitation is structural: the model starts with contrasting category
templates aligned to the artificial populations. A positive result therefore
shows selective routing by hypothesis/resonance dynamics, not de novo discovery of
neuron-specific credit from scalar reward. That original study is now explicitly
preserved as **EXP000 — Prestructured vector-routing sanity check**. **EXP001 — De
novo causal-credit experiment** removes the shortcut and tests a causal BCI task.

## Scientific motivation

Francioni et al. observed opposite task-related signals in distal apical dendrites
of intermingled layer-5 pyramidal-neuron populations during a BCI task, interpreting
them as vectorized instructive signals. Grossberg's pART account instead emphasizes
structural and temporal credit assignment through working memory, attention,
resonance, reinforcement, and gated learning. SMART embeds ART matching, reset, and
attentive learning in laminar thalamocortical circuits. This repository tests
whether a carefully labeled abstraction of those mechanisms can generate the
qualitative sign opposition without supplying neuron-wise errors.

## Experiments

- [EXP000](docs/EXP000_AUDIT.md) preserves the original implementation and all
  failed/calibrated runs. Its positive result is only a routing existence check.
- [EXP001 protocol](experiments/exp001/PROTOCOL.md) freezes the causal task,
  information boundary, controls, analyses, and held-out decision rules.
- [Theory mapping](experiments/exp001/THEORY_MAPPING.md) maps each abstraction to a
  primary Grossberg source and marks unsupported engineering choices.
- [EXP001 results](experiments/exp001/RESULTS.md) and [conclusion](experiments/exp001/CONCLUSION.md)
  report the development failures, held-out test, and theory-level interpretation.
- [EXP002 protocol](experiments/exp002/PROTOCOL.md) tests whether an independently initialized,
  Grossberg outstar-derived top-down expectancy can learn cell-specific structure after scalar
  reinforcement selects a distributed causal hypothesis. Its [theory mapping](experiments/exp002/THEORY_MAPPING.md)
  distinguishes Grossberg-derived principles from cross-system extrapolations and engineering
  baselines.

## Main finding

On 30 held-out seeds, the pART-inspired abstraction learned the causal BCI behavior
by selecting and reinforcing a chance-aligned pattern from a frozen random basis
(late success 0.728 before and 0.716 after hidden remapping). It did **not** pass the
stronger Francioni criterion: its early soma-conditioned dendritic residual did not
reliably predict later neuron-specific activity change (`r = 0.124`, threshold
0.20), whereas the explicit neuron-wise positive control reached `r = 0.461` and
perfect late success.

The warranted result is **Outcome 3—behavioral learning without validated dendritic
vectorization**, with **Outcome-2 pre-existing basis selection** explaining the
behavior. The experiment supports Grossberg-style structural/temporal credit at
the representation level; it does not identify a Grossberg-only mechanism that
learns arbitrary hidden neuronal signs from scalar outcome.

## Run EXP000

```bash
uv sync --extra dev
uv run pytest
uv run part-credit --seeds 30 --trials 1200
```

## Run EXP001

```bash
uv run part-credit-exp001 --phase development
uv run part-credit-exp001 --phase confirmatory
```

## Run EXP002

EXP002 uses the repository's uv environment. Confirmation is intentionally blocked until the
development protocol is frozen in git.

```bash
uv sync --extra dev
uv run part-credit-exp002 --phase development --output results/exp002/development_v1
```

EXP000 outputs are written to `results/initial_experiment.json` and `.png`. EXP001
development and confirmation are under `results/exp001/frozen_v1/`. The fixed
hypotheses, conditions, and decision rules are in [docs/PROTOCOL.md](docs/PROTOCOL.md).
The mapping from theory to code—and the simplifications that limit inference—is in
[docs/MODEL_CARD.md](docs/MODEL_CARD.md). The narrative outcome and failures are in
[docs/RESULTS.md](docs/RESULTS.md).

The corrected initial suite met its operational primary criterion (97.8% late
accuracy; P+ modulation +0.673, P- -0.673 across 30/30 opposite-sign seeds), but
frequent-mismatch stress failed badly. Read the results log before interpreting the
headline: the vector basis was structurally present in the category templates, and
reset/search was not validated by the ordinary task.

The post hoc frozen EXP000 audit achieved 97.8% accuracy with both learning rates
set to zero, confirming that EXP000 measured routing of a prestructured code.

## EXP000 architecture (preserved)

`task.py` generates intermingled P+/P- activity. `model.py` implements category
competition, fuzzy ART-style match/vigilance/reset, resonance-gated prototype
learning, working memory, scalar reward, a Now Print-like gate, motivated attention,
and top-down on-center/off-surround feedback. `experiment.py` applies the frozen
conditions and metrics. `cli.py` saves seed-level results and a comparison figure.

## References

- Francioni, V. et al. (2026). “Vectorized instructive signals in cortical
  dendrites during a brain-computer interface task.” *Nature*, 652, 1254–1263.
  [doi:10.1038/s41586-026-10190-7](https://doi.org/10.1038/s41586-026-10190-7)
- Grossberg, S. (2018). “Desirability, availability, credit assignment, category
  learning, and attention.” *Brain and Neuroscience Advances*.
  [doi:10.1177/2398212818772179](https://doi.org/10.1177/2398212818772179)
- Grossberg, S. & Versace, M. (2008). “Spikes, synchrony, and attentive learning
  by laminar thalamocortical circuits.” *Brain Research*, 1218, 278–312.
  [doi:10.1016/j.brainres.2008.04.024](https://doi.org/10.1016/j.brainres.2008.04.024)
- Grossberg, S. (2021). “A canonical laminar neocortical circuit whose bottom-up,
  horizontal, and top-down pathways control attention, learning, and prediction.”
  [doi:10.3389/fnsys.2021.650263](https://doi.org/10.3389/fnsys.2021.650263)
- Gaudiano, P. & Grossberg, S. (1991). “Vector associative maps.”
  [doi:10.1016/0893-6080(91)90002-M](https://doi.org/10.1016/0893-6080(91)90002-M)

## License

MIT. Scientific claims remain subject to the limitations above.
