"""Command-line runner for the preregistered EXP002 suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from .experiment import CONDITIONS, Exp002Config, run_primary_suite, run_robustness


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items() if key != "_raw"}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _paired_ci(
    primary: list[float], comparator: list[float], rng: np.random.Generator
) -> list[float]:
    differences = np.asarray(primary) - np.asarray(comparator)
    samples = rng.choice(differences, (5000, len(differences)), replace=True).mean(axis=1)
    return np.quantile(samples, [0.025, 0.975]).tolist()


def statistical_comparisons(suite: dict[str, Any]) -> dict[str, Any]:
    primary = suite["conditions"]["part_outstar_expectancy_primary"]["seeds"]
    output: dict[str, Any] = {}
    rng = np.random.default_rng(90202)
    for comparator_name in (
        "frozen_no_learning",
        "random_controller",
        "contextual_bandit",
        "bandit_selected_pattern_copy",
        "part_selection_no_expectancy",
        "primary_apical_learning_suppressed",
        "explicit_vector_error_positive_control",
    ):
        comparator = suite["conditions"][comparator_name]["seeds"]
        output[comparator_name] = {}
        for metric in (
            "pre_remap_evaluation_success",
            "post_remap_evaluation_success",
            "pre_remap_topdown_alignment",
            "post_remap_topdown_alignment",
            "pre_longitudinal_prediction",
            "post_longitudinal_prediction",
        ):
            primary_values = [float(row[metric]) for row in primary]
            comparator_values = [float(row[metric]) for row in comparator]
            output[comparator_name][metric] = {
                "paired_mean_difference": float(np.mean(
                    np.asarray(primary_values) - np.asarray(comparator_values)
                )),
                "paired_bootstrap_ci95": _paired_ci(primary_values, comparator_values, rng),
            }
    return output


def _figure(suite: dict[str, Any], path: Path) -> None:
    names = list(CONDITIONS)
    summaries = [suite["conditions"][name]["summary"] for name in names]
    labels = [
        "frozen", "random", "bandit", "bandit+copy", "pART select", "PRIMARY",
        "no structural", "no WM", "no motivation", "no reset", "no resonance", "shuffled T",
        "T learn off", "T expression off", "plastic B", "vector error",
    ]
    figure, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)
    x = np.arange(len(names))
    axes[0, 0].bar(x - 0.18, [row["pre_remap_evaluation_success"] for row in summaries], 0.36)
    axes[0, 0].bar(x + 0.18, [row["post_remap_evaluation_success"] for row in summaries], 0.36)
    axes[0, 0].set_title("Behavior before / after hidden remap")
    axes[0, 0].set_ylabel("success fraction")
    axes[0, 0].legend(["pre", "post"])
    axes[0, 1].bar(x - 0.18, [row["pre_remap_topdown_alignment"] for row in summaries], 0.36)
    axes[0, 1].bar(x + 0.18, [row["post_remap_topdown_alignment"] for row in summaries], 0.36)
    axes[0, 1].set_title("Selected top-down pattern vs hidden causal roles")
    axes[0, 1].legend(["pre", "post"])
    axes[1, 0].bar(x - 0.18, [row["pre_longitudinal_prediction"] for row in summaries], 0.36)
    axes[1, 0].bar(x + 0.18, [row["post_longitudinal_prediction"] for row in summaries], 0.36)
    axes[1, 0].set_title("Early residual predicts later soma change")
    axes[1, 0].legend(["pre", "post"])
    phase_labels = ["selection", "action", "feedback", "outcome", "post"]
    for name in (
        "bandit_selected_pattern_copy",
        "part_outstar_expectancy_primary",
        "explicit_vector_error_positive_control",
    ):
        axes[1, 1].plot(
            phase_labels,
            suite["conditions"][name]["summary"]["timing_post_role_alignment"],
            marker="o",
            label=name,
        )
    axes[1, 1].set_title("Post-remap dendritic role alignment by timing")
    axes[1, 1].legend(fontsize=8)
    for axis in axes.flat[:3]:
        axis.axhline(0.0, color="black", linewidth=0.7)
        axis.set_xticks(x, labels, rotation=60, ha="right", fontsize=8)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def save_suite(suite: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    raw_dir = output / "raw"
    raw_dir.mkdir()
    for name, result in suite["conditions"].items():
        np.savez_compressed(raw_dir / f"{name}.npz", **result["_raw"])
    with (output / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(_json_ready(suite), handle, indent=2)
    with (output / "statistics.json").open("w", encoding="utf-8") as handle:
        json.dump(_json_ready(statistical_comparisons(suite)), handle, indent=2)
    _figure(suite, output / "conditions.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("development", "confirmatory"), default="development")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--with-robustness", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    if args.phase == "confirmatory":
        marker = root / "experiments" / "exp002" / "FROZEN_PROTOCOL.json"
        if not marker.exists():
            raise SystemExit("confirmatory run blocked: frozen protocol marker is absent")
        if args.output.exists():
            raise SystemExit("confirmatory run blocked: output path already exists")
    cfg = Exp002Config()
    suite = run_primary_suite(cfg, args.phase)
    save_suite(suite, args.output)
    if args.with_robustness:
        robustness = run_robustness(cfg)
        with (args.output / "development_robustness.json").open("w", encoding="utf-8") as handle:
            json.dump(_json_ready(robustness), handle, indent=2)


if __name__ == "__main__":
    main()
