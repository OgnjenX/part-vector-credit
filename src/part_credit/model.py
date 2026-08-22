"""Mechanism-level pART/SMART-inspired model.

This is deliberately not a biophysical SMART implementation. Each state variable
has an explicit computational interpretation documented in docs/MODEL_CARD.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ModelConfig:
    n_neurons: int = 10
    vigilance: float = 0.72
    category_lr: float = 0.08
    value_lr: float = 0.12
    attention_gain: float = 1.5
    surround_gain: float = 0.55
    apical_noise: float = 0.12
    wm_decay: float = 0.96
    now_print_threshold: float = 0.55


class PARTModel:
    """Small, auditable abstraction of the mechanisms under test.

    Reward is scalar. No neuron receives a target, derivative, signed error, or
    neuron-indexed teaching signal. Neuron specificity can only arise through
    selected working-memory/category activity and fixed top-down competition.
    """

    def __init__(self, config: ModelConfig, rng: np.random.Generator):
        self.cfg = config
        self.rng = rng
        n = config.n_neurons
        plus = np.arange(n) % 2 == 0
        prototype_a = np.where(plus, 0.65, 0.35)
        prototype_b = np.where(plus, 0.35, 0.65)
        # Two initially imperfect ART prototypes/hypotheses.
        self.prototypes = np.clip(
            np.stack([prototype_a, prototype_b]) + rng.normal(0, 0.06, (2, n)), 0, 1
        )
        self.values = np.zeros(2)
        self.wm = np.zeros(2)

    @staticmethod
    def _match(x: np.ndarray, prototype: np.ndarray) -> float:
        # Normalized complement-coded L1 similarity, computed without allocating
        # the redundant [x, 1-x] representation.
        return float(1.0 - np.abs(x - prototype).mean())

    def trial(
        self,
        soma: np.ndarray,
        target_action: int,
        *,
        motivated_attention: bool = True,
        reset_enabled: bool = True,
        working_memory: bool = True,
        shuffled_feedback: bool = False,
        explicit_vector_error: bool = False,
    ) -> dict[str, object]:
        matches = np.array([self._match(soma, p) for p in self.prototypes])
        choice_scores = matches + 0.08 * self.values + self.rng.normal(0, 0.015, 2)
        order = list(np.argsort(choice_scores)[::-1])
        resets = 0
        selected = order[0]
        if reset_enabled:
            while matches[selected] < self.cfg.vigilance and len(order) > 1:
                resets += 1
                order.pop(0)
                selected = order[0]
        resonant = bool(matches[selected] >= self.cfg.vigilance)

        if working_memory:
            self.wm *= self.cfg.wm_decay
            self.wm[selected] = 1.0
            causal = int(np.argmax(self.wm))
        else:
            causal = int(self.rng.integers(0, 2))

        action = selected
        reward = float(action == target_action)
        prediction_error = reward - self.values[causal]  # scalar global quantity
        now_print = bool(resonant and reward >= self.cfg.now_print_threshold)

        # Top-down on-center/off-surround feedback from the selected hypothesis.
        center = self.prototypes[causal] - self.prototypes[causal].mean()
        apical = self.cfg.attention_gain * center
        apical -= self.cfg.surround_gain * np.roll(center, len(center) // 2)
        if motivated_attention:
            apical *= 0.35 + reward
        else:
            apical *= 0.35
        apical += self.rng.normal(0, self.cfg.apical_noise, len(soma))

        if shuffled_feedback:
            apical = self.rng.permutation(apical)
        if explicit_vector_error:
            signs = np.where(np.arange(len(soma)) % 2 == 0, 1.0, -1.0)
            apical += (1 if target_action == 0 else -1) * prediction_error * signs

        # Match learning is resonance gated; value learning is Now-Print gated.
        if resonant:
            self.prototypes[selected] += self.cfg.category_lr * (
                soma - self.prototypes[selected]
            )
            self.prototypes[selected] = np.clip(self.prototypes[selected], 0.02, 1.0)
        if now_print:
            self.values[causal] += self.cfg.value_lr * prediction_error

        return {
            "selected": selected,
            "reward": reward,
            "resonant": resonant,
            "resets": resets,
            "apical": apical,
            "soma": soma,
            "target_action": target_action,
            "now_print": now_print,
        }
