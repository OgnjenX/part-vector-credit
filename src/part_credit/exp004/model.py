"""ART/pART-inspired fixed-repertoire learner for EXP004."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .environment import TopologyTaskConfig


@dataclass(frozen=True)
class TopologyLearnerConfig:
    max_categories: int = 64
    vigilance: float = 0.86
    choice_alpha: float = 0.01
    category_lr: float = 0.15
    reinforcement_lr: float = 0.22
    outstar_lr: float = 0.10
    exploration_start: float = 0.65
    exploration_end: float = 0.05
    wm_persistence: float = 0.90
    eligibility_decay: float = 0.82
    motor_plasticity_lr: float = 4.0
    vector_lr: float = 0.18


@dataclass(frozen=True)
class TopologyCondition:
    algorithm: str = "art"
    learn_values: bool = True
    learn_topdown: bool = True
    category_recruitment: bool = True
    category_modification: bool = True
    fixed_categories: bool = False
    outcome_shuffled: bool = False
    random_reinforcement_target: bool = False
    motor_plasticity: bool = False
    explicit_vector_control: bool = False


class TopologyController:
    """Plastic categories/values/T over an otherwise fixed population-action bank."""

    def __init__(
        self,
        *,
        learner_cfg: TopologyLearnerConfig,
        task_cfg: TopologyTaskConfig,
        condition: TopologyCondition,
        motor_bank: np.ndarray,
        rng: np.random.Generator,
    ) -> None:
        self.cfg = learner_cfg
        self.task_cfg = task_cfg
        self.condition = condition
        self.rng = rng
        self.motor_basis = np.asarray(motor_bank, dtype=float).copy()
        self.initial_motor_basis = self.motor_basis.copy()
        self.n_hypotheses, self.n_neurons = self.motor_basis.shape
        self.n_bandit_states = (
            task_cfg.n_contexts * task_cfg.action_frames * task_cfg.state_bins
        )
        slots = max(learner_cfg.max_categories, self.n_bandit_states)
        self.values = np.zeros((slots, self.n_hypotheses), dtype=float)
        # Zero initialization makes every T exactly reachable from experienced targets.
        self.topdown = np.zeros(
            (slots, self.n_hypotheses, self.n_neurons), dtype=float
        )
        self.prototypes: list[np.ndarray] = []
        self.trace: list[dict[str, Any]] = []
        self.category_events: list[dict[str, Any]] = []
        self.topdown_updates: list[dict[str, Any]] = []
        self.value_updates: list[dict[str, Any]] = []
        self.motor_updates: list[dict[str, Any]] = []
        self.outcome_pool: list[float] = []
        self.total_resets = 0
        self.selection_events = 0
        self.recruitments = 0
        self.modifications = 0
        self.vector_motor = self.rng.normal(size=(task_cfg.n_contexts, self.n_neurons))
        self.vector_motor -= self.vector_motor.mean(axis=1, keepdims=True)
        self.vector_motor /= (
            np.max(np.abs(self.vector_motor), axis=1, keepdims=True) + 1e-12
        )
        if condition.fixed_categories:
            self._initialize_fixed_categories()
        elif condition.algorithm == "art" and not condition.category_recruitment:
            self._initialize_context_categories()

    @staticmethod
    def complement_code(observation: np.ndarray) -> np.ndarray:
        values = np.asarray(observation, dtype=float)
        return np.r_[values, 1.0 - values]

    @staticmethod
    def match(code: np.ndarray, prototype: np.ndarray) -> float:
        return float(np.minimum(code, prototype).sum() / (code.sum() + 1e-12))

    def _observation_template(
        self, context: int, frame: int, normalized_state: float
    ) -> np.ndarray:
        context_code = np.zeros(self.task_cfg.n_contexts)
        context_code[context] = 1.0
        phase = frame / max(1, self.task_cfg.action_frames - 1)
        return np.r_[context_code, phase, normalized_state]

    def _initialize_fixed_categories(self) -> None:
        for context in range(self.task_cfg.n_contexts):
            for frame in range(self.task_cfg.action_frames):
                for state_bin in range(self.task_cfg.state_bins):
                    normalized = state_bin / max(1, self.task_cfg.state_bins - 1)
                    code = self.complement_code(
                        self._observation_template(context, frame, normalized)
                    )
                    self.prototypes.append(code)
                    self.category_events.append({
                        "episode": -1,
                        "frame": -1,
                        "event": "fixed_initialize",
                        "category": len(self.prototypes) - 1,
                        "resets": 0,
                        "before": np.full_like(code, np.nan),
                        "after": code.copy(),
                        "delta_norm": 0.0,
                    })
        if len(self.prototypes) > self.cfg.max_categories:
            raise ValueError("max_categories is too small for fixed partition")

    def _initialize_context_categories(self) -> None:
        for context in range(self.task_cfg.n_contexts):
            code = self.complement_code(self._observation_template(context, 0, 0.0))
            self.prototypes.append(code)
            self.category_events.append({
                "episode": -1,
                "frame": -1,
                "event": "bootstrap",
                "category": len(self.prototypes) - 1,
                "resets": 0,
                "before": np.full_like(code, np.nan),
                "after": code.copy(),
                "delta_norm": 0.0,
            })

    def _bandit_category(self, context: int, frame: int, state_bin: int) -> int:
        return (
            context * self.task_cfg.action_frames * self.task_cfg.state_bins
            + frame * self.task_cfg.state_bins
            + state_bin
        )

    def _categorize(
        self,
        observation: np.ndarray,
        *,
        learn: bool,
        episode: int,
        frame: int,
    ) -> tuple[int, bool, int]:
        code = self.complement_code(observation)
        if not self.prototypes:
            self.prototypes.append(code.copy())
            self.recruitments += 1
            self.category_events.append({
                "episode": episode,
                "frame": frame,
                "event": "recruit",
                "category": 0,
                "resets": 0,
                "before": np.full_like(code, np.nan),
                "after": code.copy(),
                "delta_norm": 0.0,
            })
            return 0, True, 0
        choices = np.asarray([
            np.minimum(code, prototype).sum()
            / (self.cfg.choice_alpha + prototype.sum())
            for prototype in self.prototypes
        ])
        matches = np.asarray([self.match(code, prototype) for prototype in self.prototypes])
        order = list(np.argsort(choices)[::-1])
        resets = 0
        while order and matches[order[0]] < self.cfg.vigilance:
            order.pop(0)
            resets += 1
        if not order:
            can_recruit = (
                learn
                and self.condition.category_recruitment
                and len(self.prototypes) < self.cfg.max_categories
            )
            if can_recruit:
                self.prototypes.append(code.copy())
                category = len(self.prototypes) - 1
                self.recruitments += 1
                self.category_events.append({
                    "episode": episode,
                    "frame": frame,
                    "event": "recruit",
                    "category": category,
                    "resets": resets,
                    "before": np.full_like(code, np.nan),
                    "after": code.copy(),
                    "delta_norm": 0.0,
                })
                self.total_resets += resets
                return category, True, resets
            chosen = int(np.argmax(matches))
            self.total_resets += resets
            return chosen, False, resets
        chosen = int(order[0])
        resonant = bool(matches[chosen] >= self.cfg.vigilance)
        if learn and resonant and self.condition.category_modification:
            before = self.prototypes[chosen].copy()
            self.prototypes[chosen] += self.cfg.category_lr * (
                np.minimum(code, self.prototypes[chosen]) - self.prototypes[chosen]
            )
            delta = float(np.linalg.norm(self.prototypes[chosen] - before))
            self.modifications += int(delta > 1e-12)
            self.category_events.append({
                "episode": episode,
                "frame": frame,
                "event": "modify",
                "category": chosen,
                "resets": resets,
                "before": before,
                "after": self.prototypes[chosen].copy(),
                "delta_norm": delta,
            })
        self.total_resets += resets
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
        frame: int,
        state_bin: int,
        progress: float,
        evaluating: bool,
        episode: int,
    ) -> dict[str, Any]:
        if self.condition.algorithm == "art":
            category, resonant, resets = self._categorize(
                observation,
                learn=not evaluating,
                episode=episode,
                frame=frame,
            )
        else:
            category = self._bandit_category(context, frame, state_bin)
            resonant, resets = True, 0
        scores = self.values[category]
        epsilon = self._epsilon(progress, evaluating)
        if self.condition.algorithm == "random" or self.rng.random() < epsilon:
            hypothesis = int(self.rng.integers(self.n_hypotheses))
        else:
            jitter = self.rng.normal(0.0, 1e-10, self.n_hypotheses)
            hypothesis = int(np.argmax(scores + jitter))
        if self.condition.explicit_vector_control:
            motor = np.clip(0.5 + 0.15 * self.vector_motor[context], 0.2, 0.8)
        else:
            motor = self.motor_basis[hypothesis].copy()
        self.selection_events += 1
        return {
            "category": category,
            "hypothesis": hypothesis,
            "resonant": resonant,
            "resets": resets,
            "motor": motor,
            "value": float(scores[hypothesis]),
            "topdown": self.topdown[category, hypothesis].copy(),
        }

    def record_frame(
        self,
        selected: dict[str, Any],
        *,
        soma: np.ndarray,
        perturbation: np.ndarray,
        context: int,
        episode: int,
        frame: int,
    ) -> None:
        self.trace.append({
            "episode": episode,
            "frame": frame,
            "category": int(selected["category"]),
            "hypothesis": int(selected["hypothesis"]),
            "resonant": bool(selected["resonant"]),
            "soma": np.asarray(soma, dtype=float).copy(),
            "target": np.asarray(soma, dtype=float) - float(np.mean(soma)),
            "perturbation": np.asarray(perturbation, dtype=float).copy(),
            "context": int(context),
        })

    def delay_strength(self) -> float:
        return self.cfg.wm_persistence ** self.task_cfg.delay_steps

    def _credited_outcome(self, actual: float) -> float:
        if self.condition.outcome_shuffled:
            credited = (
                float(self.rng.choice(self.outcome_pool))
                if self.outcome_pool else 0.5
            )
            self.outcome_pool.append(float(actual))
            return credited
        self.outcome_pool.append(float(actual))
        return float(actual)

    def learn_outcome(
        self,
        *,
        outcome: float,
        hidden_role_positive_control: np.ndarray | None = None,
    ) -> dict[str, float]:
        credited_outcome = self._credited_outcome(outcome)
        eligibility = 1.0
        wm_strength = self.delay_strength()
        for item in reversed(self.trace):
            category = int(item["category"])
            selected_h = int(item["hypothesis"])
            hypothesis = (
                int(self.rng.integers(self.n_hypotheses))
                if self.condition.random_reinforcement_target else selected_h
            )
            strength = wm_strength * eligibility
            eligibility *= self.cfg.eligibility_decay
            value_before = float(self.values[category, hypothesis])
            if self.condition.learn_values and self.condition.algorithm != "random":
                self.values[category, hypothesis] += (
                    self.cfg.reinforcement_lr
                    * strength
                    * (credited_outcome - self.values[category, hypothesis])
                )
            value_after = float(self.values[category, hypothesis])
            self.value_updates.append({
                "episode": int(item["episode"]),
                "frame": int(item["frame"]),
                "category": category,
                "selected_hypothesis": selected_h,
                "credited_hypothesis": hypothesis,
                "actual_outcome": float(outcome),
                "credited_outcome": credited_outcome,
                "strength": strength,
                "before": value_before,
                "after": value_after,
            })
            if self.condition.learn_topdown and bool(item["resonant"]):
                gain = 1.0 + max(0.0, value_after)
                eta = self.cfg.outstar_lr * gain * strength
                target = np.asarray(item["target"])
                before = self.topdown[category, hypothesis].copy()
                self.topdown[category, hypothesis] += eta * (
                    target - self.topdown[category, hypothesis]
                )
                self.topdown_updates.append({
                    "episode": int(item["episode"]),
                    "frame": int(item["frame"]),
                    "category": category,
                    "selected_hypothesis": selected_h,
                    "credited_hypothesis": hypothesis,
                    "actual_outcome": float(outcome),
                    "credited_outcome": credited_outcome,
                    "strength": strength,
                    "eta_eff": eta,
                    "target": target.copy(),
                    "before": before,
                    "after": self.topdown[category, hypothesis].copy(),
                })
            if self.condition.motor_plasticity:
                perturbation = np.asarray(item["perturbation"])
                advantage = credited_outcome - value_before
                before = self.motor_basis[selected_h].copy()
                self.motor_basis[selected_h] += (
                    self.cfg.motor_plasticity_lr
                    * strength
                    * advantage
                    * perturbation
                )
                self.motor_basis[selected_h] = np.clip(
                    self.motor_basis[selected_h], 0.2, 0.8
                )
                self.motor_updates.append({
                    "episode": int(item["episode"]),
                    "frame": int(item["frame"]),
                    "hypothesis": selected_h,
                    "advantage": advantage,
                    "before": before,
                    "after": self.motor_basis[selected_h].copy(),
                })
        if self.condition.explicit_vector_control:
            if hidden_role_positive_control is None:
                raise ValueError("explicit vector control requires hidden role")
            context = int(self.trace[-1]["context"])
            target = np.asarray(hidden_role_positive_control, dtype=float)
            self.vector_motor[context] += self.cfg.vector_lr * (
                target - self.vector_motor[context]
            )
            self.vector_motor[context] = np.clip(self.vector_motor[context], -1.0, 1.0)
        return {
            "actual_outcome": float(outcome),
            "credited_outcome": credited_outcome,
            "wm_strength": wm_strength,
        }
