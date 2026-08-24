"""Prespecified EXP004 summary figures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def _mean(result: dict[str, Any], key: str) -> float:
    return float(np.mean([row[key] for row in result["seeds"]]))


def save_figures(results: dict[str, dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True)
    sizes = (2, 4, 8, 16, 32, 64, 128)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for regime, style in (("fixed", "o-"), ("search_normalized", "s--")):
        primary = [
            results[f"random_m{size}_{regime}_primary_art_outstar"] for size in sizes
        ]
        axes[0].plot(
            sizes, [_mean(row, "A_single") for row in primary], style, label=regime
        )
        axes[1].plot(
            sizes,
            [_mean(row, "evaluation_behavior") for row in primary],
            style,
            label=f"learner—{regime}",
        )
        axes[1].plot(
            sizes,
            [_mean(row, "best_allowed_behavior") for row in primary],
            ":",
            alpha=0.7,
            label=f"oracle—{regime}",
        )
    for axis in axes:
        axis.set_xscale("log", base=2)
        axis.set_xticks(sizes, labels=[str(size) for size in sizes])
        axis.set_ylim(-0.03, 1.03)
        axis.legend(fontsize=8)
    axes[0].set(title="Initial repertoire coverage", xlabel="Bank size M", ylabel="A_single")
    axes[1].set(title="Behavior versus allowed oracle", xlabel="Bank size M", ylabel="Normalized final state")
    fig.tight_layout()
    fig.savefig(output / "bank_size_coverage_behavior.png", dpi=180)
    plt.close(fig)

    labels = ("low", "medium", "high")
    art = [results[f"controlled_{label}_primary_art_outstar"] for label in labels]
    bandit = [results[f"controlled_{label}_contextual_bandit"] for label in labels]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    width = 0.36
    axes[0].bar(x - width / 2, [_mean(row, "evaluation_behavior") for row in art], width, label="ART/outstar")
    axes[0].bar(x + width / 2, [_mean(row, "evaluation_behavior") for row in bandit], width, label="bandit")
    axes[1].bar(x - width / 2, [_mean(row, "t_alignment") for row in art], width, label="ART/outstar")
    axes[1].bar(x + width / 2, [_mean(row, "t_alignment") for row in bandit], width, label="bandit")
    for axis in axes:
        axis.set_xticks(x, labels)
        axis.legend(fontsize=8)
    axes[0].set(title="Controlled coverage and behavior", ylabel="Normalized final state")
    axes[1].set(title="Controlled coverage and learned T", ylabel="corr(T, role)")
    fig.tight_layout()
    fig.savefig(output / "controlled_coverage.png", dpi=180)
    plt.close(fig)

    composition_names = (
        "composition_random_selector",
        "composition_contextual_bandit",
        "composition_primary_art_outstar",
    )
    display = ("random", "bandit", "ART/outstar")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].bar(
        np.arange(3) - 0.24,
        [_mean(results[name], "best_single_behavior") for name in composition_names],
        0.24,
        label="best repeated single",
    )
    axes[0].bar(
        np.arange(3),
        [_mean(results[name], "evaluation_behavior") for name in composition_names],
        0.24,
        label="learner",
    )
    axes[0].bar(
        np.arange(3) + 0.24,
        [_mean(results[name], "best_allowed_behavior") for name in composition_names],
        0.24,
        label="allowed sequence",
    )
    axes[0].set_xticks(np.arange(3), display)
    axes[0].set_ylim(0.0, 1.05)
    axes[0].set(title="Low-single-coverage composition", ylabel="Normalized final state")
    axes[0].legend(fontsize=8)
    ablation_names = (
        "controlled_medium_primary_art_outstar",
        "controlled_medium_fixed_categories",
        "controlled_medium_no_new_category",
        "controlled_medium_no_category_modification",
        "controlled_medium_contextual_bandit",
    )
    ablation_display = ("full", "fixed", "no new", "no modify", "bandit")
    axes[1].bar(
        np.arange(len(ablation_names)),
        [_mean(results[name], "evaluation_behavior") for name in ablation_names],
    )
    axes[1].set_xticks(np.arange(len(ablation_names)), ablation_display, rotation=25)
    axes[1].set_ylim(0.0, 1.05)
    axes[1].set(title="Category contribution", ylabel="Normalized final state")
    fig.tight_layout()
    fig.savefig(output / "composition_and_categories.png", dpi=180)
    plt.close(fig)
