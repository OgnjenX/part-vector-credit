"""Leakage, Francioni-style residual, and longitudinal analyses for EXP003b."""

from __future__ import annotations

import numpy as np


def safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=float).ravel()
    right = np.asarray(right, dtype=float).ravel()
    finite = np.isfinite(left) & np.isfinite(right)
    if finite.sum() < 3 or np.std(left[finite]) < 1e-12 or np.std(right[finite]) < 1e-12:
        return 0.0
    return float(np.corrcoef(left[finite], right[finite])[0, 1])


def bootstrap_mean_ci(
    values: np.ndarray, rng: np.random.Generator, samples: int = 5000
) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if len(values) == 1:
        return float(values[0]), float(values[0])
    means = rng.choice(values, (samples, len(values)), replace=True).mean(axis=1)
    low, high = np.quantile(means, (0.025, 0.975))
    return float(low), float(high)


def _nearest_centroid_loo(features: np.ndarray, labels: np.ndarray) -> float:
    predictions: list[int] = []
    for held_out in range(len(labels)):
        train = np.arange(len(labels)) != held_out
        centers = []
        for label in (-1, 1):
            selected = features[train & (labels == label)]
            centers.append(selected.mean(axis=0))
        distances = [np.linalg.norm(features[held_out] - center) for center in centers]
        predictions.append((-1, 1)[int(np.argmin(distances))])
    return float(np.mean(np.asarray(predictions) == labels))


def initialization_audit(
    patterns: np.ndarray,
    causal: np.ndarray,
    rng: np.random.Generator,
    permutations: int = 300,
) -> dict[str, object]:
    patterns = np.asarray(patterns, dtype=float).reshape(-1, len(causal))
    correlations = np.asarray([safe_corr(row, causal) for row in patterns])
    features = patterns.T
    observed = _nearest_centroid_loo(features, causal)
    null = np.asarray([
        _nearest_centroid_loo(features, rng.permutation(causal))
        for _ in range(permutations)
    ])
    return {
        "candidate_correlations": correlations.tolist(),
        "mean_signed_correlation": float(correlations.mean()),
        "max_absolute_correlation": float(np.abs(correlations).max()),
        "decoder_accuracy": observed,
        "decoder_null_mean": float(null.mean()),
        "decoder_permutation_p": float(
            (1 + np.sum(null >= observed)) / (permutations + 1)
        ),
    }


def soma_conditioned_residual(
    soma: np.ndarray, dendrite: np.ndarray
) -> np.ndarray:
    soma = np.asarray(soma, dtype=float)
    dendrite = np.asarray(dendrite, dtype=float)
    network = soma.mean(axis=1)
    residual = np.zeros_like(dendrite)
    for neuron in range(soma.shape[1]):
        design = np.column_stack((np.ones(len(soma)), soma[:, neuron], network))
        coefficients, *_ = np.linalg.lstsq(design, dendrite[:, neuron], rcond=None)
        residual[:, neuron] = dendrite[:, neuron] - design @ coefficients
    return residual


def residual_error_signal(
    soma: np.ndarray,
    dendrite: np.ndarray,
    improvements: np.ndarray,
) -> np.ndarray:
    if len(soma) < 4:
        return np.zeros(soma.shape[-1])
    residual = soma_conditioned_residual(soma, dendrite)
    split = float(np.median(improvements))
    improved = improvements > split
    if improved.sum() == 0 or (~improved).sum() == 0:
        return np.zeros(soma.shape[-1])
    return residual[improved].mean(axis=0) - residual[~improved].mean(axis=0)


def records_arrays(
    records: list[dict[str, object]], phase_index: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    soma = np.stack([np.asarray(row["soma"]) for row in records])
    dendrite = np.stack([
        np.asarray(row["dendrite_phases"])[phase_index] for row in records
    ])
    improvement = np.asarray([row["error_improvement"] for row in records], dtype=float)
    return soma, dendrite, improvement


def longitudinal_for_fixed_h(
    *,
    early_records: list[dict[str, object]],
    late_records: list[dict[str, object]],
    early_probe: np.ndarray,
    late_probe: np.ndarray,
    early_weights: np.ndarray,
    late_weights: np.ndarray,
    phase_index: int,
) -> dict[str, object]:
    if not early_records or not late_records:
        return {
            "hypothesis": -1,
            "n_early": 0,
            "d_to_w": 0.0,
            "d_to_s": 0.0,
            "w_to_s": 0.0,
            "signal": np.zeros(early_weights.shape[1]),
        }
    all_h = np.asarray([
        int(row["hypothesis"]) for row in early_records + late_records
    ])
    counts = np.bincount(all_h, minlength=early_weights.shape[0])
    hypothesis = int(np.argmax(counts))
    early_h = [row for row in early_records if int(row["hypothesis"]) == hypothesis]
    late_h = [row for row in late_records if int(row["hypothesis"]) == hypothesis]
    if len(early_h) < 4 or len(late_h) < 2:
        return {
            "hypothesis": hypothesis,
            "n_early": len(early_h),
            "d_to_w": 0.0,
            "d_to_s": 0.0,
            "w_to_s": 0.0,
            "signal": np.zeros(early_weights.shape[1]),
        }
    soma, dendrite, improvement = records_arrays(early_h, phase_index)
    signal = residual_error_signal(soma, dendrite, improvement)
    delta_weight = late_weights[hypothesis] - early_weights[hypothesis]
    delta_soma = late_probe[hypothesis] - early_probe[hypothesis]
    return {
        "hypothesis": hypothesis,
        "n_early": len(early_h),
        "d_to_w": safe_corr(signal, delta_weight),
        "d_to_s": safe_corr(signal, delta_soma),
        "w_to_s": safe_corr(delta_weight, delta_soma),
        "signal": signal,
        "delta_weight": delta_weight,
        "delta_soma": delta_soma,
    }


def timing_role_alignment(
    records: list[dict[str, object]], causal: np.ndarray, n_phases: int
) -> list[float]:
    alignments = []
    for phase_index in range(n_phases):
        soma, dendrite, improvement = records_arrays(records, phase_index)
        signal = residual_error_signal(soma, dendrite, improvement)
        alignments.append(safe_corr(signal, causal))
    return alignments
