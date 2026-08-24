"""Seed-level statistics and preregisterable classifiers for EXP004."""

from __future__ import annotations

from typing import Any

import numpy as np

PRIMARY_METRICS = (
    "A_single",
    "Q_single",
    "best_single_behavior",
    "best_allowed_behavior",
    "evaluation_success",
    "evaluation_behavior",
    "behavior_minus_best_single",
    "behavior_oracle_gap",
    "t_alignment",
    "t_effective_alignment",
    "t_improvement_over_best_initial",
    "t_improvement_over_best_target",
    "t_to_selected_initial",
    "t_to_simple_average",
    "reconstruction_rmse",
    "same_h_category_t_distance",
    "category_count",
    "category_modifications",
    "prototype_total_change",
    "category_context_nmi",
    "structural_credit_concentration",
    "motor_basis_change_norm",
)


DEFAULT_FLOORS = {
    "behavior_effect": 0.15,
    "composition_advantage": 0.15,
    "composition_oracle_gap": 0.10,
    "category_effect": 0.10,
    "copy_similarity": 0.95,
    "representational_gain": 0.10,
    "reconstruction_rmse": 1e-8,
    "outcome_information_effect": 0.15,
    "additional_plasticity_effect": 0.20,
}


def _bootstrap_mean(values: np.ndarray, rng_seed: int) -> dict[str, Any]:
    data = np.asarray(values, dtype=float)
    rng = np.random.default_rng(rng_seed)
    estimates = np.empty(5000, dtype=float)
    for index in range(estimates.size):
        sample = rng.integers(0, data.size, data.size)
        estimates[index] = float(np.mean(data[sample]))
    return {
        "mean": float(np.mean(data)),
        "ci95": np.quantile(estimates, [0.025, 0.975]).tolist(),
        "n": int(data.size),
    }


def _paired_effect(
    left: dict[str, Any], right: dict[str, Any], metric: str, rng_seed: int
) -> dict[str, Any]:
    right_by_seed = {int(row["seed"]): row for row in right["seeds"]}
    differences = np.asarray([
        float(row[metric]) - float(right_by_seed[int(row["seed"])][metric])
        for row in left["seeds"]
    ])
    result = _bootstrap_mean(differences, rng_seed)
    result.update({
        "metric": metric,
        "left": left["scenario"]["name"],
        "right": right["scenario"]["name"],
    })
    return result


def _ols(y: np.ndarray, columns: list[np.ndarray]) -> tuple[np.ndarray, float]:
    design = np.column_stack([np.ones(y.size), *columns])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    fitted = design @ coefficients
    total = float(np.sum((y - np.mean(y)) ** 2))
    residual = float(np.sum((y - fitted) ** 2))
    r_squared = 1.0 - residual / total if total > 1e-12 else 0.0
    return coefficients, r_squared


def _mediation(
    results: dict[str, dict[str, Any]],
    *,
    regime: str,
    condition: str,
    rng_seed: int,
) -> dict[str, Any]:
    rows = []
    for result in results.values():
        scenario = result["scenario"]
        if (
            scenario["family"] == "random"
            and scenario["experience_regime"] == regime
            and scenario["condition"] == condition
        ):
            rows.extend(result["seeds"])
    seed_ids = np.asarray([int(row["seed"]) for row in rows])
    log_m = np.log2(np.asarray([row["n_hypotheses"] for row in rows], dtype=float))
    coverage = np.asarray([row["A_single"] for row in rows], dtype=float)
    behavior = np.asarray([row["evaluation_behavior"] for row in rows], dtype=float)

    def estimate(indices: np.ndarray) -> tuple[float, float, float, float, float]:
        x = log_m[indices]
        mediator = coverage[indices]
        outcome = behavior[indices]
        a, _r2_a = _ols(mediator, [x])
        c, _ = _ols(outcome, [x])
        direct, r2_direct = _ols(outcome, [x, mediator])
        return float(a[1]), float(direct[2]), float(c[1]), float(a[1] * direct[2]), r2_direct

    observed = estimate(np.arange(len(rows)))
    unique_seeds = np.unique(seed_ids)
    rng = np.random.default_rng(rng_seed)
    boot = np.empty((5000, 5), dtype=float)
    for index in range(boot.shape[0]):
        sampled = rng.choice(unique_seeds, unique_seeds.size, replace=True)
        indices = np.concatenate([np.flatnonzero(seed_ids == seed) for seed in sampled])
        boot[index] = estimate(indices)
    labels = ("a_m_to_coverage", "b_coverage_to_behavior", "total_m_to_behavior", "indirect", "direct_model_r2")
    return {
        "regime": regime,
        "condition": condition,
        "n_seed_clusters": int(unique_seeds.size),
        **{
            label: {
                "estimate": observed[position],
                "ci95": np.quantile(boot[:, position], [0.025, 0.975]).tolist(),
            }
            for position, label in enumerate(labels)
        },
    }


