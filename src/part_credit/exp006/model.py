"""Learners compared in the EXP006 common benchmark."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class LearnerConfig:
    motor_amplitude: float = 0.20
    repertoire_size: int = 64
    max_categories: int = 96
    vigilance: float = 0.84
    choice_alpha: float = 0.01
    category_lr: float = 0.12
    value_lr: float = 0.18
    outstar_lr: float = 0.10
    reward_trace_decay: float = 0.92
    exploration_start: float = 0.55
    exploration_end: float = 0.04
    perturbation_sd: float = 0.08
    eligibility_decay: float = 0.88
    visual_learning_rate: float = 0.0012
    reward_learning_rate: float = 0.0008
    correction_bound: float = 0.28
    baseline_rate: float = 0.03
    oracle_lr: float = 0.08
    oracle_exploration_sd: float = 0.025
    hybrid_art_gain: float = 0.55
    hybrid_eligibility_gain: float = 1.0


@dataclass(frozen=True)
class Condition:
    name: str
    shuffle_modulators: bool = False
    exploration: bool = True
    temporal_eligibility: bool = True
    eligibility_plasticity: bool = True


@dataclass
class Action:
    soma: np.ndarray
    deterministic: np.ndarray
    perturbation: np.ndarray
    prior_feedback: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)


def safe_center(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    return array - float(np.mean(array))


def safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.size < 2 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def random_balanced_repertoire(
    rng: np.random.Generator,
    *,
    n_neurons: int,
    size: int,
    amplitude: float,
) -> np.ndarray:
    """Create hidden-role-independent antithetic balanced motor patterns."""
    if size % 2:
        raise ValueError("repertoire size must be even")
    pairs: list[np.ndarray] = []
    seen: set[bytes] = set()
    attempts = 0
    while len(pairs) < size // 2:
        attempts += 1
        if attempts > 100_000:
            raise ValueError("requested repertoire exceeds unique balanced patterns")
        direction = np.r_[np.ones(n_neurons // 2), -np.ones(n_neurons // 2)]
        direction = direction[rng.permutation(n_neurons)].astype(float)
        canonical = min(direction.tobytes(), (-direction).tobytes())
        if canonical in seen:
            continue
        seen.add(canonical)
        pairs.append(direction)
    directions = np.stack([signed for row in pairs for signed in (row, -row)])
    directions = directions[rng.permutation(directions.shape[0])]
    return np.clip(0.5 + amplitude * directions, 0.0, 1.0)


class ARTCore:
    """Fuzzy-ART categories with value selection and outstar expectancy."""

    def __init__(
        self,
        bank: np.ndarray,
        cfg: LearnerConfig,
        condition: Condition,
        rng: np.random.Generator,
    ) -> None:
        self.bank = np.asarray(bank, dtype=float).copy()
        self.cfg = cfg
        self.condition = condition
        self.rng = rng
        self.prototypes: list[np.ndarray] = []
        self.values = np.zeros((cfg.max_categories, self.bank.shape[0]), dtype=float)
        self.topdown = np.zeros(
            (cfg.max_categories, self.bank.shape[0], self.bank.shape[1]),
            dtype=float,
        )
        self.trace: list[dict[str, Any]] = []
        self.modulator_pool: list[float] = []
        self.category_events = 0
        self.reset_count = 0

    @staticmethod
    def complement_code(observation: np.ndarray) -> np.ndarray:
        obs = np.clip(np.asarray(observation, dtype=float), 0.0, 1.0)
        return np.r_[obs, 1.0 - obs]

    @staticmethod
    def match(code: np.ndarray, prototype: np.ndarray) -> float:
        return float(np.minimum(code, prototype).sum() / (code.sum() + 1e-12))

    def _category(self, observation: np.ndarray, *, learn: bool) -> tuple[int, bool]:
        code = self.complement_code(observation)
        if not self.prototypes:
            if not learn:
                return 0, False
            self.prototypes.append(code.copy())
            self.category_events += 1
            return 0, True
        choices = np.asarray([
            np.minimum(code, prototype).sum()
            / (self.cfg.choice_alpha + prototype.sum())
            for prototype in self.prototypes
        ])
        matches = np.asarray([self.match(code, row) for row in self.prototypes])
        order = list(np.argsort(choices)[::-1])
        resets = 0
        while order and matches[order[0]] < self.cfg.vigilance:
            order.pop(0)
            resets += 1
        self.reset_count += resets
        if not order:
            if learn and len(self.prototypes) < self.cfg.max_categories:
                self.prototypes.append(code.copy())
                self.category_events += 1
                return len(self.prototypes) - 1, True
            return int(np.argmax(matches)), False
        category = int(order[0])
        if learn:
            self.prototypes[category] += self.cfg.category_lr * (
                np.minimum(code, self.prototypes[category]) - self.prototypes[category]
            )
        return category, True

    def start_trial(self) -> None:
        self.trace = []

    def _epsilon(self, progress: float) -> float:
        return self.cfg.exploration_start + progress * (
            self.cfg.exploration_end - self.cfg.exploration_start
        )

    def select(self, observation: np.ndarray, progress: float) -> Action:
        category, resonant = self._category(observation, learn=True)
        if self.rng.random() < self._epsilon(progress):
            hypothesis = int(self.rng.integers(self.bank.shape[0]))
        else:
            jitter = self.rng.normal(0.0, 1e-10, self.bank.shape[0])
            hypothesis = int(np.argmax(self.values[category] + jitter))
        deterministic = self.bank[hypothesis].copy()
        feedback = self.topdown[category, hypothesis].copy()
        action = Action(
            soma=deterministic.copy(),
            deterministic=deterministic,
            perturbation=np.zeros(self.bank.shape[1]),
            prior_feedback=feedback,
            metadata={
                "category": category,
                "hypothesis": hypothesis,
                "resonant": resonant,
                "observation": np.asarray(observation, dtype=float).copy(),
            },
        )
        self.trace.append({"action": action})
        return action

    def _assigned_modulator(self, value: float) -> float:
        actual = float(value)
        if self.condition.shuffle_modulators:
            if self.modulator_pool:
                index = int(self.rng.integers(len(self.modulator_pool)))
                assigned = float(self.modulator_pool[index])
            else:
                assigned = 0.0
        else:
            assigned = actual
        self.modulator_pool.append(actual)
        return assigned

    def learn_transition(self, action: Action, visible_score: float) -> np.ndarray:
        category = int(action.metadata["category"])
        hypothesis = int(action.metadata["hypothesis"])
        assigned = self._assigned_modulator(visible_score)
        before = float(self.values[category, hypothesis])
        self.values[category, hypothesis] += self.cfg.value_lr * (assigned - before)
        if bool(action.metadata["resonant"]):
            eta = self.cfg.outstar_lr * max(0.0, assigned)
            target = safe_center(action.soma)
            self.topdown[category, hypothesis] += eta * (
                target - self.topdown[category, hypothesis]
            )
        return action.prior_feedback.copy()

    def end_trial(self, reward: float) -> np.ndarray:
        assigned = self._assigned_modulator(reward)
        eligibility = 1.0
        combined = np.zeros(self.bank.shape[1], dtype=float)
        for row in reversed(self.trace):
            action = row["action"]
            category = int(action.metadata["category"])
            hypothesis = int(action.metadata["hypothesis"])
            value = float(self.values[category, hypothesis])
            self.values[category, hypothesis] += (
                self.cfg.value_lr * eligibility * (assigned - value)
            )
            if bool(action.metadata["resonant"]):
                eta = self.cfg.outstar_lr * eligibility * max(0.0, assigned)
                target = safe_center(action.soma)
                self.topdown[category, hypothesis] += eta * (
                    target - self.topdown[category, hypothesis]
                )
            combined += eligibility * action.prior_feedback
            eligibility *= self.cfg.reward_trace_decay
        return safe_center(combined)

    def representative_action(self, observation: np.ndarray) -> np.ndarray:
        if not self.prototypes:
            return self.bank[0].copy()
        code = self.complement_code(observation)
        matches = np.asarray([self.match(code, row) for row in self.prototypes])
        category = int(np.argmax(matches))
        hypothesis = int(np.argmax(self.values[category]))
        return self.bank[hypothesis].copy()


class EligibilityMechanism:
    """Local perturbation trace and scalar modulators for a motor correction."""

    def __init__(
        self,
        n_neurons: int,
        cfg: LearnerConfig,
        condition: Condition,
        rng: np.random.Generator,
    ) -> None:
        self.cfg = cfg
        self.condition = condition
        self.rng = rng
        initial = rng.normal(0.0, 0.004, n_neurons)
        self.correction = safe_center(initial)
        self.eligibility = np.zeros(n_neurons, dtype=float)
        self.visual_baseline = 0.0
        self.reward_baseline = 0.0
        self.modulator_pool: list[float] = []
        self.update_log: list[dict[str, np.ndarray | float]] = []

    def start_trial(self) -> None:
        self.eligibility.fill(0.0)

    def emit(self, base: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        deterministic = np.clip(base + self.correction, 0.0, 1.0)
        if self.condition.exploration:
            proposed = safe_center(
                self.rng.normal(0.0, self.cfg.perturbation_sd, deterministic.size)
            )
        else:
            proposed = np.zeros_like(deterministic)
        soma = np.clip(deterministic + proposed, 0.0, 1.0)
        perturbation = soma - deterministic
        if self.condition.temporal_eligibility:
            self.eligibility = (
                self.cfg.eligibility_decay * self.eligibility
                + perturbation / (self.cfg.perturbation_sd**2)
            )
        return soma, deterministic, perturbation

    def _assigned_modulator(self, value: float) -> float:
        actual = float(value)
        if self.condition.shuffle_modulators:
            if self.modulator_pool:
                index = int(self.rng.integers(len(self.modulator_pool)))
                assigned = float(self.modulator_pool[index])
            else:
                assigned = 0.0
        else:
            assigned = actual
        self.modulator_pool.append(actual)
        return assigned

    def _apply(self, modulator: float, rate: float) -> np.ndarray:
        before = self.correction.copy()
        drive = modulator * self.eligibility
        if self.condition.eligibility_plasticity:
            self.correction += rate * drive
            self.correction = np.clip(
                safe_center(self.correction),
                -self.cfg.correction_bound,
                self.cfg.correction_bound,
            )
            self.correction = safe_center(self.correction)
        self.update_log.append({
            "modulator": float(modulator),
            "eligibility": self.eligibility.copy(),
            "before": before,
            "delta": self.correction - before,
            "after": self.correction.copy(),
        })
        return drive

    def observe_visible(self, visible_score: float) -> np.ndarray:
        assigned = self._assigned_modulator(visible_score)
        advantage = assigned - self.visual_baseline
        drive = self._apply(advantage, self.cfg.visual_learning_rate)
        self.visual_baseline += self.cfg.baseline_rate * (
            assigned - self.visual_baseline
        )
        return drive

    def end_trial(self, reward: float) -> np.ndarray:
        assigned = self._assigned_modulator(reward)
        advantage = assigned - self.reward_baseline
        drive = self._apply(advantage, self.cfg.reward_learning_rate)
        self.reward_baseline += self.cfg.baseline_rate * (
            assigned - self.reward_baseline
        )
        return drive


class ARTRepertoireLearner:
    def __init__(
        self,
        bank: np.ndarray,
        cfg: LearnerConfig,
        condition: Condition,
        rng: np.random.Generator,
    ) -> None:
        self.art = ARTCore(bank, cfg, condition, rng)
        self.bank = np.asarray(bank, dtype=float)

    def start_trial(self) -> None:
        self.art.start_trial()

    def act(self, observation: np.ndarray, progress: float) -> Action:
        return self.art.select(observation, progress)

    def observe_transition(self, action: Action, visible_score: float) -> np.ndarray:
        feedback = self.art.learn_transition(action, visible_score)
        action.metadata["feedback_art"] = feedback.copy()
        action.metadata["feedback_eligibility"] = np.zeros_like(feedback)
        action.metadata["feedback_vector"] = np.zeros_like(feedback)
        return feedback

    def end_trial(self, reward: float) -> np.ndarray:
        feedback = self.art.end_trial(reward)
        self.last_post_components = {
            "art": feedback.copy(),
            "eligibility": np.zeros_like(feedback),
            "vector": np.zeros_like(feedback),
        }
        return feedback

    def representative_action(self, observation: np.ndarray) -> np.ndarray:
        return self.art.representative_action(observation)


class LocalEligibilityLearner:
    def __init__(
        self,
        n_neurons: int,
        cfg: LearnerConfig,
        condition: Condition,
        rng: np.random.Generator,
    ) -> None:
        self.mechanism = EligibilityMechanism(n_neurons, cfg, condition, rng)
        self.base = np.full(n_neurons, 0.5)

    def start_trial(self) -> None:
        self.mechanism.start_trial()

    def act(self, observation: np.ndarray, progress: float) -> Action:
        del observation, progress
        soma, deterministic, perturbation = self.mechanism.emit(self.base)
        return Action(soma, deterministic, perturbation, np.zeros_like(soma))

    def observe_transition(self, action: Action, visible_score: float) -> np.ndarray:
        feedback = self.mechanism.observe_visible(visible_score)
        action.metadata["feedback_art"] = np.zeros_like(feedback)
        action.metadata["feedback_eligibility"] = feedback.copy()
        action.metadata["feedback_vector"] = np.zeros_like(feedback)
        return feedback

    def end_trial(self, reward: float) -> np.ndarray:
        feedback = self.mechanism.end_trial(reward)
        self.last_post_components = {
            "art": np.zeros_like(feedback),
            "eligibility": feedback.copy(),
            "vector": np.zeros_like(feedback),
        }
        return feedback

    def representative_action(self, observation: np.ndarray) -> np.ndarray:
        del observation
        return np.clip(self.base + self.mechanism.correction, 0.0, 1.0)


class HybridLearner:
    def __init__(
        self,
        bank: np.ndarray,
        cfg: LearnerConfig,
        condition: Condition,
        art_rng: np.random.Generator,
        eligibility_rng: np.random.Generator,
    ) -> None:
        self.cfg = cfg
        self.art = ARTCore(bank, cfg, condition, art_rng)
        self.mechanism = EligibilityMechanism(
            bank.shape[1], cfg, condition, eligibility_rng
        )

    def start_trial(self) -> None:
        self.art.start_trial()
        self.mechanism.start_trial()

    def act(self, observation: np.ndarray, progress: float) -> Action:
        selected = self.art.select(observation, progress)
        soma, deterministic, perturbation = self.mechanism.emit(selected.deterministic)
        selected.soma = soma
        selected.deterministic = deterministic
        selected.perturbation = perturbation
        return selected

    def observe_transition(self, action: Action, visible_score: float) -> np.ndarray:
        art_feedback = self.art.learn_transition(action, visible_score)
        eligibility_feedback = self.mechanism.observe_visible(visible_score)
        action.metadata["feedback_art"] = art_feedback.copy()
        action.metadata["feedback_eligibility"] = eligibility_feedback.copy()
        action.metadata["feedback_vector"] = np.zeros_like(art_feedback)
        return (
            self.cfg.hybrid_art_gain * art_feedback
            + self.cfg.hybrid_eligibility_gain * eligibility_feedback
        )

    def end_trial(self, reward: float) -> np.ndarray:
        art_feedback = self.art.end_trial(reward)
        eligibility_feedback = self.mechanism.end_trial(reward)
        self.last_post_components = {
            "art": art_feedback.copy(),
            "eligibility": eligibility_feedback.copy(),
            "vector": np.zeros_like(art_feedback),
        }
        return (
            self.cfg.hybrid_art_gain * art_feedback
            + self.cfg.hybrid_eligibility_gain * eligibility_feedback
        )

    def representative_action(self, observation: np.ndarray) -> np.ndarray:
        base = self.art.representative_action(observation)
        return np.clip(base + self.mechanism.correction, 0.0, 1.0)


class VectorOracle:
    """Privileged task-sensitivity control; hidden role is accepted only here."""

    def __init__(
        self,
        role: np.ndarray,
        cfg: LearnerConfig,
        rng: np.random.Generator,
    ) -> None:
        self.role = np.asarray(role, dtype=float).copy()
        self.cfg = cfg
        self.rng = rng
        self.weights = np.zeros_like(self.role)
        self.last_perturbation = np.zeros_like(self.role)

    def set_role(self, role: np.ndarray) -> None:
        self.role = np.asarray(role, dtype=float).copy()

    def start_trial(self) -> None:
        pass

    def act(self, observation: np.ndarray, progress: float) -> Action:
        del observation, progress
        deterministic = np.clip(0.5 + self.cfg.motor_amplitude * self.weights, 0.0, 1.0)
        perturbation = safe_center(
            self.rng.normal(0.0, self.cfg.oracle_exploration_sd, self.weights.size)
        )
        soma = np.clip(deterministic + perturbation, 0.0, 1.0)
        self.last_perturbation = soma - deterministic
        return Action(soma, deterministic, self.last_perturbation, self.role.copy())

    def observe_transition(self, action: Action, visible_score: float) -> np.ndarray:
        direction = float(np.sign(visible_score))
        feedback = direction * self.role
        action.metadata["feedback_art"] = np.zeros_like(feedback)
        action.metadata["feedback_eligibility"] = np.zeros_like(feedback)
        action.metadata["feedback_vector"] = feedback.copy()
        return feedback

    def end_trial(self, reward: float) -> np.ndarray:
        self.weights += self.cfg.oracle_lr * (self.role - self.weights)
        self.weights = np.clip(self.weights, -1.0, 1.0)
        feedback = (2.0 * reward - 1.0) * self.role
        self.last_post_components = {
            "art": np.zeros_like(feedback),
            "eligibility": np.zeros_like(feedback),
            "vector": feedback.copy(),
        }
        return feedback

    def representative_action(self, observation: np.ndarray) -> np.ndarray:
        del observation
        return np.clip(0.5 + self.cfg.motor_amplitude * self.weights, 0.0, 1.0)


class RandomNoLearning:
    def __init__(self, n_neurons: int, rng: np.random.Generator) -> None:
        self.motor = np.clip(0.5 + safe_center(rng.normal(0.0, 0.03, n_neurons)), 0.0, 1.0)

    def start_trial(self) -> None:
        pass

    def act(self, observation: np.ndarray, progress: float) -> Action:
        del observation, progress
        zeros = np.zeros_like(self.motor)
        return Action(self.motor.copy(), self.motor.copy(), zeros, zeros)

    def observe_transition(self, action: Action, visible_score: float) -> np.ndarray:
        del visible_score
        feedback = np.zeros_like(action.soma)
        action.metadata["feedback_art"] = feedback.copy()
        action.metadata["feedback_eligibility"] = feedback.copy()
        action.metadata["feedback_vector"] = feedback.copy()
        return feedback

    def end_trial(self, reward: float) -> np.ndarray:
        del reward
        feedback = np.zeros_like(self.motor)
        self.last_post_components = {
            "art": feedback.copy(),
            "eligibility": feedback.copy(),
            "vector": feedback.copy(),
        }
        return feedback

    def representative_action(self, observation: np.ndarray) -> np.ndarray:
        del observation
        return self.motor.copy()
