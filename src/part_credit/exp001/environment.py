"""Closed-loop causal BCI environment; hidden neuron roles live only here."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BCIConfig:
    n_neurons: int = 10
    n_plus: int | None = None
    action_frames: int = 5
    delay_steps: int = 4
    causal_strength: float = 0.50
    transition_noise: float = 0.025
    causal_weight_noise: float = 0.0
    stochastic_reward: float = 0.0
    target: float = 1.0
    success_error: float = 0.20


class CausalBCI:
    """Environment with an experimenter-hidden, randomly permuted causal vector."""

    def __init__(self, cfg: BCIConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.rng = rng
        self.causal = self._draw_causal()
        self.causal_weights = self._draw_weights()

    def _draw_causal(self) -> np.ndarray:
        n_plus = self.cfg.n_plus or self.cfg.n_neurons // 2
        roles = np.r_[np.ones(n_plus), -np.ones(self.cfg.n_neurons - n_plus)]
        return self.rng.permutation(roles)

    def _draw_weights(self) -> np.ndarray:
        if self.cfg.causal_weight_noise == 0:
            return np.ones(self.cfg.n_neurons)
        return np.clip(
            1.0 + self.rng.normal(0, self.cfg.causal_weight_noise, self.cfg.n_neurons),
            0.10,
            None,
        )

    def remap(self, fraction: float = 1.0) -> None:
        if fraction >= 1.0:
            candidate = self._draw_causal()
        else:
            candidate = self.causal.copy()
            count = max(2, round(fraction * self.cfg.n_neurons))
            indices = self.rng.choice(self.cfg.n_neurons, count, replace=False)
            candidate[indices] *= -1
            # Restore the requested population count without index-based rules.
            desired = self.cfg.n_plus or self.cfg.n_neurons // 2
            while int((candidate > 0).sum()) != desired:
                sign = 1 if (candidate > 0).sum() > desired else -1
                choices = np.flatnonzero(candidate == sign)
                candidate[self.rng.choice(choices)] *= -1
        if np.array_equal(candidate, self.causal):
            candidate = np.roll(candidate, 1)
        self.causal = candidate
        self.causal_weights = self._draw_weights()

    def observation(self, context: int = 0, n_contexts: int = 1) -> np.ndarray:
        context_code = np.zeros(max(2, n_contexts), dtype=float)
        context_code[context] = 1.0
        return np.r_[context_code, 0.0, self.cfg.target]

    def execute(self, soma_frames: np.ndarray) -> dict[str, object]:
        """Evaluate activity; hidden roles never leave this return except analysis fields."""
        state = 0.0
        states = []
        errors = []
        delta_errors = []
        previous_error = abs(self.cfg.target - state)
        plus = self.causal > 0
        for soma in soma_frames:
            control = float(
                (soma[plus] * self.causal_weights[plus]).mean()
                - (soma[~plus] * self.causal_weights[~plus]).mean()
            )
            state = float(np.clip(
                state + self.cfg.causal_strength * control
                + self.rng.normal(0, self.cfg.transition_noise), 0.0, 1.0
            ))
            error = abs(self.cfg.target - state)
            states.append(state)
            errors.append(error)
            delta_errors.append(previous_error - error)
            previous_error = error
        success = float(previous_error <= self.cfg.success_error)
        if self.cfg.stochastic_reward > 0 and self.rng.random() < self.cfg.stochastic_reward:
            success = 1.0 - success
        return {
            "states": np.asarray(states),
            "errors": np.asarray(errors),
            "delta_errors": np.asarray(delta_errors),
            "global_improvement": float(1.0 - previous_error),
            "reward": success,
            # The following are analysis-only and never passed to the Grossberg learner.
            "causal_contribution": (
                soma_frames * (self.causal * self.causal_weights)[None, :]
            ),
        }

    def distractors(self) -> list[np.ndarray]:
        return [self.rng.normal(0, 1, 4) for _ in range(self.cfg.delay_steps)]
