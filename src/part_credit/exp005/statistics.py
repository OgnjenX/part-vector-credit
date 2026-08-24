"""Preregistered summaries for the non-Grossberg EXP005 diagnostic."""

from __future__ import annotations

from typing import Any

import numpy as np

METRICS = (
    "initial_alignment",
    "pre_remap_alignment",
    "post_remap_alignment",
    "pre_correct_sign_fraction",
    "post_correct_sign_fraction",
    "sign_reversal_accuracy",
    "pre_behavior",
    "post_behavior",
    "pre_success",
    "post_success",
    "pre_minus_best_sample",
    "post_minus_best_sample",
    "reconstruction_rmse",
    "legal_update_reconstruction_rmse",
    "local_eligibility_update_corr",
    "local_prediction_update_corr",
    "pre_local_variation_outcome_role_alignment",
    "post_local_variation_outcome_role_alignment",
    "outcome_update_magnitude_corr",
)

FLOORS = {
    "alignment": 0.70,
    "sign_fraction": 0.80,
    "behavior": 0.60,
    "ablation_effect": 0.40,
    "reversal": 0.75,
    "reconstruction_rmse": 1e-12,
}


def bootstrap(values: np.ndarray, seed: int) -> dict[str, Any]:
    data = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    samples = np.empty(5000)
    for index in range(samples.size):
        samples[index] = np.mean(rng.choice(data, data.size, replace=True))
    return {
        "mean": float(np.mean(data)),
        "ci95": np.quantile(samples, [0.025, 0.975]).tolist(),
        "n": int(data.size),
    }


def paired(
    left: dict[str, Any], right: dict[str, Any], metric: str, seed: int
) -> dict[str, Any]:
    by_seed = {int(row["seed"]): row for row in right["seeds"]}
    differences = np.asarray([
        float(row[metric]) - float(by_seed[int(row["seed"])][metric])
        for row in left["seeds"]
    ])
    result = bootstrap(differences, seed)
    result.update({"metric": metric, "left": left["scenario"]["name"], "right": right["scenario"]["name"]})
    return result


def analyze_results(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    aggregates = {
        name: {
            metric: bootstrap(
                np.asarray([row[metric] for row in result["seeds"]]),
                5505 + scenario_index * 100 + metric_index,
            )
            for metric_index, metric in enumerate(METRICS)
        }
        for scenario_index, (name, result) in enumerate(results.items())
    }
    contrasts = {}
    for n_index, n in enumerate((8, 16, 32, 64)):
        primary = results[f"n{n}_generic_node_perturbation"]
        controls = ["outcome_shuffled"]
        if n == 32:
            controls.extend((
                "plasticity_disabled",
                "temporal_eligibility_disabled",
                "exploration_removed",
                "random_no_learning",
            ))
        for c_index, control in enumerate(controls):
            for m_index, metric in enumerate(("pre_remap_alignment", "post_remap_alignment")):
                key = f"n{n}_generic_minus_{control}__{metric}"
                contrasts[key] = paired(
                    primary,
                    results[f"n{n}_{control}"],
                    metric,
                    6505 + n_index * 1000 + c_index * 20 + m_index,
                )
    n32 = aggregates["n32_generic_node_perturbation"]
    shuffled_effect = contrasts[
        "n32_generic_minus_outcome_shuffled__post_remap_alignment"
    ]
    exploration_effect = contrasts[
        "n32_generic_minus_exploration_removed__post_remap_alignment"
    ]
    generic_works = (
        n32["pre_remap_alignment"]["mean"] >= FLOORS["alignment"]
        and n32["post_remap_alignment"]["mean"] >= FLOORS["alignment"]
        and n32["post_correct_sign_fraction"]["mean"] >= FLOORS["sign_fraction"]
        and n32["sign_reversal_accuracy"]["mean"] >= FLOORS["reversal"]
        and shuffled_effect["mean"] >= FLOORS["ablation_effect"]
        and shuffled_effect["ci95"][0] > 0.0
        and exploration_effect["mean"] >= FLOORS["ablation_effect"]
        and exploration_effect["ci95"][0] > 0.0
    )
    return {
        "status": "post-hard-stop generic diagnostic",
        "source_gate_outcome": "E_NO_GROSSBERG_CANDIDATE_EXISTS",
        "aggregates": aggregates,
        "contrasts": contrasts,
        "classifications": {
            "grossberg_primary_confirmed": False,
            "generic_scalar_reward_cellular_credit_works": bool(generic_works),
            "interpretation_if_generic_works": "C_GENERIC_CELLULAR_CREDIT_WORKS_BUT_NO_GROSSBERG_CANDIDATE",
        },
        "floors": FLOORS,
    }
