# pART/SMART without vector errors: an initial computational test

This project asks a deliberately narrow question: can a mechanism-level
pART/SMART-style architecture produce opposite P+/P- dendritic/apical modulation
in a Francioni-like neurofeedback task **without an explicit vectorized error
signal**?

It is an exploratory computational model, not a faithful reproduction of the full
pART or SMART equations and not a reproduction of the animal experiment. The most
important limitation is structural: the model starts with contrasting category
templates aligned to the artificial populations. A positive result therefore
shows selective routing by hypothesis/resonance dynamics, not de novo discovery of
neuron-specific credit from scalar reward.

## Scientific motivation

Francioni et al. observed opposite task-related signals in distal apical dendrites
of intermingled layer-5 pyramidal-neuron populations during a BCI task, interpreting
them as vectorized instructive signals. Grossberg's pART account instead emphasizes
structural and temporal credit assignment through working memory, attention,
resonance, reinforcement, and gated learning. SMART embeds ART matching, reset, and
attentive learning in laminar thalamocortical circuits. This repository tests
whether a carefully labeled abstraction of those mechanisms can generate the
qualitative sign opposition without supplying neuron-wise errors.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
part-credit --seeds 30 --trials 1200
```

Outputs are written to `results/initial_experiment.json` and `.png`. The fixed
hypotheses, conditions, and decision rules are in [docs/PROTOCOL.md](docs/PROTOCOL.md).
The mapping from theory to code—and the simplifications that limit inference—is in
[docs/MODEL_CARD.md](docs/MODEL_CARD.md). The narrative outcome and failures are in
[docs/RESULTS.md](docs/RESULTS.md).

The corrected initial suite met its operational primary criterion (97.8% late
accuracy; P+ modulation +0.673, P- -0.673 across 30/30 opposite-sign seeds), but
frequent-mismatch stress failed badly. Read the results log before interpreting the
headline: the vector basis was structurally present in the category templates, and
reset/search was not validated by the ordinary task.

## Architecture

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

## License

MIT. Scientific claims remain subject to the limitations above.
