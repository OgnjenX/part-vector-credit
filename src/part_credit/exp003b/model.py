"""EXP003b category/hypothesis selection and learned expectancy abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class LearnerConfig:
    n_neurons: int = 8
    n_hypotheses: int = 16
    n_visual_bins: int = 7
    max_categories: int = 18
    vigilance: float = 0.88
    choice_alpha: float = 0.01
    category_lr: float = 0.12
    reinforcement_lr: float = 0.24
    outstar_lr: float = 0.09
    motor_basis_lr: float = 0.035
    generic_hebb_lr: float = 0.035
    exploration_start: float = 0.38
    exploration_end: float = 0.05
    wm_persistence: float = 0.90
    eligibility_decay: float = 0.82
    motivated_gain: float = 0.70
    initial_topdown_scale: float = 0.02
    topdown_target_scale: float = 0.45
    vector_lr: float = 0.16


@dataclass(frozen=True)
class Condition:
    algorithm: str = "part"
    learn_values: bool = True
    learn_topdown: bool = True
    express_topdown: bool = True
    smart_plasticity: bool = True
    topdown_to_smart: bool = True
    structural_credit: bool = True
    working_memory: bool = True
    motivated_attention: bool = True
    reset_search: bool = True
    resonance_gate: bool = True
    shuffled_topdown: bool = False
    suppress_expression_evaluation: bool = False
    direct_copy_apical: bool = False
    generic_hebb: bool = False
    plastic_motor_basis: bool = False
    explicit_vector_credit: bool = False


def random_motor_basis(
    rng: np.random.Generator, rows: int, cols: int
) -> np.ndarray:
    pairs = rows // 2
    directions = rng.normal(size=(pairs, cols))
    directions -= directions.mean(axis=1, keepdims=True)
    directions /= np.max(np.abs(directions), axis=1, keepdims=True) + 1e-12
    raw = np.concatenate((directions, -directions), axis=0)
    if rows % 2:
        extra = rng.normal(size=(1, cols))
        extra -= extra.mean(axis=1, keepdims=True)
        extra /= np.max(np.abs(extra), axis=1, keepdims=True) + 1e-12
        raw = np.concatenate((raw, extra), axis=0)
    return 0.825 + 0.275 * raw


class Exp003bController:
    """Explicit category-hypothesis state with delayed scalar reinforcement."""

    def __init__(
        self,
        cfg: LearnerConfig,
        condition: Condition,
        rng: np.random.Generator,
    ) -> None:
        self.cfg = cfg
        self.condition = condition
        self.rng = rng
        self.motor_basis = random_motor_basis(
            rng, cfg.n_hypotheses, cfg.n_neurons
        )
        self.initial_motor_basis = self.motor_basis.copy()
        self.topdown = rng.normal(
            0.0,
            cfg.initial_topdown_scale,
            (cfg.max_categories, cfg.n_hypotheses, cfg.n_neurons),
        )
        self.topdown -= self.topdown.mean(axis=2, keepdims=True)
        self.initial_topdown = self.topdown.copy()
        self.lower_weights = np.full(
            (cfg.n_hypotheses, cfg.n_neurons), 0.60, dtype=float
        )
        self.initial_lower_weights = self.lower_weights.copy()
        self.values = np.zeros((cfg.max_categories, cfg.n_hypotheses))
        self.bandit_values = np.zeros(
            (2, cfg.n_visual_bins, cfg.n_hypotheses)
        )
        self.prototypes: list[np.ndarray] = []
        self.trace: list[dict[str, Any]] = []
        self.shuffle = rng.permutation(cfg.n_neurons)
        self.vector_motor = rng.normal(size=(2, cfg.n_neurons))
        self.vector_motor -= self.vector_motor.mean(axis=1, keepdims=True)
        self.vector_motor /= (
            np.max(np.abs(self.vector_motor), axis=1, keepdims=True) + 1e-12
        )
        self.category_recruitments = 0
        self.total_resets = 0
        self.resonance_events = 0
        self.selection_events = 0

    @staticmethod
    def _complement_code(observation: np.ndarray) -> np.ndarray:
        observation = np.asarray(observation, dtype=float)
        return np.r_[observation, 1.0 - observation]

    @staticmethod
    def _match(code: np.ndarray, prototype: np.ndarray) -> float:
        return float(np.minimum(code, prototype).sum() / (code.sum() + 1e-12))

    def _categorize(
        self, observation: np.ndarray, *, learn: bool
    ) -> tuple[int, bool, int]:
        code = self._complement_code(observation)
        if not self.prototypes:
            self.prototypes.append(code.copy())
            self.category_recruitments += 1
            return 0, True, 0
        choices = np.asarray([
            np.minimum(code, prototype).sum()
            / (self.cfg.choice_alpha + prototype.sum())
            for prototype in self.prototypes
        ])
        matches = np.asarray([
            self._match(code, prototype) for prototype in self.prototypes
        ])
        order = list(np.argsort(choices)[::-1])
        resets = 0
        if self.condition.reset_search:
            while order and matches[order[0]] < self.cfg.vigilance:
                order.pop(0)
                resets += 1
            if not order:
                if learn and len(self.prototypes) < self.cfg.max_categories:
                    self.prototypes.append(code.copy())
                    self.category_recruitments += 1
                    return len(self.prototypes) - 1, True, resets
                chosen = int(np.argmax(matches))
                return chosen, False, resets
        chosen = int(order[0] if order else np.argmax(choices))
        resonant = bool(matches[chosen] >= self.cfg.vigilance)
        if learn and resonant:
            self.prototypes[chosen] += self.cfg.category_lr * (
                np.minimum(code, self.prototypes[chosen]) - self.prototypes[chosen]
            )
        return chosen, resonant, resets

    def start_episode(self) -> None:
        self.trace = []

    def _epsilon(self, progress: float, evaluating: bool) -> float:
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
    ) -> dict[str, Any]:
        if self.condition.algorithm == "part":
            category, resonant, resets = self._categorize(
                observation, learn=not evaluating
            )
            scores = self.values[category]
        else:
            category = context * self.cfg.n_visual_bins + state_bin
            resonant, resets = True, 0
            scores = self.bandit_values[context, state_bin]

        epsilon = self._epsilon(progress, evaluating)
        if self.condition.algorithm == "random":
            hypothesis = int(self.rng.integers(self.cfg.n_hypotheses))
        elif self.condition.explicit_vector_credit:
            hypothesis = context
        elif self.rng.random() < epsilon:
            hypothesis = int(self.rng.integers(self.cfg.n_hypotheses))
        else:
            jitter = self.rng.normal(0.0, 1e-9, self.cfg.n_hypotheses)
            hypothesis = int(np.argmax(scores + jitter))

        if self.condition.explicit_vector_credit:
            motor = np.clip(
                0.825 + 0.275 * self.vector_motor[context], 0.55, 1.10
            )
        else:
            motor = self.motor_basis[hypothesis].copy()

        learned = self.topdown[category, hypothesis].copy()
        if self.condition.direct_copy_apical:
            raw_topdown = motor - motor.mean()
        elif self.condition.express_topdown:
            raw_topdown = learned
        else:
            raw_topdown = np.zeros(self.cfg.n_neurons)
        if self.condition.shuffled_topdown:
            raw_topdown = raw_topdown[self.shuffle]
        if self.condition.suppress_expression_evaluation and evaluating:
            raw_topdown = np.zeros_like(raw_topdown)

        value = float(scores[hypothesis])
        source_gain = 1.0
        if self.condition.motivated_attention:
            source_gain += self.cfg.motivated_gain * max(0.0, value)
        raw_topdown = source_gain * raw_topdown
        topdown_profile = np.clip(
            raw_topdown / self.cfg.topdown_target_scale, 0.0, 1.0
        )
        if not self.condition.topdown_to_smart:
            circuit_topdown = np.zeros_like(topdown_profile)
        else:
            circuit_topdown = topdown_profile

        self.total_resets += resets
        self.resonance_events += int(resonant)
        self.selection_events += 1
        return {
            "category": category,
            "hypothesis": hypothesis,
            "resonant": resonant,
            "resets": resets,
            "motor": motor,
            "raw_topdown": raw_topdown,
            "topdown_profile": topdown_profile,
            "circuit_topdown": circuit_topdown,
            "value": value,
        }

    def record_frame(
        self,
        selected: dict[str, Any],
        *,
        soma: np.ndarray,
        weight_before: np.ndarray,
        weight_after: np.ndarray,
        context: int,
        state_bin: int,
    ) -> None:
        self.trace.append({
            "category": int(selected["category"]),
            "hypothesis": int(selected["hypothesis"]),
            "resonant": bool(selected["resonant"]),
            "soma": np.asarray(soma).copy(),
            "soma_target": np.asarray(soma) - float(np.mean(soma)),
            "weight_before": np.asarray(weight_before).copy(),
            "weight_after": np.asarray(weight_after).copy(),
            "context": context,
            "state_bin": state_bin,
        })

    def delay(self, distractors: list[np.ndarray]) -> float:
        strength = self.cfg.wm_persistence ** len(distractors)
        if not self.condition.working_memory:
            for item in self.trace:
                item["category"] = int(self.rng.integers(self.cfg.max_categories))
                item["hypothesis"] = int(self.rng.integers(self.cfg.n_hypotheses))
            return 1.0
        return strength

    def learn_outcome(
        self,
        *,
        global_improvement: float,
        reward: float,
        wm_strength: float,
        hidden_causal_positive_control: np.ndarray | None,
    ) -> None:
        if not self.trace:
            return
        outcome = 0.80 * global_improvement + 0.20 * reward
        trace = self.trace
        if not self.condition.structural_credit:
            trace = [
                dict(
                    item,
                    category=int(self.rng.integers(self.cfg.max_categories)),
                    hypothesis=int(self.rng.integers(self.cfg.n_hypotheses)),
                )
                for item in trace
            ]

        eligibility = 1.0
        for item in reversed(trace):
            category = int(item["category"])
            hypothesis = int(item["hypothesis"])
            context = int(item["context"])
            state_bin = int(item["state_bin"])
            gate = bool(item["resonant"]) or not self.condition.resonance_gate
            strength = wm_strength * eligibility
            eligibility *= self.cfg.eligibility_decay

            if self.condition.learn_values and self.condition.algorithm != "random":
                if self.condition.algorithm == "part":
                    old = self.values[category, hypothesis]
                    self.values[category, hypothesis] += (
                        self.cfg.reinforcement_lr * strength * (outcome - old)
                    )
                else:
                    old = self.bandit_values[context, state_bin, hypothesis]
                    self.bandit_values[context, state_bin, hypothesis] += (
                        self.cfg.reinforcement_lr * strength * (outcome - old)
                    )

            if self.condition.learn_topdown and gate:
                source_gain = 1.0
                if self.condition.motivated_attention:
                    source_gain += max(0.0, self.values[category, hypothesis])
                target = np.asarray(item["soma_target"])
                self.topdown[category, hypothesis] += (
                    self.cfg.outstar_lr
                    * source_gain
                    * strength
                    * (target - self.topdown[category, hypothesis])
                )

            if self.condition.generic_hebb:
                target = np.asarray(item["soma"])
                current = self.lower_weights[hypothesis]
                potentiation = target * (1.0 - current)
                depression = (1.0 - target) * (current - 0.05)
                self.lower_weights[hypothesis] += (
                    self.cfg.generic_hebb_lr
                    * strength
                    * max(0.0, outcome)
                    * (potentiation - 0.10 * depression)
                )
                self.lower_weights[hypothesis] = np.clip(
                    self.lower_weights[hypothesis], 0.05, 1.0
                )

            if self.condition.plastic_motor_basis and gate:
                target = 0.825 + 0.275 * np.asarray(item["soma_target"])
                self.motor_basis[hypothesis] += (
                    self.cfg.motor_basis_lr
                    * strength
                    * (target - self.motor_basis[hypothesis])
                )
                self.motor_basis[hypothesis] = np.clip(
                    self.motor_basis[hypothesis], 0.55, 1.10
                )

        if self.condition.explicit_vector_credit:
            if hidden_causal_positive_control is None:
                raise ValueError("positive control requires the hidden causal vector")
            context = int(self.trace[-1]["context"])
            target = np.asarray(hidden_causal_positive_control, dtype=float)
            self.vector_motor[context] += self.cfg.vector_lr * (
                target - self.vector_motor[context]
            )
            self.vector_motor[context] = np.clip(
                self.vector_motor[context], -1.0, 1.0
            )
            hypothesis = context
            self.lower_weights[hypothesis] = np.clip(
                self.lower_weights[hypothesis]
                + self.cfg.vector_lr * 0.10 * target,
                0.05,
                1.0,
            )
