"""Artificial P+/P- neurofeedback task analogous to Francioni et al. (2026)."""

from __future__ import annotations

import numpy as np


def sample_trial(rng: np.random.Generator, n_neurons: int) -> tuple[np.ndarray, int]:
    """Return intermingled population activity and the rewarded rotation action.

    The two populations are interleaved in the returned vector. The action is
    determined by a latent context cue, not handed to individual model neurons.
    """
    target = int(rng.integers(0, 2))
    half = n_neurons // 2
    p_plus = rng.beta(5 if target == 0 else 3, 3 if target == 0 else 5, half)
    p_minus = rng.beta(3 if target == 0 else 5, 5 if target == 0 else 3, n_neurons - half)
    grouped = np.r_[p_plus, p_minus]
    permutation = np.ravel(np.column_stack((np.arange(half), np.arange(half, n_neurons))))
    return grouped[permutation], target


def population_masks(n_neurons: int) -> tuple[np.ndarray, np.ndarray]:
    """Masks for the spatially intermingled P+ and P- populations."""
    plus = np.arange(n_neurons) % 2 == 0
    return plus, ~plus

