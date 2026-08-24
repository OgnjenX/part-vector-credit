"""Generic node-perturbation comparator; this is not a Grossberg model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class LearnerConfig:
    learning_rate: float = 0.0015
    oracle_learning_rate: float = 0.012
    perturbation_sd: float = 0.10
    initial_weight_sd: float = 0.008
    weight_bound: float = 0.30
    eligibility_decay: float = 0.80
    baseline_rate: float = 0.08
    batch_size: int = 16
    learning_rate_reference_neurons: int = 32


@dataclass(frozen=True)
class Condition:
    name: str
    plasticity: bool = True
    exploration: bool = True
    temporal_eligibility: bool = True
    shuffle_outcomes: bool = False
    hidden_vector_oracle: bool = False
    zero_initial_topology: bool = False


class GenericNodePerturbationLearner:
    """A class-D three-factor learner using only local perturbation and scalar reward."""

    def __init__(
        self,
        n_neurons: int,
        cfg: LearnerConfig,
        condition: Condition,
        rng: np.random.Generator,
    ) -> None:
        if condition.hidden_vector_oracle:
            raise ValueError("use HiddenVectorOracle for privileged information")
        self.cfg = cfg
        self.condition = condition
        self.effective_learning_rate = (
            cfg.learning_rate * n_neurons / cfg.learning_rate_reference_neurons
        )
        weights = (
            np.zeros(n_neurons)
            if condition.zero_initial_topology
            else rng.normal(0.0, cfg.initial_weight_sd, n_neurons)
        )
        self.weights = weights - weights.mean()
        self.baseline = 0.0
        self._eligibility = np.zeros(n_neurons, dtype=float)
        self._pending: list[dict[str, Any]] = []
        self.update_log: list[dict[str, Any]] = []

    def start_episode(self) -> None:
        self._eligibility.fill(0.0)

    def emit(self, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        deterministic = np.clip(0.5 + self.weights, 0.0, 1.0)
        if self.condition.exploration:
            proposed = rng.normal(0.0, self.cfg.perturbation_sd, self.weights.size)
            proposed -= proposed.mean()
        else:
            proposed = np.zeros_like(self.weights)
        soma = np.clip(deterministic + proposed, 0.0, 1.0)
        perturbation = soma - deterministic
        if self.condition.temporal_eligibility:
            self._eligibility = (
                self.cfg.eligibility_decay * self._eligibility
                + perturbation / (self.cfg.perturbation_sd**2)
            )
        return soma, perturbation

    def close_episode(self, reward: float, episode: int) -> None:
        self._pending.append({
            "episode": episode,
            "reward": float(reward),
            "eligibility": self._eligibility.copy(),
        })

    def batch_ready(self) -> bool:
        return len(self._pending) >= self.cfg.batch_size

    def apply_pending(self, rng: np.random.Generator) -> None:
        if not self._pending:
            return
        rewards = np.asarray([row["reward"] for row in self._pending], dtype=float)
        assigned = rewards.copy()
        if self.condition.shuffle_outcomes and assigned.size > 1:
            assigned = assigned[rng.permutation(assigned.size)]
        for row, assigned_reward in zip(self._pending, assigned, strict=True):
            advantage = float(assigned_reward - self.baseline)
            before = self.weights.copy()
            if self.condition.plasticity:
                proposed_delta = (
                    self.effective_learning_rate * advantage * row["eligibility"]
                )
                if np.any(proposed_delta):
                    self.weights += proposed_delta
                    self.weights = np.clip(
                        self.weights, -self.cfg.weight_bound, self.cfg.weight_bound
                    )
                    self.weights -= self.weights.mean()
                    self.weights = np.clip(
                        self.weights, -self.cfg.weight_bound, self.cfg.weight_bound
                    )
            delta = self.weights - before
            self.update_log.append({
                "episode": int(row["episode"]),
                "true_reward": float(row["reward"]),
                "assigned_reward": float(assigned_reward),
                "baseline": float(self.baseline),
                "advantage": advantage,
                "eligibility": row["eligibility"].copy(),
                "before": before,
                "delta": delta,
                "after": self.weights.copy(),
            })
            self.baseline += self.cfg.baseline_rate * (assigned_reward - self.baseline)
        self._pending.clear()


class HiddenVectorOracle:
    """Class-E sensitivity control; the hidden role is accepted only here."""

    def __init__(
        self,
        n_neurons: int,
        cfg: LearnerConfig,
        rng: np.random.Generator,
    ) -> None:
        self.cfg = cfg
        weights = rng.normal(0.0, cfg.initial_weight_sd, n_neurons)
        self.weights = weights - weights.mean()
        self.update_log: list[dict[str, Any]] = []

    def emit(self, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        del rng
        return np.clip(0.5 + self.weights, 0.0, 1.0), np.zeros_like(self.weights)

    def privileged_update(self, hidden_role: np.ndarray, episode: int) -> None:
        before = self.weights.copy()
        self.weights += self.cfg.oracle_learning_rate * hidden_role
        self.weights = np.clip(
            self.weights, -self.cfg.weight_bound, self.cfg.weight_bound
        )
        self.weights -= self.weights.mean()
        self.update_log.append({
            "episode": episode,
            "true_reward": np.nan,
            "assigned_reward": np.nan,
            "baseline": np.nan,
            "advantage": np.nan,
            "eligibility": np.zeros_like(self.weights),
            "before": before,
            "delta": self.weights - before,
            "after": self.weights.copy(),
        })
