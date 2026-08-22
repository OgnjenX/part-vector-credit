"""Frozen EXP003b summary figures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def save_figures(suite: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    names = (
        "frozen_no_learning",
        "random_controller",
        "contextual_bandit",
        "bandit_generic_hebb",
        "primary_part_t_smart",
        "primary_t_to_smart_blocked",
        "explicit_vector_credit_positive_control",
    )
    labels = ("frozen", "random", "bandit", "Hebb", "primary", "T→SMART off", "vector")
    summaries = {name: suite["conditions"][name]["summary"] for name in names}

    figure, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    x = np.arange(len(names))
    width = 0.36
    axes[0].bar(
        x - width / 2,
        [summaries[name]["pre_remap_evaluation_success"] for name in names],
        width,
        label="before remap",
    )
    axes[0].bar(
        x + width / 2,
        [summaries[name]["post_remap_evaluation_success"] for name in names],
        width,
        label="after remap",
    )
    axes[0].set_xticks(x, labels, rotation=30, ha="right")
    axes[0].set_ylabel("evaluation success")
    axes[0].set_title("Closed-loop behavior")
    axes[0].legend()

    primary = summaries["primary_part_t_smart"]
    axes[1].bar(
        np.arange(4),
        [
            primary["pre_d_to_w"],
            primary["pre_d_to_s"],
            primary["post_d_to_w"],
            primary["post_d_to_s"],
        ],
        color=("#4c78a8", "#72b7b2", "#f58518", "#e45756"),
    )
    axes[1].axhline(0.20, color="black", ls="--", lw=1, label="frozen floor")
    axes[1].axhline(0.0, color="black", lw=0.7)
    axes[1].set_xticks(np.arange(4), ("pre D→W", "pre D→S", "post D→W", "post D→S"), rotation=25)
    axes[1].set_ylabel("within-h correlation")
    axes[1].set_title("Primary longitudinal chain")
    axes[1].legend()

    axes[2].bar(
        np.arange(4),
        [
            primary["pre_topdown_alignment"],
            primary["post_topdown_alignment"],
            primary["old_topdown_new_alignment"],
            primary["context_topdown_opposition"],
        ],
        color="#6f4e7c",
    )
    axes[2].axhline(0.20, color="black", ls="--", lw=1)
    axes[2].set_xticks(
        np.arange(4),
        ("pre T↔c", "post T↔c", "old T↔new c", "context opposition"),
        rotation=25,
    )
    axes[2].set_title("Learned expectation and remap")
    figure.savefig(output / "behavior_longitudinal_expectancy.png", dpi=180)
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    phase_names = ("select", "pre-action", "action", "feedback", "outcome", "post")
    for name, label, color in (
        ("primary_part_t_smart", "primary", "#4c78a8"),
        ("bandit_direct_copy_apical", "direct copy", "#f2cf5b"),
        ("explicit_vector_credit_positive_control", "vector control", "#e45756"),
    ):
        axes[0].plot(
            phase_names,
            suite["conditions"][name]["summary"]["timing_pre_role_alignment"],
            marker="o",
            label=label,
            color=color,
        )
    axes[0].axhline(0, color="black", lw=0.7)
    axes[0].set_ylabel("residual signal ↔ hidden role")
    axes[0].set_title("Timing before hidden remap")
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].legend()

    contrasts = (
        "primary_part_t_smart",
        "part_learned_t_no_smart",
        "primary_t_to_smart_blocked",
        "primary_t_learning_disabled",
    )
    contrast_labels = ("primary", "no SMART", "T→SMART off", "T learning off")
    axes[1].bar(
        np.arange(len(contrasts)),
        [suite["conditions"][name]["summary"]["weight_change_norm"] for name in contrasts],
        color=("#4c78a8", "#72b7b2", "#e45756", "#b279a2"),
    )
    axes[1].set_xticks(np.arange(len(contrasts)), contrast_labels, rotation=25)
    axes[1].set_ylabel("||ΔW_lower||")
    axes[1].set_title("Causal local-plasticity contrast")
    figure.savefig(output / "timing_and_causal_ablation.png", dpi=180)
    plt.close(figure)
