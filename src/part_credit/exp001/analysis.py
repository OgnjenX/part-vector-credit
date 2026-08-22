"""Leakage and Francioni-inspired somato-dendritic analyses."""

from __future__ import annotations

import numpy as np


def _nearest_centroid_loo(features: np.ndarray, labels: np.ndarray) -> float:
    predictions = []
    for held_out in range(len(labels)):
        train = np.arange(len(labels)) != held_out
        centroids = [features[train & (labels == label)].mean(0) for label in (-1, 1)]
        distances = [np.linalg.norm(features[held_out] - center) for center in centroids]
        predictions.append((-1, 1)[int(np.argmin(distances))])
    return float(np.mean(np.asarray(predictions) == labels))


def initialization_audit(
    basis: np.ndarray, causal: np.ndarray, rng: np.random.Generator, permutations: int = 200
) -> dict[str, object]:
    correlations = np.array([np.corrcoef(pattern, causal)[0, 1] for pattern in basis])
    features = basis.T
    observed = _nearest_centroid_loo(features, causal)
    null = np.array([
        _nearest_centroid_loo(features, rng.permutation(causal)) for _ in range(permutations)
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


def soma_dendritic_residual(records: list[dict[str, object]]) -> np.ndarray:
    soma = np.concatenate([np.asarray(row["soma"]) for row in records])
    dendrite = np.concatenate([np.asarray(row["dendrite"]) for row in records])
    network = soma.mean(1)
    residual = np.empty_like(dendrite)
    for neuron in range(soma.shape[1]):
        design = np.column_stack([np.ones(len(soma)), soma[:, neuron], network])
        coefficients, *_ = np.linalg.lstsq(design, dendrite[:, neuron], rcond=None)
        residual[:, neuron] = dendrite[:, neuron] - design @ coefficients
    return residual


def dendritic_metrics(records: list[dict[str, object]], causal: np.ndarray) -> dict[str, object]:
    if len(records) < 4:
        return {"role_alignment": 0.0, "appropriate_sign_fraction": 0.0, "opposite_population_signs": False, "signal": []}
    residual = soma_dendritic_residual(records)
    changes = np.concatenate([np.asarray(row["delta_errors"]) for row in records])
    split = float(np.median(changes))
    high = changes > split
    if high.sum() == 0 or (~high).sum() == 0:
        signal = np.zeros(residual.shape[1])
    else:
        signal = residual[high].mean(0) - residual[~high].mean(0)
    alignment = float(np.corrcoef(signal, causal)[0, 1]) if np.std(signal) > 1e-9 else 0.0
    return {
        "role_alignment": alignment,
        "appropriate_sign_fraction": float(np.mean(signal * causal > 0)),
        "opposite_population_signs": bool(
            signal[causal > 0].mean() > 0 and signal[causal < 0].mean() < 0
        ),
        "signal": signal.tolist(),
    }


def longitudinal_prediction(
    early: list[dict[str, object]], late: list[dict[str, object]], causal: np.ndarray
) -> float:
    early_signal = np.asarray(dendritic_metrics(early, causal)["signal"])
    early_soma = np.concatenate([np.asarray(row["soma"]) for row in early]).mean(0)
    late_soma = np.concatenate([np.asarray(row["soma"]) for row in late]).mean(0)
    change = late_soma - early_soma
    if np.std(early_signal) < 1e-9 or np.std(change) < 1e-9:
        return 0.0
    return float(np.corrcoef(early_signal, change)[0, 1])
