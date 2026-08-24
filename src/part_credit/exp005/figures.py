"""Figures for the EXP005 generic diagnostic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def save_figures(results: dict[str, dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True)
    conditions = (
        "generic_node_perturbation",
        "outcome_shuffled",
        "exploration_removed",
        "hidden_vector_oracle",
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    x = np.arange(len(conditions))
    for phase_index, metric in enumerate(("pre_remap_alignment", "post_remap_alignment")):
        means = [
            np.mean([row[metric] for row in results[f"n32_{condition}"]["seeds"]])
            for condition in conditions
        ]
        axes[phase_index].bar(x, means, color=("#35618f", "#a76a31", "#8b8b8b", "#4a8f59"))
        axes[phase_index].axhline(0.0, color="black", linewidth=0.8)
        axes[phase_index].set_xticks(x, ["generic", "shuffled", "no exploration", "oracle"], rotation=18)
        axes[phase_index].set_ylim(-0.2, 1.05)
        axes[phase_index].set_ylabel("topology–role correlation")
        axes[phase_index].set_title("Acquisition" if phase_index == 0 else "After hidden remap")
    fig.savefig(output / "n32_alignment_controls.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.8, 4.4), constrained_layout=True)
    for condition, color in (
        ("generic_node_perturbation", "#35618f"),
        ("outcome_shuffled", "#a76a31"),
        ("hidden_vector_oracle", "#4a8f59"),
    ):
        means = []
        for n in (8, 16, 32, 64):
            means.append(np.mean([
                row["post_remap_alignment"]
                for row in results[f"n{n}_{condition}"]["seeds"]
            ]))
        ax.plot((8, 16, 32, 64), means, marker="o", label=condition)
    ax.set_xscale("log", base=2)
    ax.set_xticks((8, 16, 32, 64), ("8", "16", "32", "64"))
    ax.set_ylim(-0.2, 1.05)
    ax.set_xlabel("RSC population size N")
    ax.set_ylabel("post-remap topology–role correlation")
    ax.legend(frameon=False)
    fig.savefig(output / "scaling_after_remap.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
    for condition, color in (
        ("generic_node_perturbation", "#35618f"),
        ("outcome_shuffled", "#a76a31"),
        ("exploration_removed", "#8b8b8b"),
    ):
        trajectories = np.stack([
            raw["episode_alignment"]
            for raw in results[f"n32_{condition}"]["_raw"]
        ])
        ax.plot(np.mean(trajectories, axis=0), color=color, label=condition)
    remap = trajectories.shape[1] // 2
    ax.axvline(remap, color="black", linestyle="--", linewidth=1, label="hidden remap")
    ax.set_ylim(-0.4, 1.05)
    ax.set_xlabel("episode")
    ax.set_ylabel("current topology–current role correlation")
    ax.legend(frameon=False)
    fig.savefig(output / "n32_acquisition_trajectory.png", dpi=180)
    plt.close(fig)