def analyze_results(
    results: dict[str, dict[str, Any]],
    floors: dict[str, float] | None = None,
) -> dict[str, Any]:
    thresholds = DEFAULT_FLOORS if floors is None else floors
    aggregates = {}
    for scenario_index, (name, result) in enumerate(results.items()):
        aggregates[name] = {
            metric: _bootstrap_mean(
                np.asarray([row[metric] for row in result["seeds"]]),
                4404 + scenario_index * 100 + metric_index,
            )
            for metric_index, metric in enumerate(PRIMARY_METRICS)
        }

    contrasts = {}
    medium_primary = results["controlled_medium_primary_art_outstar"]
    for index, comparison in enumerate((
        "controlled_medium_contextual_bandit",
        "controlled_medium_fixed_categories",
        "controlled_medium_no_new_category",
        "controlled_medium_no_category_modification",
        "controlled_medium_outcome_shuffled",
        "controlled_medium_random_reinforcement_target",
    )):
        for metric_index, metric in enumerate(("evaluation_behavior", "evaluation_success", "t_alignment")):
            key = f"primary_minus_{comparison}__{metric}"
            contrasts[key] = _paired_effect(
                medium_primary,
                results[comparison],
                metric,
                5504 + index * 100 + metric_index,
            )
    contrasts["controlled_high_minus_low__evaluation_behavior"] = _paired_effect(
        results["controlled_high_primary_art_outstar"],
        results["controlled_low_primary_art_outstar"],
        "evaluation_behavior",
        6104,
    )
    contrasts["motor_plasticity_minus_low_primary__evaluation_behavior"] = _paired_effect(
        results["controlled_low_generic_scalar_motor_plasticity"],
        results["controlled_low_primary_art_outstar"],
        "evaluation_behavior",
        6105,
    )
    contrasts["vector_minus_low_primary__evaluation_behavior"] = _paired_effect(
        results["controlled_low_explicit_hidden_vector_control"],
        results["controlled_low_primary_art_outstar"],
        "evaluation_behavior",
        6106,
    )
    composition = results["composition_primary_art_outstar"]
    composition_advantage = _bootstrap_mean(np.asarray([
        row["behavior_minus_best_single"] for row in composition["seeds"]
    ]), 6204)
    composition_gap = _bootstrap_mean(np.asarray([
        row["behavior_oracle_gap"] for row in composition["seeds"]
    ]), 6205)

    primary_controlled = [
        results[f"controlled_{coverage}_primary_art_outstar"]
        for coverage in ("low", "medium", "high")
    ]
    controlled_rows = [row for result in primary_controlled for row in result["seeds"]]
    x = np.asarray([row["A_single"] for row in controlled_rows])
    y_behavior = np.asarray([row["evaluation_behavior"] for row in controlled_rows])
    y_t = np.asarray([row["t_alignment"] for row in controlled_rows])
    coverage_behavior = float(np.corrcoef(x, y_behavior)[0, 1])
    coverage_t = float(np.corrcoef(x, y_t)[0, 1])

    copy_value = aggregates["controlled_medium_primary_art_outstar"][
        "t_to_selected_initial"
    ]
    reconstruction = aggregates["controlled_medium_primary_art_outstar"][
        "reconstruction_rmse"
    ]
    gain = aggregates["controlled_medium_primary_art_outstar"][
        "t_improvement_over_best_target"
    ]
    category_effect = contrasts[
        "primary_minus_controlled_medium_contextual_bandit__evaluation_behavior"
    ]
    high_low = contrasts["controlled_high_minus_low__evaluation_behavior"]
    motor_effect = contrasts[
        "motor_plasticity_minus_low_primary__evaluation_behavior"
    ]
    outcome_effect = contrasts[
        "primary_minus_controlled_medium_outcome_shuffled__t_alignment"
    ]

    classifications = {
        "behavioral": {
            "B1_single_repertoire_selection": (
                copy_value["mean"] >= thresholds["copy_similarity"]
            ),
            "B2_sequential_contextual_composition": (
                composition_advantage["mean"] >= thresholds["composition_advantage"]
                and composition_advantage["ci95"][0] > 0.0
                and composition_gap["mean"] <= thresholds["composition_oracle_gap"]
            ),
            "B3_search_or_architecture_limitation": any(
                aggregates[f"random_m{size}_search_normalized_primary_art_outstar"][
                    "behavior_oracle_gap"
                ]["mean"] >= thresholds["behavior_effect"]
                and aggregates[f"random_m{size}_search_normalized_primary_art_outstar"][
                    "best_allowed_behavior"
                ]["mean"] >= 0.95
                for size in (64, 128)
            ),
            "B4_additional_motor_plasticity_required": (
                motor_effect["mean"] >= thresholds["additional_plasticity_effect"]
                and motor_effect["ci95"][0] > 0.0
            ),
        },
        "representational": {
            "R1_copy_or_single_pattern_storage": (
                copy_value["mean"] >= thresholds["copy_similarity"]
                and gain["mean"] < thresholds["representational_gain"]
            ),
            "R2_outstar_construction": (
                gain["mean"] >= thresholds["representational_gain"]
                and reconstruction["mean"] <= thresholds["reconstruction_rmse"]
            ),
            "R3_category_factorization": (
                category_effect["mean"] >= thresholds["category_effect"]
                and category_effect["ci95"][0] > 0.0
                and aggregates["controlled_medium_primary_art_outstar"][
                    "same_h_category_t_distance"
                ]["mean"] >= thresholds["representational_gain"]
            ),
            "R4_unexplained_structure": (
                reconstruction["mean"] > thresholds["reconstruction_rmse"]
            ),
        },
        "A2": {
            "weak_form_support": (
                outcome_effect["mean"] >= thresholds["outcome_information_effect"]
                and outcome_effect["ci95"][0] > 0.0
                and reconstruction["mean"] <= thresholds["reconstruction_rmse"]
            ),
            "repertoire_limited": (
                high_low["mean"] >= thresholds["behavior_effect"]
                and high_low["ci95"][0] > 0.0
            ),
            "requires_additional_plasticity": (
                motor_effect["mean"] >= thresholds["additional_plasticity_effect"]
                and motor_effect["ci95"][0] > 0.0
            ),
        },
    }
    return {
        "thresholds": thresholds,
        "aggregates": aggregates,
        "contrasts": contrasts,
        "mediation": {
            f"{regime}_{condition}": _mediation(
                results,
                regime=regime,
                condition=condition,
                rng_seed=6604 + regime_index * 100 + condition_index,
            )
            for regime_index, regime in enumerate(("fixed", "search_normalized"))
            for condition_index, condition in enumerate((
                "contextual_bandit", "primary_art_outstar"
            ))
        },
        "controlled_coverage": {
            "coverage_to_behavior_correlation": coverage_behavior,
            "coverage_to_t_alignment_correlation": coverage_t,
            "high_minus_low_behavior": high_low,
        },
        "composition": {
            "behavior_minus_best_single": composition_advantage,
            "behavior_oracle_gap": composition_gap,
        },
        "classifications": classifications,
    }
