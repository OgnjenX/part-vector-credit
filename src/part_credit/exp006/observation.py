"""Common synthetic soma--dendrite measurement layer for EXP006."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ObservationConfig:
    soma_gain: float = 0.82
    feedback_gain: float = 0.16
    noise_sd: float = 0.035


def _feedback_standardization(
    feedback: np.ndarray, mask: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    standardized = np.full_like(feedback, np.nan, dtype=float)
    flat = feedback[mask]
    mean = np.nanmean(flat, axis=0)
    scale = np.nanstd(flat, axis=0)
    safe_scale = np.where(scale < 1e-9, 1.0, scale)
    standardized[mask] = np.clip((flat - mean) / safe_scale, -4.0, 4.0)
    return standardized, mean, safe_scale


def simulate_residuals(
    *,
    soma: np.ndarray,
    feedback: np.ndarray,
    valid_mask: np.ndarray,
    post_soma: np.ndarray,
    post_feedback: np.ndarray,
    cfg: ObservationConfig,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Apply one observation model and fit one soma--dendrite line per cell."""
    standardized, feedback_mean, feedback_scale = _feedback_standardization(
        feedback, valid_mask
    )
    dendrite = np.full_like(soma, np.nan, dtype=float)
    action_noise = rng.normal(0.0, cfg.noise_sd, soma.shape)
    dendrite[valid_mask] = (
        cfg.soma_gain * soma[valid_mask]
        + cfg.feedback_gain * standardized[valid_mask]
        + action_noise[valid_mask]
    )

    n_neurons = soma.shape[-1]
    intercept = np.zeros(n_neurons, dtype=float)
    slope = np.zeros(n_neurons, dtype=float)
    residual = np.full_like(soma, np.nan, dtype=float)
    for neuron in range(n_neurons):
        x = soma[..., neuron][valid_mask]
        y = dendrite[..., neuron][valid_mask]
        design = np.column_stack([np.ones(x.size), x])
        coefficient = np.linalg.lstsq(design, y, rcond=None)[0]
        intercept[neuron], slope[neuron] = coefficient
        residual[..., neuron][valid_mask] = y - design @ coefficient

    post_standardized = np.clip(
        (post_feedback - feedback_mean) / feedback_scale,
        -4.0,
        4.0,
    )
    post_dendrite = (
        cfg.soma_gain * post_soma
        + cfg.feedback_gain * post_standardized
        + rng.normal(0.0, cfg.noise_sd, post_soma.shape)
    )
    post_residual = post_dendrite - (
        intercept[None, :] + slope[None, :] * post_soma
    )
    return {
        "feedback_standardized": standardized,
        "dendrite": dendrite,
        "residual": residual,
        "post_feedback_standardized": post_standardized,
        "post_dendrite": post_dendrite,
        "post_residual": post_residual,
        "residual_intercept": intercept,
        "residual_slope": slope,
    }


def balanced_accuracy(labels: np.ndarray, predictions: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=int)
    predictions = np.asarray(predictions, dtype=int)
    scores = []
    for label in (0, 1):
        mask = labels == label
        if np.any(mask):
            scores.append(float(np.mean(predictions[mask] == label)))
    return float(np.mean(scores)) if len(scores) == 2 else 0.5


def cross_validated_linear_decode(
    features: np.ndarray,
    labels: np.ndarray,
    *,
    folds: int = 5,
    ridge: float = 1e-3,
) -> float:
    """Deterministic blocked ridge decoder with balanced-accuracy scoring."""
    x = np.asarray(features, dtype=float)
    y = np.asarray(labels, dtype=int)
    if x.shape[0] < folds * 2 or np.unique(y).size < 2:
        return 0.5
    predictions = np.zeros_like(y)
    fold_ids = np.arange(y.size) % folds
    for fold in range(folds):
        test = fold_ids == fold
        train = ~test
        design = np.column_stack([np.ones(np.sum(train)), x[train]])
        regularizer = ridge * np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficient = np.linalg.solve(
            design.T @ design + regularizer,
            design.T @ y[train],
        )
        test_design = np.column_stack([np.ones(np.sum(test)), x[test]])
        predictions[test] = (test_design @ coefficient >= 0.5).astype(int)
    return balanced_accuracy(y, predictions)

