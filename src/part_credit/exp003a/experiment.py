"""EXP003a validation suite, metrics, figures, and outcome classification."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from .motif import MotifConfig, run_condition
from .plasticity import timing_curve

CONDITIONS = ("matched", "topdown_ablated", "shuffled", "mismatch")


def _summary(result: dict[str, object]) -> dict[str, Any]:
    before = result["before_probe"]
    after = result["after_probe"]
    latencies = np.asarray(result["presentation_latencies_ms"], dtype=float)
    finite_latency = np.isfinite(latencies)
    mean_training_latency = np.divide(
        np.nansum(latencies, axis=0),
        finite_latency.sum(axis=0),
        out=np.full(latencies.shape[1], np.nan),
        where=finite_latency.sum(axis=0) > 0,
    )
    cfg = result["config"]
    spike_times = np.asarray(result["lower_spike_times_ms"], dtype=float)
    relative_spike_times = np.mod(spike_times, cfg["cycle_ms"])
    pre_feedforward_spikes = int(np.sum(
        (relative_spike_times >= cfg["topdown_at_ms"])
        & (relative_spike_times < cfg["feedforward_at_ms"])
    ))
    return {
        "center": int(result["center"]),
        "competitor": int(result["competitor"]),
        "initial_weights": np.asarray(result["initial_weights"]).tolist(),
        "final_weights": np.asarray(result["final_weights"]).tolist(),
        "weight_change": np.asarray(result["weight_change"]).tolist(),
        "stdp_window_occupancy": np.asarray(result["stdp_window_occupancy"]).tolist(),
        "training_spike_count": np.bincount(
            np.asarray(result["lower_spike_indices"], dtype=int), minlength=2
        ).tolist(),
        "training_first_latency_mean_ms": mean_training_latency.tolist(),
        "spikes_after_topdown_before_feedforward": pre_feedforward_spikes,
        "future_before_spike_count": np.asarray(before["spike_counts"]).tolist(),
        "future_after_spike_count": np.asarray(after["spike_counts"]).tolist(),
        "future_before_latency_ms": np.asarray(before["mean_latency_ms"]).tolist(),
        "future_after_latency_ms": np.asarray(after["mean_latency_ms"]).tolist(),
        "surround_spike_count": len(result["inhibitory_spike_times_ms"]),
        "reset_spike_count": len(result["reset_spike_times_ms"]),
    }


def classify(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    matched = summaries["matched"]
    ablated = summaries["topdown_ablated"]
    mismatch = summaries["mismatch"]
    center = matched["center"]
    competitor = matched["competitor"]
    matched_delta = matched["weight_change"][center]
    competitor_delta = matched["weight_change"][competitor]
    ablated_max = max(abs(value) for value in ablated["weight_change"])
    mismatch_max = max(abs(value) for value in mismatch["weight_change"])
    before_count = matched["future_before_spike_count"][center]
    after_count = matched["future_after_spike_count"][center]
    criteria = {
        "matched_update_nonzero": matched_delta >= 0.04,
        "competitor_update_much_smaller": abs(competitor_delta) <= 0.25 * abs(matched_delta),
        "topdown_ablation_removes_advantage": ablated_max <= 0.25 * abs(matched_delta),
        "mismatch_suppresses_learning": mismatch_max <= 0.25 * abs(matched_delta),
        "matched_timing_inside_window": matched["stdp_window_occupancy"][center] >= 0.80,
        "competitor_timing_suppressed": matched["stdp_window_occupancy"][competitor] <= 0.25,
        "future_response_changed": after_count > before_count,
        "surround_circuit_operated": matched["surround_spike_count"] >= 1,
        "reset_circuit_operated": mismatch["reset_spike_count"] >= 1,
        "topdown_is_modulatory_alone": matched[
            "spikes_after_topdown_before_feedforward"
        ] == 0,
    }
    passed = sum(criteria.values())
    if passed == len(criteria):
        outcome = "A_VALIDATED"
    elif passed >= len(criteria) - 2:
        outcome = "B_PARTIALLY_VALIDATED"
    else:
        outcome = "C_FAILED"
    return {"outcome": outcome, "criteria": criteria, "passed": passed, "total": len(criteria)}


def run_suite(cfg: MotifConfig | None = None) -> dict[str, object]:
    if cfg is None:
        cfg = MotifConfig()
    raw = {condition: run_condition(condition, cfg) for condition in CONDITIONS}
    summaries = {name: _summary(result) for name, result in raw.items()}
    offsets = np.linspace(-30.0, 30.0, 121)
    curve = timing_curve(offsets, cfg.plasticity)
    return {
        "config": asdict(cfg),
        "conditions": summaries,
        "timing_curve": {"post_minus_pre_ms": offsets, "delta_weight": curve},
        "classification": classify(summaries),
        "_raw": raw,
    }


def save_figures(suite: dict[str, object], figure_dir: Path) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)
    raw = suite["_raw"]
    colors = ("#c43c39", "#3569a8")

    figure, axes = plt.subplots(4, 2, figsize=(13, 13), constrained_layout=True)
    for row, condition in enumerate(CONDITIONS):
        result = raw[condition]
        duration = 4 * result["config"]["cycle_ms"]
        for neuron in range(2):
            spikes = np.asarray(result["lower_spike_times_ms"])[
                np.asarray(result["lower_spike_indices"]) == neuron
            ]
            spikes = spikes[spikes < duration]
            axes[row, 0].scatter(spikes, np.full(spikes.size, neuron), s=18, color=colors[neuron])
        for presentation in range(4):
            pre = presentation * result["config"]["cycle_ms"] + result["config"]["feedforward_at_ms"]
            axes[row, 0].axvline(pre, color="black", alpha=0.2, linewidth=0.8)
        axes[row, 0].set_xlim(0, duration)
        axes[row, 0].set_yticks([0, 1], ["cell A", "cell B"])
        axes[row, 0].set_title(f"{condition}: lower-cell spikes (first 4 presentations)")
        weights = np.asarray(result["presentation_weights"])
        axes[row, 1].plot(weights[:, 0], color=colors[0], label="cell A")
        axes[row, 1].plot(weights[:, 1], color=colors[1], label="cell B")
        axes[row, 1].axhline(result["config"]["plasticity"]["w_baseline"], color="black", ls="--", lw=0.8)
        axes[row, 1].set_title(f"{condition}: local lower weights")
        axes[row, 1].set_xlabel("presentation")
        axes[row, 1].legend()
    axes[-1, 0].set_xlabel("time (ms)")
    figure.savefig(figure_dir / "mechanism_rasters_and_weights.png", dpi=180)
    plt.close(figure)

    summaries = suite["conditions"]
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    x = np.arange(len(CONDITIONS))
    width = 0.34
    axes[0].bar(x - width / 2, [summaries[name]["weight_change"][0] for name in CONDITIONS], width, label="cell A")
    axes[0].bar(x + width / 2, [summaries[name]["weight_change"][1] for name in CONDITIONS], width, label="cell B")
    axes[0].set_xticks(x, CONDITIONS, rotation=25, ha="right")
    axes[0].set_ylabel("Delta W_lower")
    axes[0].set_title("Local plasticity")
    axes[0].legend()
    axes[1].bar(x - width / 2, [summaries[name]["stdp_window_occupancy"][0] for name in CONDITIONS], width)
    axes[1].bar(x + width / 2, [summaries[name]["stdp_window_occupancy"][1] for name in CONDITIONS], width)
    axes[1].set_xticks(x, CONDITIONS, rotation=25, ha="right")
    axes[1].set_ylabel("fraction of presentations")
    axes[1].set_title("Post spike inside 25 ms window")
    curve = suite["timing_curve"]
    axes[2].plot(curve["post_minus_pre_ms"], curve["delta_weight"], color="#5d3a9b")
    axes[2].axhline(0, color="black", lw=0.8)
    axes[2].axvline(0, color="black", lw=0.8, ls="--")
    axes[2].set_xlabel("post minus pre spike (ms)")
    axes[2].set_ylabel("Delta weight / pair")
    axes[2].set_title("Reduced Eq. 5/6 timing relationship")
    figure.savefig(figure_dir / "timing_and_ablation_summary.png", dpi=180)
    plt.close(figure)

    matched = raw["matched"]
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.5), constrained_layout=True)
    before = matched["before_probe"]
    after = matched["after_probe"]
    labels = ["cell A", "cell B"]
    axes[0].bar(np.arange(2) - 0.18, before["spike_counts"], 0.36, label="before")
    axes[0].bar(np.arange(2) + 0.18, after["spike_counts"], 0.36, label="after")
    axes[0].set_xticks(np.arange(2), labels)
    axes[0].set_ylabel("spikes / identical probe")
    axes[0].set_title("Learning-off future response")
    axes[0].legend()
    axes[1].plot(before["voltage_time_ms"], before["voltage_mv"][0], label="A before", color="#c43c39", ls="--")
    axes[1].plot(after["voltage_time_ms"], after["voltage_mv"][0], label="A after", color="#c43c39")
    axes[1].set_xlim(0, matched["config"]["cycle_ms"])
    axes[1].set_xlabel("time (ms)")
    axes[1].set_ylabel("membrane voltage (mV)")
    axes[1].set_title("Same feedforward input, changed W")
    axes[1].legend()
    figure.savefig(figure_dir / "future_response.png", dpi=180)
    plt.close(figure)
