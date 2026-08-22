"""Auditable pART-inspired hypothesis-selection abstraction for EXP001."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LearnerConfig:
    n_neurons: int = 10
    n_hypotheses: int = 32
    max_categories: int = 8
    vigilance: float = 0.80
    attention_gain: float = 1.0
    wm_persistence: float = 0.96
    reinforcement_lr: float = 0.30
    exploration: float = 0.20
    action_scale: float = 0.32
    soma_noise: float = 0.08
    dendrite_noise: float = 0.10
    category_lr: float = 0.15
    basis_lr: float = 0.03


@dataclass(frozen=True)
class Condition:
    plasticity: bool = True
    random_policy: bool = False
    structural_credit: bool = True
    working_memory: bool = True
    motivated_attention: bool = True
    now_print: bool = True
    reset_search: bool = True
    resonance_gate: bool = True
    shuffled_feedback: bool = False
    plastic_basis: bool = False
    apical_suppression: bool = False
    explicit_vector_error: bool = False


def random_basis(rng: np.random.Generator, rows: int, cols: int) -> np.ndarray:
    basis = rng.normal(0, 1, (rows, cols))
    basis -= basis.mean(axis=1, keepdims=True)
    basis /= np.sqrt(np.mean(basis**2, axis=1, keepdims=True)) + 1e-9
    return basis


class HypothesisLearner:
    """Selects distributed patterns using delayed scalar outcome only.

    The Grossberg-only path has no reference to the environment's causal vector.
    `explicit_vector` is accepted only when the positive-control flag is true.
    """

    def __init__(self, cfg: LearnerConfig, condition: Condition, rng: np.random.Generator):
        self.cfg = cfg
        self.condition = condition
        self.rng = rng
        self.basis = random_basis(rng, cfg.n_hypotheses, cfg.n_neurons)
        self.prototypes: list[np.ndarray] = []
        self.values = np.zeros((cfg.max_categories, cfg.n_hypotheses))
        self.wm_hypothesis: int | None = None
        self.wm_category: int | None = None
        self.wm_strength = 0.0
        self.last_hypothesis = 0
        self.last_category = 0
        self.last_resonant = False
        self.category_recruitments = 0
        self.explicit_policy = random_basis(rng, 1, cfg.n_neurons)[0]

    @staticmethod
    def _match(observation: np.ndarray, prototype: np.ndarray) -> float:
        return float(1.0 - np.abs(observation - prototype).mean())

    def _categorize(self, observation: np.ndarray) -> tuple[int, bool, int]:
        if not self.prototypes:
            self.prototypes.append(observation.copy())
            self.category_recruitments += 1
            return 0, True, 0
        matches = np.array([self._match(observation, p) for p in self.prototypes])
        order = list(np.argsort(matches)[::-1])
        resets = 0
        chosen = order[0]
        if self.condition.reset_search:
            while matches[chosen] < self.cfg.vigilance:
                resets += 1
                order.pop(0)
                if order:
                    chosen = order[0]
                    continue
                if len(self.prototypes) < self.cfg.max_categories:
                    self.prototypes.append(observation.copy())
                    self.category_recruitments += 1
                    return len(self.prototypes) - 1, True, resets
                chosen = int(np.argmax(matches))
                return chosen, False, resets
        resonant = bool(matches[chosen] >= self.cfg.vigilance)
        return chosen, resonant, resets

    def act(
        self, observation: np.ndarray, action_frames: int, explicit_vector: np.ndarray | None = None
    ) -> dict[str, object]:
        category, resonant, resets = self._categorize(observation)
        if self.condition.random_policy:
            hypothesis = int(self.rng.integers(self.cfg.n_hypotheses))
            pattern = random_basis(self.rng, 1, self.cfg.n_neurons)[0]
        elif self.condition.explicit_vector_error:
            if explicit_vector is None:
                raise ValueError("positive control requires environment-only explicit vector")
            hypothesis = 0
            pattern = self.explicit_policy
        else:
            if self.rng.random() < self.cfg.exploration:
                hypothesis = int(self.rng.integers(self.cfg.n_hypotheses))
            else:
                scores = self.values[category] + self.rng.normal(0, 1e-6, self.cfg.n_hypotheses)
                hypothesis = int(np.argmax(scores))
            pattern = self.basis[hypothesis]

        if self.condition.shuffled_feedback:
            pattern = self.rng.permutation(pattern)
        value_gain = max(0.0, self.values[category, hypothesis])
        gain = self.cfg.attention_gain * (1.0 + value_gain)
        if not self.condition.motivated_attention:
            gain = 0.45 * self.cfg.attention_gain
        if self.condition.apical_suppression:
            gain = 0.0

        apical = gain * pattern[None, :] + self.rng.normal(
            0, self.cfg.dendrite_noise, (action_frames, self.cfg.n_neurons)
        )
        soma = np.clip(
            0.5 + self.cfg.action_scale * apical
            + self.rng.normal(0, self.cfg.soma_noise, apical.shape), 0.0, 1.0
        )
        network_drive = soma.mean(axis=1, keepdims=True)
        dendrite = 0.35 * soma + 0.20 * network_drive + apical

        self.last_hypothesis = hypothesis
        self.last_category = category
        self.last_resonant = resonant
        self.wm_hypothesis = hypothesis
        self.wm_category = category
        self.wm_strength = 1.0
        return {
            "soma": soma,
            "dendrite": dendrite,
            "apical": apical,
            "hypothesis": hypothesis,
            "category": category,
            "resonant": resonant,
            "resets": resets,
            "passive_sensory": observation.copy(),
            "feedback_pattern": pattern.copy(),
            "feedback_gain": gain,
        }

    def delay(self, distractors: list[np.ndarray]) -> None:
        for _ in distractors:
            self.wm_strength *= self.cfg.wm_persistence
            if not self.condition.working_memory:
                self.wm_hypothesis = int(self.rng.integers(self.cfg.n_hypotheses))
                self.wm_category = int(self.rng.integers(max(1, len(self.prototypes))))

    def learn(self, global_improvement: float, reward: float, explicit_vector: np.ndarray | None = None) -> None:
        if not self.condition.plasticity:
            return
        hypothesis = self.wm_hypothesis if self.condition.structural_credit else int(
            self.rng.integers(self.cfg.n_hypotheses)
        )
        category = self.wm_category if self.condition.structural_credit else int(
            self.rng.integers(max(1, len(self.prototypes)))
        )
        if hypothesis is None or category is None:
            return
        gated = self.last_resonant or not self.condition.resonance_gate
        if self.condition.now_print and gated:
            outcome = 0.75 * global_improvement + 0.25 * reward
            self.values[category, hypothesis] += self.cfg.reinforcement_lr * self.wm_strength * (
                outcome - self.values[category, hypothesis]
            )
        if self.condition.plastic_basis and gated:
            # Outstar-like consolidation contains no causal derivative: it can
            # stabilize an executed pattern but cannot discover hidden signs.
            executed = self.basis[hypothesis]
            self.basis[hypothesis] += self.cfg.basis_lr * max(global_improvement, 0) * (
                executed - self.basis[hypothesis]
            )
        if self.condition.explicit_vector_error:
            if explicit_vector is None:
                raise ValueError("positive control requires the forbidden causal vector")
            error = 1.0 - global_improvement
            self.explicit_policy += self.cfg.basis_lr * error * explicit_vector
            self.explicit_policy -= self.explicit_policy.mean()
            self.explicit_policy /= np.sqrt(np.mean(self.explicit_policy**2)) + 1e-9
