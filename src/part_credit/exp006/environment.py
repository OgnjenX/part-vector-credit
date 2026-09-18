"""Shared Francioni-like closed-loop environment for EXP006."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FrancioniTaskConfig:
    n_neurons: int = 10
    max_frames: int = 28
    visual_bins: int = 7
    state_gain: float = 0.12
    target_state: float = 1.0
    reward_delay_frames: int = 1

    @property
    def bin_width(self) -> float:
        return 1.0 / (self.visual_bins - 1)


def balanced_role(rng: np.random.Generator, n_neurons: int) -> np.ndarray:
    """Sample a hidden balanced P+/P- assignment."""
    if n_neurons % 2:
        raise ValueError("balanced roles require an even number of neurons")
    role = np.r_[np.ones(n_neurons // 2), -np.ones(n_neurons // 2)]
    return role[rng.permutation(n_neurons)].astype(float)


def independent_remap(rng: np.random.Generator, role: np.ndarray) -> np.ndarray:
    """Sample a balanced remap with neither trivial nor complete reversal."""
    for _ in range(10_000):
        candidate = balanced_role(rng, role.size)
        changed = float(np.mean(candidate != role))
        if 0.2 <= changed <= 0.8:
            return candidate
    raise RuntimeError("unable to sample a nontrivial balanced remap")


class FrancioniBCI:
    """Environment-only P+/P- mapping with continuous binned visual feedback."""

    def __init__(self, cfg: FrancioniTaskConfig, role: np.ndarray) -> None:
        self.cfg = cfg
        self.role = np.asarray(role, dtype=float).copy()
        if self.role.shape != (cfg.n_neurons,):
            raise ValueError("role shape does not match task population")
        self.state = 0.0
        self.displayed_state = 0.0
        self.previous_visible_delta = 0.0
        self.frame = 0

    def reset(self, role: np.ndarray | None = None) -> np.ndarray:
        if role is not None:
            selected = np.asarray(role, dtype=float)
            if selected.shape != self.role.shape:
                raise ValueError("remapped role shape does not match task population")
            self.role = selected.copy()
        self.state = 0.0
        self.displayed_state = 0.0
        self.previous_visible_delta = 0.0
        self.frame = 0
        return self.observation()

    def _display(self, state: float) -> float:
        index = int(np.clip(np.rint(state * (self.cfg.visual_bins - 1)), 0, self.cfg.visual_bins - 1))
        return index / (self.cfg.visual_bins - 1)

    def observation(self) -> np.ndarray:
        phase = self.frame / max(1, self.cfg.max_frames - 1)
        signed_change = np.clip(
            self.previous_visible_delta / self.cfg.bin_width,
            -1.0,
            1.0,
        )
        return np.asarray([
            phase,
            self.displayed_state,
            0.5 + 0.5 * signed_change,
        ])

    def opponent_drive(self, soma: np.ndarray) -> float:
        activity = np.asarray(soma, dtype=float)
        return float(activity[self.role > 0].mean() - activity[self.role < 0].mean())

    def step(self, soma: np.ndarray) -> dict[str, float | np.ndarray]:
        if self.frame >= self.cfg.max_frames:
            raise RuntimeError("trial already reached its maximum frame count")
        state_before = self.state
        displayed_before = self.displayed_state
        drive = self.opponent_drive(soma)
        self.state = float(np.clip(
            self.state + self.cfg.state_gain * drive,
            0.0,
            self.cfg.target_state,
        ))
        self.displayed_state = self._display(self.state)
        self.previous_visible_delta = self.displayed_state - displayed_before
        self.frame += 1
        return {
            "drive": drive,
            "state_before": state_before,
            "state_after": self.state,
            "latent_delta": self.state - state_before,
            "displayed_before": displayed_before,
            "displayed_after": self.displayed_state,
            "visible_delta": self.previous_visible_delta,
            "error_before": self.cfg.target_state - state_before,
            "error_after": self.cfg.target_state - self.state,
            "success": float(self.displayed_state >= self.cfg.target_state),
            "observation": self.observation(),
        }

