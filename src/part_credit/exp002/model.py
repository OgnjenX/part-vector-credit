"""Mechanism-level controllers for EXP002.

The primary controller combines pART-inspired selection/temporal credit with a
Grossberg outstar-derived top-down expectancy. The application of that outstar
to BCI motor neurons is explicitly an extrapolation, not a published pART model.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LearnerConfig:
    n_neurons: int = 10
    n_hypotheses: int = 48
    n_visual_bins: int = 7
    max_categories: int = 28
    vigilance: float = 0.88
    exploration_start: float = 0.32
    exploration_end: float = 0.06
    reinforcement_lr: float = 0.22
    wm_persistence: float = 0.94
    motor_scale: float = 0.27
    soma_noise: float = 0.045
    apical_noise: float = 0.035
    initial_topdown_scale: float = 0.04
    outstar_lr: float = 0.075
    category_lr: float = 0.10
    basis_lr: float = 0.035
    motivated_gain: float = 0.75
    vector_lr: float = 0.11


@dataclass(frozen=True)
class Condition:
    algorithm: str = "part"
    topdown: str = "learned"
    plasticity: bool = True
    structural_credit: bool = True
    working_memory: bool = True
    motivated_attention: bool = True
    reset_search: bool = True
    resonance_gate: bool = True
    shuffled_topdown: bool = False
    suppress_apical_learning: bool = False
    suppress_apical_expression: bool = False
    plastic_basis: bool = False
    explicit_vector_error: bool = False


def random_patterns(rng: np.random.Generator, rows: int, cols: int) -> np.ndarray:
    patterns = rng.normal(0.0, 1.0, (rows, cols))
    patterns -= patterns.mean(axis=1, keepdims=True)
    patterns /= np.sqrt(np.mean(patterns**2, axis=1, keepdims=True)) + 1e-12
    return patterns


class Exp002Controller:
    """Shared controller with explicit, inspectable condition switches."""

    def __init__(self, cfg: LearnerConfig, condition: Condition, rng: np.random.Generator):
        self.cfg = cfg
        self.condition = condition
        self.rng = rng
        self.motor_basis = random_patterns(rng, cfg.n_hypotheses, cfg.n_neurons)
        independent = random_patterns(rng, cfg.n_hypotheses, cfg.n_neurons)
        self.topdown = cfg.initial_topdown_scale * independent
        self.initial_motor_basis = self.motor_basis.copy()
        self.initial_topdown = self.topdown.copy()
        self.shuffle = rng.permutation(cfg.n_neurons)
        self.values = np.zeros((cfg.max_categories, cfg.n_hypotheses))
        self.bandit_values = np.zeros((2, cfg.n_visual_bins, cfg.n_hypotheses))
        self.prototypes: list[np.ndarray] = []
        self.category_recruitments = 0
        self.total_resets = 0
        self.resonance_events = 0
        self.selection_events = 0
        self.trace: list[dict[str, object]] = []
        self.vector_policy = random_patterns(rng, 2, cfg.n_neurons)
        self.last_hypothesis = 0
        self.last_category = 0

    @staticmethod
    def _complement_code(observation: np.ndarray) -> np.ndarray:
        return np.r_[observation, 1.0 - observation]

    @staticmethod
    def _match(code: np.ndarray, prototype: np.ndarray) -> float:
        return float(1.0 - np.abs(code - prototype).mean())

    def _categorize(self, observation: np.ndarray, learn: bool) -> tuple[int, bool, int]:
        code = self._complement_code(observation)
        if not self.prototypes:
            self.prototypes.append(code.copy())
            self.category_recruitments += 1
            return 0, True, 0
        matches = np.asarray([self._match(code, prototype) for prototype in self.prototypes])
        order = list(np.argsort(matches)[::-1])
        chosen = order[0]
        resets = 0
        if self.condition.reset_search:
            while matches[chosen] < self.cfg.vigilance:
                resets += 1
                order.pop(0)
                if order:
                    chosen = order[0]
                    continue
                if len(self.prototypes) < self.cfg.max_categories and learn:
                    self.prototypes.append(code.copy())
                    self.category_recruitments += 1
                    return len(self.prototypes) - 1, True, resets
                chosen = int(np.argmax(matches))
                return chosen, False, resets
        resonant = bool(matches[chosen] >= self.cfg.vigilance)
        if learn and resonant:
            self.prototypes[chosen] += self.cfg.category_lr * (code - self.prototypes[chosen])
        return chosen, resonant, resets

    def start_episode(self) -> None:
        self.trace = []

    def _exploration(self, progress: float, evaluating: bool) -> float:
        if evaluating:
            return 0.0
        return self.cfg.exploration_start + progress * (
            self.cfg.exploration_end - self.cfg.exploration_start
        )

    def select(
        self,
        observation: np.ndarray,
        *,
        context: int,
        state_bin: int,
        progress: float,
        evaluating: bool,
    ) -> dict[str, object]:
        algorithm = self.condition.algorithm
        if algorithm == "part":
            category, resonant, resets = self._categorize(observation, learn=not evaluating)
            scores = self.values[category]
        else:
            category, resonant, resets = context * self.cfg.n_visual_bins + state_bin, True, 0
            scores = self.bandit_values[context, state_bin]

        epsilon = self._exploration(progress, evaluating)
        if algorithm == "random":
            hypothesis = int(self.rng.integers(self.cfg.n_hypotheses))
        elif self.condition.explicit_vector_error:
            hypothesis = context
        elif self.rng.random() < epsilon:
            hypothesis = int(self.rng.integers(self.cfg.n_hypotheses))
        else:
            hypothesis = int(np.argmax(scores + self.rng.normal(0.0, 1e-8, len(scores))))

        if self.condition.explicit_vector_error:
            motor_pattern = self.vector_policy[context]
        else:
            motor_pattern = self.motor_basis[hypothesis]
        soma = np.clip(
            0.5
            + self.cfg.motor_scale * motor_pattern
            + self.rng.normal(0.0, self.cfg.soma_noise, self.cfg.n_neurons),
            0.0,
            1.0,
        )

        if self.condition.topdown == "copy":
            apical_pattern = motor_pattern.copy()
        elif self.condition.topdown == "learned":
            apical_pattern = self.topdown[hypothesis].copy()
        elif self.condition.topdown == "vector":
            apical_pattern = self.vector_policy[context].copy()
        else:
            apical_pattern = np.zeros(self.cfg.n_neurons)
        if self.condition.shuffled_topdown:
            apical_pattern = apical_pattern[self.shuffle]
        if self.condition.suppress_apical_expression and evaluating:
            apical_pattern = np.zeros_like(apical_pattern)

        value = float(scores[hypothesis]) if hypothesis < len(scores) else 0.0
        gain = 1.0
        if self.condition.motivated_attention:
            gain += self.cfg.motivated_gain * max(0.0, value)
        apical = gain * apical_pattern + self.rng.normal(
            0.0, self.cfg.apical_noise, self.cfg.n_neurons
        )
        dendrite = 0.35 * soma + 0.20 * soma.mean() + apical

        self.trace.append({
            "hypothesis": hypothesis,
            "category": category,
            "context": context,
            "state_bin": state_bin,
            "resonant": resonant,
            "soma_target": soma - soma.mean(),
            "motor_pattern": motor_pattern.copy(),
        })
        self.last_hypothesis = hypothesis
        self.last_category = category
        self.total_resets += resets
        self.resonance_events += int(resonant)
        self.selection_events += 1
        return {
            "hypothesis": hypothesis,
            "category": category,
            "resonant": resonant,
            "resets": resets,
            "soma": soma,
            "apical": apical,
            "dendrite": dendrite,
            "topdown_pattern": apical_pattern,
            "motor_pattern": motor_pattern.copy(),
        }

    def delay(self, distractors: list[np.ndarray]) -> float:
        strength = 1.0
        for _ in distractors:
            strength *= self.cfg.wm_persistence
        if not self.condition.working_memory and self.trace:
            for item in self.trace:
                item["hypothesis"] = int(self.rng.integers(self.cfg.n_hypotheses))
                if self.condition.algorithm == "part":
                    item["category"] = int(self.rng.integers(max(1, len(self.prototypes))))
            strength = 1.0
        return strength

    def learn(
        self,
        *,
        global_improvement: float,
        reward: float,
        wm_strength: float,
        active_causal_for_positive_control: np.ndarray | None,
    ) -> None:
        if not self.condition.plasticity or not self.trace:
            return
        outcome = 0.80 * global_improvement + 0.20 * reward
        trace = self.trace
        if not self.condition.structural_credit:
            trace = [dict(item, hypothesis=int(self.rng.integers(self.cfg.n_hypotheses))) for item in trace]

        eligibility = 1.0
        for item in reversed(trace):
            hypothesis = int(item["hypothesis"])
            category = int(item["category"])
            context = int(item["context"])
            state_bin = int(item["state_bin"])
            gate = bool(item["resonant"]) or not self.condition.resonance_gate
            weight = wm_strength * eligibility
            eligibility *= 0.82

            if self.condition.motivated_attention and gate:
                if self.condition.algorithm == "part":
                    value = self.values[category, hypothesis]
                    self.values[category, hypothesis] += (
                        self.cfg.reinforcement_lr * weight * (outcome - value)
                    )
                elif self.condition.algorithm != "random":
                    value = self.bandit_values[context, state_bin, hypothesis]
                    self.bandit_values[context, state_bin, hypothesis] += (
                        self.cfg.reinforcement_lr * weight * (outcome - value)
                    )

            if (
                self.condition.topdown == "learned"
                and not self.condition.suppress_apical_learning
                and gate
            ):
                # Grossberg outstar principle: an active source samples the
                # distributed target activity. Reward never multiplies the
                # neuron-wise target. Motivated value only scales source gain.
                source_gain = 1.0
                if self.condition.motivated_attention:
                    source_gain += max(0.0, self.values[category, hypothesis])
                target = np.asarray(item["soma_target"])
                self.topdown[hypothesis] += (
                    self.cfg.outstar_lr * source_gain * weight
                    * (target - self.topdown[hypothesis])
                )

            if self.condition.plastic_basis and gate:
                # Corrected EXP001 probe: target is executed soma, not B_h itself.
                target = np.asarray(item["soma_target"])
                self.motor_basis[hypothesis] += (
                    self.cfg.basis_lr * weight * (target - self.motor_basis[hypothesis])
                )

        if self.condition.explicit_vector_error:
            if active_causal_for_positive_control is None:
                raise ValueError("vector positive control requires hidden causal roles")
            context = int(self.trace[-1]["context"])
            policy = self.vector_policy[context]
            policy += self.cfg.vector_lr * (active_causal_for_positive_control - policy)
            policy -= policy.mean()
            policy /= np.sqrt(np.mean(policy**2)) + 1e-12

    def phase_dendrites(self, selected: dict[str, object]) -> np.ndarray:
        """Five timing bins without multiplying an action pattern by task error."""
        soma = np.asarray(selected["soma"])
        apical = np.asarray(selected["apical"])
        base = 0.35 * soma + 0.20 * soma.mean()
        gains = np.asarray([0.90, 1.00, 0.95, 1.10, 0.85])
        return base[None, :] + gains[:, None] * apical[None, :]
