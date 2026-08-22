# Model card: what is Grossberg-derived and what is engineered

## Mechanisms represented

The implementation maps Grossberg concepts to explicit, inspectable operations:

| Concept | Implementation |
|---|---|
| competing categories/hypotheses | two category scores with winner selection |
| ART match and vigilance | complement-coded L1 similarity compared with a threshold |
| mismatch, reset, search | a below-vigilance winner is inhibited and the next candidate tested |
| resonance-gated match learning | prototype update occurs only after a sufficient match |
| causal working memory | a decaying selected-category trace persists until outcome |
| motivated attention | scalar reward changes the gain of selected top-down feedback |
| Now Print-like gate | reward plus resonance gates category-value learning |
| top-down on-center/off-surround | selected prototype excites matching features and suppresses competitors |

No operation computes a loss gradient, backpropagates an error, supplies a target
activation to a neuron, or multiplies an error by neuron-specific trainable weights.
The only outcome signal in the full model is scalar reward.

## Engineering simplifications and risks

This is a discrete rate model, not the differential-equation, spiking, laminar
SMART model. Its two categories, fixed vigilance, scalar reinforcement gate, and
one-step task are engineered abstractions. “Apical activity” is the top-down
feedback vector plus noise; it is not a compartmental membrane or calcium model.
The task's P+/P- identities and the model's two contrasting initial prototypes are
structurally aligned. This is a consequential prior: success would show that ART
selection can *route* a vector pattern without an explicit vector error, not that
the pattern's neuron-level sign was learned from scalar reward alone.

The Now Print gate is only an analogy: Grossberg's basal-ganglia and reinforcement
circuits are substantially richer. The working-memory trace does not model dlPFC
laminar dynamics. The model also lacks gamma/beta synchrony, nonspecific thalamus,
acetylcholine, STDP, OFC/vlPFC/amygdala detail, eligibility traces, and anatomical
distances between the intermingled neurons.

These omissions prevent a claim of biological reproduction. The repository tests
a narrower existence question and exposes the assumptions that could make an
apparent positive result trivial.
