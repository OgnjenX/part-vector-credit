"""Stepwise BCI environment. Hidden neuron roles never enter learner observations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BCIConfig:
    n_neurons: int = 10
    n_plus: int | None = None
    action_frames: int = 8
    delay_steps: int = 5
    causal_strength: float = 1.50
    transition_noise: float = 0.018
    action_noise: float = 0.045
    n_visual_bins: int = 7
    target: float = 1.0
    success_error: float = 0.19


class StepwiseCausalBCI:
    """A closed-loop causal environment with an experimenter-only role vector."""

    def __init__(self, cfg: BCIConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.rng = rng
        self.base_causal = self._draw_causal()
        self.state = 0.0
        self.context = 0

    def _draw_causal(self) -> np.ndarray:
        n_plus = self.cfg.n_plus or self.cfg.n_neurons // 2
        roles = np.r_[np.ones(n_plus), -np.ones(self.cfg.n_neurons - n_plus)]
        return self.rng.permutation(roles)

    def active_causal(self, context: int | None = None) -> np.ndarray:
        active_context = self.context if context is None else context
        return self.base_causal if active_context == 0 else -self.base_causal

    def remap(self) -> tuple[np.ndarray, np.ndarray]:
        old = self.base_causal.copy()
        new = self._draw_causal()
        while np.array_equal(new, old) or np.array_equal(new, -old):
            new = self._draw_causal()
        self.base_causal = new
        return old, new.copy()

    def reset(self, context: int) -> np.ndarray:
        self.context = context
        self.state = 0.0
        return self.observation()

    def state_bin(self) -> int:
        return min(self.cfg.n_visual_bins - 1, int(self.state * self.cfg.n_visual_bins))

    def observation(self) -> np.ndarray:
        context_code = np.zeros(2, dtype=float)
        context_code[self.context] = 1.0
        state_code = np.zeros(self.cfg.n_visual_bins, dtype=float)
        state_code[self.state_bin()] = 1.0
        target_code = np.zeros(self.cfg.n_visual_bins, dtype=float)
        target_code[-1] = 1.0
        return np.r_[context_code, state_code, target_code]

    def step(self, soma: np.ndarray) -> dict[str, object]:
        """Advance one displayed BCI frame and return only observable task quantities."""
        causal = self.active_causal()
        plus = causal > 0
        control = float(soma[plus].mean() - soma[~plus].mean())
        previous_error = abs(self.cfg.target - self.state)
        self.state = float(np.clip(
            self.state
            + self.cfg.causal_strength * control
            + self.rng.normal(0.0, self.cfg.transition_noise),
            0.0,
            1.0,
        ))
        error = abs(self.cfg.target - self.state)
        return {
            "observation": self.observation(),
            "state": self.state,
            "state_bin": self.state_bin(),
            "error": error,
            "error_improvement": previous_error - error,
            "control": control,
        }

    def outcome(self) -> dict[str, float]:
        error = abs(self.cfg.target - self.state)
        return {
            "reward": float(error <= self.cfg.success_error),
            "global_improvement": float(1.0 - error),
            "final_error": error,
        }

    def distractors(self) -> list[np.ndarray]:
        """Observable-irrelevant intervening events between action and outcome."""
        return [self.rng.normal(0.0, 1.0, 6) for _ in range(self.cfg.delay_steps)]
