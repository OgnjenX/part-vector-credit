"""Create the manuscript summary figure from frozen EXP006 classifications."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

MODELS = (
    ("vector_oracle", "Oracle"),
    ("art_repertoire", "ART"),
    ("local_eligibility", "Eligibility"),
    ("art_eligibility_hybrid", "Hybrid"),
    ("random_no_learning", "Random"),
)

PANELS = (
    (
        "Late-trial success",
        "acquisition_late_success",
        "remap_late_success",
        0.60,
        (-0.05, 1.08),
    ),
    (
        "Topology-role correlation",
        "pre_remap_alignment",
        "post_remap_alignment",
        0.55,
        (-0.12, 1.08),
    ),
    (
        "Dendritic residual vectorization",
        "residual_vectorization_acquisition",
        "residual_vectorization_remap",
        0.01,
        (-0.035, 0.175),
    ),
    (
        "Prospective activity prediction",
        "prospective_activity_prediction_acquisition",
        "prospective_activity_prediction_remap",
        0.20,
        (-0.95, 1.08),
    ),
)


def values(
    intervals: dict[str, dict[str, dict[str, float]]], metric: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    means = np.asarray([intervals[key][metric]["mean"] for key, _ in MODELS])
    lows = np.asarray([intervals[key][metric]["ci95_low"] for key, _ in MODELS])
    highs = np.asarray([intervals[key][metric]["ci95_high"] for key, _ in MODELS])
    return means, means - lows, highs - means


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    record = json.loads(args.classification.read_text(encoding="utf-8"))
    intervals = record["intervals"]
    labels = [label for _, label in MODELS]
    positions = np.arange(len(labels))
    width = 0.36
    colors = ("#2F6690", "#D97706")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
    })
    figure, axes = plt.subplots(2, 2, figsize=(10.2, 6.8), constrained_layout=True)
    for axis, (title, acquisition_metric, remap_metric, floor, limits) in zip(
        axes.flat, PANELS, strict=True
    ):
        acquisition, acquisition_low, acquisition_high = values(
            intervals, acquisition_metric
        )
        remap, remap_low, remap_high = values(intervals, remap_metric)
        axis.bar(
            positions - width / 2,
            acquisition,
            width,
            yerr=np.vstack([acquisition_low, acquisition_high]),
            color=colors[0],
            capsize=2.5,
            label="Acquisition",
        )
        axis.bar(
            positions + width / 2,
            remap,
            width,
            yerr=np.vstack([remap_low, remap_high]),
            color=colors[1],
            capsize=2.5,
            label="Remap",
        )
        axis.axhline(0.0, color="#333333", linewidth=0.8)
        axis.axhline(
            floor,
            color="#7A1F1F",
            linestyle="--",
            linewidth=1.1,
            label="Frozen floor",
        )
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xticks(positions, labels, rotation=18, ha="right")
        axis.set_ylim(*limits)
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.6)
        axis.set_axisbelow(True)

    handles, legend_labels = axes[0, 0].get_legend_handles_labels()
    order = (1, 2, 0)
    figure.legend(
        [handles[index] for index in order],
        [legend_labels[index] for index in order],
        loc="outside upper center",
        ncol=3,
        frameon=False,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
