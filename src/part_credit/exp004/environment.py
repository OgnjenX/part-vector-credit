"""Closed-loop fixed-repertoire population-control environment for EXP004."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TopologyTaskConfig:
    n_neurons: int = 32
    action_frames: int = 3
    n_contexts: int = 2
    target: float = 0.30
    success_tolerance: float = 0.02
    causal_strength: float = 1.0
    action_noise: float = 0.012
    delay_steps: int = 4
    state_bins: int = 5


class TopologyBCI:
    """Environment-only causal mapping; the controller receives only observations."""

    def __init__(
        self,
        cfg: TopologyTaskConfig,
        rng: np.random.Generator,
        base_role: np.ndarray,
        phase_masks: np.ndarray | None = None,
    ) -> None:
        self.cfg = cfg
        self.rng = rng
        self.base_role = np.asarray(base_role, dtype=float).copy()
        self.phase_masks = None if phase_masks is None else np.asarray(phase_masks, dtype=bool)
        self.state = 0.0
        self.context = 0
        self.frame = 0

    def active_role(self, context: int | None = None) -> np.ndarray:
        selected = self.context if context is None else context
        return self.base_role if selected == 0 else -self.base_role

    def reset(self, context: int) -> np.ndarray:
        self.context = int(context)
        self.state = 0.0
        self.frame = 0
        return self.observation()

    def state_bin(self) -> int:
        normalized = np.clip(self.state / self.cfg.target, 0.0, 1.0)
        return min(self.cfg.state_bins - 1, int(normalized * self.cfg.state_bins))

    def observation(self) -> np.ndarray:
        context = np.zeros(self.cfg.n_contexts, dtype=float)
        context[self.context] = 1.0
        phase = self.frame / max(1, self.cfg.action_frames - 1)
        normalized_state = np.clip(self.state / self.cfg.target, 0.0, 1.0)
        return np.r_[context, phase, normalized_state]

    def causal_score(self, soma: np.ndarray, frame: int | None = None) -> float:
        role = self.active_role()
        values = np.asarray(soma, dtype=float)
        active_frame = self.frame if frame is None else frame
        if self.phase_masks is not None:
            mask = self.phase_masks[active_frame]
            role = role[mask]
            values = values[mask]
        return float(values[role > 0].mean() - values[role < 0].mean())

    def execute(self, motor: np.ndarray) -> dict[str, np.ndarray | float | int]:
        noise = self.rng.normal(0.0, self.cfg.action_noise, self.cfg.n_neurons)
        noise -= float(np.mean(noise))
        soma = np.clip(np.asarray(motor, dtype=float) + noise, 0.0, 1.0)
        previous = self.state
        score = self.causal_score(soma)
        self.state = float(np.clip(
            self.state + self.cfg.causal_strength * score,
            0.0,
            self.cfg.target,
        ))
        self.frame += 1
        return {
            "soma": soma,
            "perturbation": soma - np.asarray(motor, dtype=float),
            "causal_score": score,
            "state_before": previous,
            "state_after": self.state,
            "state_improvement": self.state - previous,
            "observation": self.observation(),
        }

    def outcome(self) -> dict[str, float]:
        normalized = float(np.clip(self.state / self.cfg.target, 0.0, 1.0))
        success = float(self.cfg.target - self.state <= self.cfg.success_tolerance)
        return {
            "reward": success,
            "global_improvement": normalized,
            "outcome": 0.80 * normalized + 0.20 * success,
            "final_state": self.state,
            "final_error": self.cfg.target - self.state,
        }
