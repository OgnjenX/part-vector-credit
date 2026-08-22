"""Leakage, somato-dendritic residual, timing, and longitudinal analyses."""

from __future__ import annotations

import numpy as np


def safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    if left.size < 2 or np.std(left) < 1e-12 or np.std(right) < 1e-12:
        return 0.0
    return float(np.corrcoef(left, right)[0, 1])


def _nearest_centroid_loo(features: np.ndarray, labels: np.ndarray) -> float:
    predictions = []
    for held_out in range(len(labels)):
        train = np.arange(len(labels)) != held_out
        centroids = [features[train & (labels == label)].mean(0) for label in (-1, 1)]
        distances = [np.linalg.norm(features[held_out] - center) for center in centroids]
        predictions.append((-1, 1)[int(np.argmin(distances))])
    return float(np.mean(np.asarray(predictions) == labels))


def initialization_audit(
    patterns: np.ndarray,
    causal: np.ndarray,
    rng: np.random.Generator,
    permutations: int = 300,
) -> dict[str, object]:
    correlations = np.asarray([safe_corr(pattern, causal) for pattern in patterns])
    features = np.asarray(patterns).T
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
        "decoder_permutation_p": float((1 + np.sum(null >= observed)) / (permutations + 1)),
        "decoder_null_accuracies": null.tolist(),
    }


def _window_arrays(records: list[dict[str, object]], timing_index: int) -> tuple[np.ndarray, ...]:
    soma = np.concatenate([np.asarray(row["soma_frames"]) for row in records])
    dendrite = np.concatenate([
        np.asarray(row["dendrite_frames"])[:, timing_index, :] for row in records
    ])
    improvement = np.concatenate([np.asarray(row["frame_improvements"]) for row in records])
    return soma, dendrite, improvement


def soma_conditioned_residual(soma: np.ndarray, dendrite: np.ndarray) -> np.ndarray:
    network = soma.mean(axis=1)
    residual = np.empty_like(dendrite)
    for neuron in range(soma.shape[1]):
        design = np.column_stack([np.ones(len(soma)), soma[:, neuron], network])
        coefficients, *_ = np.linalg.lstsq(design, dendrite[:, neuron], rcond=None)
        residual[:, neuron] = dendrite[:, neuron] - design @ coefficients
    return residual


def francioni_signal(
    records: list[dict[str, object]], causal: np.ndarray, timing_index: int = 2
) -> dict[str, object]:
    if len(records) < 3:
        return {"signal": [0.0] * len(causal), "role_alignment": 0.0}
    soma, dendrite, improvement = _window_arrays(records, timing_index)
    residual = soma_conditioned_residual(soma, dendrite)
    split = float(np.median(improvement))
    improved = improvement > split
    if improved.sum() == 0 or (~improved).sum() == 0:
        signal = np.zeros(len(causal))
    else:
        signal = residual[improved].mean(axis=0) - residual[~improved].mean(axis=0)
    return {
        "signal": signal.tolist(),
        "role_alignment": safe_corr(signal, causal),
        "appropriate_sign_fraction": float(np.mean(signal * causal > 0)),
    }


def longitudinal_prediction(
    early: list[dict[str, object]],
    late: list[dict[str, object]],
    causal: np.ndarray,
) -> float:
    early_signal = np.asarray(francioni_signal(early, causal)["signal"])
    early_soma = np.concatenate([np.asarray(row["soma_frames"]) for row in early]).mean(0)
    late_soma = np.concatenate([np.asarray(row["soma_frames"]) for row in late]).mean(0)
    return safe_corr(early_signal, late_soma - early_soma)


def selected_pattern(records: list[dict[str, object]], field: str) -> np.ndarray:
    patterns = np.stack([np.asarray(row[field]).mean(axis=0) for row in records])
    return patterns.mean(axis=0)


def timing_alignments(records: list[dict[str, object]], causal: np.ndarray) -> list[float]:
    return [francioni_signal(records, causal, timing_index=index)["role_alignment"] for index in range(5)]


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if len(values) == 1:
        return float(values[0]), float(values[0])
    samples = rng.choice(values, size=(5000, len(values)), replace=True).mean(axis=1)
    low, high = np.quantile(samples, [0.025, 0.975])
    return float(low), float(high)
