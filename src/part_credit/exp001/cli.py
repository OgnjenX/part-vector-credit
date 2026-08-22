"""Run EXP001 development or held-out confirmatory suites."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .experiment import (
    Exp001Config,
    run_art_search_probe,
    run_capacity_sweep,
    run_generalization,
    run_primary_suite,
    run_robustness_sweeps,
)


def _extract_raw(value: Any, prefix: str, raw: dict[str, np.ndarray]) -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for key, child in value.items():
            child_prefix = f"{prefix}__{key}" if prefix else key
            if key.startswith("_raw"):
                raw[child_prefix] = child
            else:
                cleaned[key] = _extract_raw(child, child_prefix, raw)
        return cleaned
    return value


def _classification(result: dict[str, Any]) -> dict[str, object]:
    conditions = result["primary"]["conditions"]
    full = conditions["grossberg_inspired_full"]["summary"]
    frozen = conditions["frozen_zero_plasticity"]["summary"]
    positive = conditions["explicit_vector_error_positive_control"]["summary"]
    suppressed = conditions["apical_pathway_suppressed"]["summary"]
    task_valid = positive["post_remap_late_success"] >= 0.70
    full_learns = (
        full["pre_remap_late_success"] >= 0.70
        and full["learning_improvement"] >= 0.20
        and full["pre_remap_late_success"] - frozen["pre_remap_late_success"] >= 0.15
    )
    vectorized = (
        full["post_dendritic_role_alignment"] >= 0.20
        and full["post_opposite_population_signs"] >= 0.80
        and full["post_residual_predicts_later_soma"] >= 0.20
    )
    apical_causal = (
        suppressed["post_remap_late_success"] <= full["post_remap_late_success"] - 0.15
        and suppressed["post_dendritic_role_alignment"] <= 0.5 * full["post_dendritic_role_alignment"]
    )
    if not task_valid:
        outcome = 5
        label = "Current model/task is too abstract or invalid to decide"
    elif not full_learns:
        outcome = 4
        label = "Grossberg-only abstraction cannot learn the hidden causal mapping"
    elif not vectorized:
        outcome = 3
        label = "Behavioral learning without dendritic vectorization"
    else:
        # Grossberg-only neuron patterns are frozen by protocol; success is basis selection.
        outcome = 2
        label = "Selection from a pre-existing random distributed basis"
    return {
        "outcome": outcome,
        "label": label,
        "task_valid": task_valid,
        "full_behavioral_criterion": full_learns,
        "vector_signature_criterion": vectorized,
        "apical_causal_criterion": apical_causal,
        "strong_sufficiency_possible_in_this_implementation": False,
        "reason": "Grossberg-only control patterns are frozen and contain no de novo sign-learning rule.",
    }


def _plot(result: dict[str, Any], output: Path) -> None:
    conditions = result["primary"]["conditions"]
    names = list(conditions)
    labels = {
        "frozen_zero_plasticity": "frozen",
        "random_policy_feedback": "random policy",
        "grossberg_inspired_full": "full",
        "no_structural_credit": "no structural credit",
        "no_working_memory": "no working memory",
        "no_motivated_attention": "no motivation",
        "no_now_print_gating": "no Now Print",
        "no_reset_search": "no reset/search",
        "no_match_resonance_gating": "no resonance gate",
        "shuffled_top_down_feedback": "shuffled feedback",
        "preexisting_random_basis_only": "frozen basis",
        "plastic_basis_engineering_probe": "plastic-basis probe",
        "apical_pathway_suppressed": "apical suppressed",
        "explicit_vector_error_positive_control": "vector-error control",
    }
    display_names = [labels[name] for name in names]
    summaries = [conditions[name]["summary"] for name in names]
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].bar(display_names, [row["post_remap_late_success"] for row in summaries])
    axes[0].axhline(0.7, color="black", linestyle="--", linewidth=1)
    axes[0].set_ylabel("post-remap late success")
    axes[1].bar(display_names, [row["post_dendritic_role_alignment"] for row in summaries])
    axes[1].axhline(0.2, color="black", linestyle="--", linewidth=1)
    axes[1].set_ylabel("soma-conditioned residual role alignment")
    capacities = sorted(result["capacity"], key=int)
    axes[2].plot(
        [int(x) for x in capacities],
        [result["capacity"][x]["summary"]["post_remap_late_success"] for x in capacities],
        marker="o",
        label="success",
    )
    axes[2].plot(
        [int(x) for x in capacities],
        [result["capacity"][x]["summary"]["best_initial_basis_alignment"] for x in capacities],
        marker="o",
        label="best initial alignment",
    )
    axes[2].set_xscale("log", base=2)
    axes[2].set_xlabel("random hypothesis capacity")
    axes[2].legend()
    for axis in axes[:2]:
        axis.tick_params(axis="x", rotation=55)
        for label in axis.get_xticklabels():
            label.set_horizontalalignment("right")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("development", "confirmatory"), required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("results/exp001"))
    parser.add_argument("--quick", action="store_true", help="two seeds and 200 trials for smoke tests")
    args = parser.parse_args()
    cfg = Exp001Config()
    if args.quick:
        cfg = Exp001Config(
            trials=200,
            evaluation_window=30,
            development_seeds=(0, 1),
            confirmatory_seeds=(1000, 1001),
        )
    seeds = cfg.development_seeds if args.phase == "development" else cfg.confirmatory_seeds
    result: dict[str, Any] = {
        "phase": args.phase,
        "primary": run_primary_suite(cfg, args.phase),
        "capacity": run_capacity_sweep(cfg, seeds),
    }
    if args.phase == "development":
        result["robustness"] = run_robustness_sweeps(cfg)
        result["generalization"] = run_generalization(cfg)
        result["art_search_probe"] = run_art_search_probe(cfg)
    result["classification"] = _classification(result)
    raw: dict[str, np.ndarray] = {}
    cleaned = _extract_raw(result, "", raw)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"exp001_{args.phase}"
    (args.output_dir / f"{stem}.json").write_text(json.dumps(cleaned, indent=2) + "\n")
    np.savez_compressed(args.output_dir / f"{stem}_trial_raw.npz", **raw)
    _plot(cleaned, args.output_dir / f"{stem}.png")
    print(json.dumps({
        "classification": cleaned["classification"],
        "full": cleaned["primary"]["conditions"]["grossberg_inspired_full"]["summary"],
        "positive_control": cleaned["primary"]["conditions"]["explicit_vector_error_positive_control"]["summary"],
    }, indent=2))


if __name__ == "__main__":
    main()
