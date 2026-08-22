"""POST HOC failure localization from frozen EXP003b held-out arrays only."""

from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from part_credit.exp003b.analysis import residual_error_signal, safe_corr
from part_credit.exp003b.spiking_cache import SmartResponseCache

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "results/exp003b/frozen_v1"
RAW_PATH = FROZEN / "raw/primary_part_t_smart.npz"
CACHE_PATH = ROOT / "results/exp003b/smart_response_cache.npz"
OUTPUT = ROOT / "experiments/exp003b_posthoc/results_v3"

SEEDS = tuple(range(3100, 3112))
TOPDOWN_SCALE = 0.45
V_REST_MV = -65.0
E_EXC_MV = 0.0
E_INH_MV = -80.0
TAU_MEMBRANE_MS = 10.0
ZERO_WEIGHT_EPS = 1e-8
LATENCY_CHANGE_EPS_MS = 0.025
BOOTSTRAPS = 5000

UNITS = (
    ("pre", 0, 40, 60, 100, 39, 99),
    ("post", 120, 160, 200, 240, 159, 239),
)

REPRESENTATIONS = (
    "raw_t",
    "clipped_t",
    "g_td",
    "neg_g_inh",
    "net_topdown_peak_envelope",
    "latency_advance",
    "created_spike_frequency",
    "apical_mean",
    "apical_improvement_contrast",
    "d_residual",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bootstrap_ci(values: np.ndarray, seed: int) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = rng.choice(values, (BOOTSTRAPS, len(values)), replace=True).mean(axis=1)
    return [float(value) for value in np.quantile(means, (0.025, 0.975))]


def verify_frozen_evidence() -> dict[str, Any]:
    manifest = json.loads((FROZEN / "SHA256SUMS.json").read_text(encoding="utf-8"))
    mismatches = [
        relative
        for relative, expected in manifest.items()
        if sha256(FROZEN / relative) != expected
    ]
    statistics = json.loads((FROZEN / "statistics.json").read_text(encoding="utf-8"))
    if mismatches:
        raise RuntimeError(f"frozen evidence hash mismatch: {mismatches}")
    if statistics["outcome"] != "C_COMPOSITION_FAILS_LONGITUDINAL_CHAIN":
        raise RuntimeError("unexpected frozen EXP003b classification")
    return {
        "manifest_files": len(manifest),
        "mismatches": mismatches,
        "frozen_outcome": statistics["outcome"],
        "raw_sha256": sha256(RAW_PATH),
        "cache_sha256": sha256(CACHE_PATH),
    }


def context_mask(
    raw: dict[str, np.ndarray], seed_index: int, start: int, stop: int, context: int
) -> np.ndarray:
    episode_context = raw["episode_scalar"][seed_index, :, 1].astype(int)
    episodes = np.arange(len(episode_context))
    episode_mask = (episodes >= start) & (episodes < stop) & (episode_context == context)
    return np.repeat(episode_mask[:, None], raw["hypothesis"].shape[2], axis=1)


def fixed_hypothesis(
    hypotheses: np.ndarray, early_mask: np.ndarray, late_mask: np.ndarray
) -> int:
    selected = np.concatenate((hypotheses[early_mask], hypotheses[late_mask]))
    return int(np.argmax(np.bincount(selected, minlength=16)))


def weight_state(
    raw: dict[str, np.ndarray], seed_index: int, hypothesis: int, boundary: int
) -> np.ndarray:
    selected = (
        raw["hypothesis"][seed_index] == hypothesis
    ) & (np.arange(raw["hypothesis"].shape[1])[:, None] <= boundary)
    positions = np.argwhere(selected)
    if not len(positions):
        return np.full(raw["soma"].shape[-1], 0.60)
    episode, frame = positions[-1]
    return raw["weight_after"][seed_index, episode, frame].astype(float)


def infer_motor_grid(
    raw: dict[str, np.ndarray], seed_index: int, hypothesis: int, cache_payload: Any
) -> np.ndarray:
    motor_axis = cache_payload["axis_motor"].astype(float)
    weight_axis = cache_payload["axis_weight"].astype(float)
    shape = tuple(int(value) for value in cache_payload["shape"])
    gff = cache_payload["g_ff_peak"].reshape(shape)
    selected = np.argwhere(raw["hypothesis"][seed_index] == hypothesis)
    if not len(selected):
        raise RuntimeError(f"hypothesis {hypothesis} never observed")
    estimates = []
    for episode, frame in selected[: min(12, len(selected))]:
        weight = raw["weight_before"][seed_index, episode, frame]
        observed = raw["g_ff_peak"][seed_index, episode, frame]
        estimate = np.empty(len(observed))
        for neuron in range(len(observed)):
            w_index = int(np.abs(weight_axis - weight[neuron]).argmin())
            candidates = gff[:, w_index, 0, 0, 0]
            estimate[neuron] = motor_axis[int(np.abs(candidates - observed[neuron]).argmin())]
        estimates.append(estimate)
    inferred = np.median(np.stack(estimates), axis=0)
    # The runtime motor drive is fixed by hypothesis; all sampled cache-grid
    # reconstructions must agree up to the discrete axis spacing.
    if np.max(np.ptp(np.stack(estimates), axis=0)) > 1e-9:
        raise RuntimeError("motor-grid reconstruction was not invariant across frames")
    return inferred


def held_h_probe(
    cache: SmartResponseCache, motor: np.ndarray, weight: np.ndarray
) -> np.ndarray:
    return cache.frame(
        motor=motor,
        weight=weight,
        topdown=np.zeros_like(weight),
        reset=False,
        plastic=False,
    )["soma"]


def mean_or_zero(values: np.ndarray, mask: np.ndarray) -> np.ndarray:
    if not np.any(mask):
        return np.zeros(values.shape[-1])
    return values[mask].mean(axis=0).astype(float)


def improvement_contrast(values: np.ndarray, improvements: np.ndarray) -> np.ndarray:
    split = float(np.median(improvements))
    improved = improvements > split
    if not np.any(improved) or not np.any(~improved):
        return np.zeros(values.shape[-1])
    return values[improved].mean(axis=0) - values[~improved].mean(axis=0)


def latency_advance_vector(
    actual: np.ndarray, counterfactual: np.ndarray
) -> np.ndarray:
    both = np.isfinite(actual) & np.isfinite(counterfactual)
    difference = counterfactual - actual
    output = np.zeros(actual.shape[-1], dtype=float)
    for neuron in range(actual.shape[-1]):
        selected = both[:, neuron]
        if np.any(selected):
            output[neuron] = float(np.mean(difference[selected, neuron]))
    return output


def net_peak_envelope(
    g_td: np.ndarray, g_inh: np.ndarray, v_peak_mv: np.ndarray
) -> np.ndarray:
    """Equation-derived top-down dV/dt envelope in mV/ms.

    Frozen raw data retain separate maxima, not time-aligned traces. This uses
    the actual SMART-derived membrane equation and recorded V peak, without a
    fitted subtraction coefficient, but is explicitly not an instantaneous or
    integrated current.
    """

    excitatory = g_td * (E_EXC_MV - v_peak_mv) / TAU_MEMBRANE_MS
    inhibitory = g_inh * (E_INH_MV - v_peak_mv) / TAU_MEMBRANE_MS
    return excitatory + inhibitory


def analyze_unit(
    raw: dict[str, np.ndarray],
    seed_index: int,
    seed: int,
    context: int,
    label: str,
    early_start: int,
    early_stop: int,
    late_start: int,
    late_stop: int,
    early_boundary: int,
    late_boundary: int,
    cache: SmartResponseCache,
    cache_payload: Any,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    early_mask = context_mask(raw, seed_index, early_start, early_stop, context)
    late_mask = context_mask(raw, seed_index, late_start, late_stop, context)
    hypothesis = fixed_hypothesis(raw["hypothesis"][seed_index], early_mask, late_mask)
    early_h = early_mask & (raw["hypothesis"][seed_index] == hypothesis)

    raw_t_frames = raw["topdown"][seed_index][early_h].astype(float)
    clipped_frames = np.clip(raw_t_frames / TOPDOWN_SCALE, 0.0, 1.0)
    g_td_frames = raw["g_td_peak"][seed_index][early_h].astype(float)
    g_inh_frames = raw["g_inh_peak"][seed_index][early_h].astype(float)
    v_peak_frames = raw["v_peak_mv"][seed_index][early_h].astype(float)
    soma_frames = raw["soma"][seed_index][early_h].astype(float)
    dendrite_frames = raw["dendrite_phases"][seed_index][early_h, 1].astype(float)
    improvement = raw["error_improvement"][seed_index][early_h].astype(float)
    actual_latency = raw["first_latency_ms"][seed_index][early_h].astype(float)
    no_t_latency = raw["counterfactual_no_t_latency_ms"][seed_index][early_h].astype(float)
    actual_spikes = raw["spike_count"][seed_index][early_h].astype(float)
    no_t_spikes = raw["counterfactual_no_t_spike_count"][seed_index][early_h].astype(float)
    apical_frames = (
        dendrite_frames
        - 0.35 * soma_frames
        - 0.20 * soma_frames.mean(axis=1, keepdims=True)
    )

    early_weight = weight_state(raw, seed_index, hypothesis, early_boundary)
    late_weight = weight_state(raw, seed_index, hypothesis, late_boundary)
    delta_weight = late_weight - early_weight
    motor = infer_motor_grid(raw, seed_index, hypothesis, cache_payload)
    early_probe = held_h_probe(cache, motor, early_weight)
    late_probe = held_h_probe(cache, motor, late_weight)
    delta_soma = late_probe - early_probe

    variables = {
        "raw_t": raw_t_frames.mean(axis=0),
        "clipped_t": clipped_frames.mean(axis=0),
        "g_td": g_td_frames.mean(axis=0),
        "neg_g_inh": -g_inh_frames.mean(axis=0),
        "net_topdown_peak_envelope": net_peak_envelope(
            g_td_frames, g_inh_frames, v_peak_frames
        ).mean(axis=0),
        "latency_advance": latency_advance_vector(actual_latency, no_t_latency),
        "created_spike_frequency": (
            (actual_spikes > no_t_spikes).mean(axis=0)
        ),
        "apical_mean": apical_frames.mean(axis=0),
        "apical_improvement_contrast": improvement_contrast(
            apical_frames, improvement
        ),
        "d_residual": residual_error_signal(soma_frames, dendrite_frames, improvement),
    }
    role_episode = next(
        episode
        for episode in range(early_start, early_stop)
        if int(raw["episode_scalar"][seed_index, episode, 1]) == context
    )
    role = raw["causal"][seed_index, role_episode].astype(float)

    row: dict[str, Any] = {
        "seed": seed,
        "period": label,
        "context": context,
        "hypothesis": hypothesis,
        "early_events": int(np.sum(early_h)),
        "delta_w_nonzero_neurons": int(np.sum(np.abs(delta_weight) > ZERO_WEIGHT_EPS)),
        "delta_w_zero_neurons": int(np.sum(np.abs(delta_weight) <= ZERO_WEIGHT_EPS)),
        "delta_w_to_delta_s": safe_corr(delta_weight, delta_soma),
        "raw_t_to_clipped_t": safe_corr(variables["raw_t"], variables["clipped_t"]),
        "clipped_t_to_g_td": safe_corr(variables["clipped_t"], variables["g_td"]),
        "raw_t_to_neg_g_inh": safe_corr(variables["raw_t"], variables["neg_g_inh"]),
        "g_td_to_net_topdown": safe_corr(
            variables["g_td"], variables["net_topdown_peak_envelope"]
        ),
        "neg_g_inh_to_net_topdown": safe_corr(
            variables["neg_g_inh"], variables["net_topdown_peak_envelope"]
        ),
        "net_topdown_to_d_residual": safe_corr(
            variables["net_topdown_peak_envelope"], variables["d_residual"]
        ),
        "net_topdown_to_apical_mean": safe_corr(
            variables["net_topdown_peak_envelope"], variables["apical_mean"]
        ),
        "apical_mean_to_improvement_contrast": safe_corr(
            variables["apical_mean"], variables["apical_improvement_contrast"]
        ),
        "apical_improvement_contrast_to_d_residual": safe_corr(
            variables["apical_improvement_contrast"], variables["d_residual"]
        ),
    }
    for name, values in variables.items():
        row[f"{name}_to_delta_w"] = safe_corr(values, delta_weight)
        row[f"{name}_to_delta_s"] = safe_corr(values, delta_soma)
        row[f"{name}_to_role"] = safe_corr(values, role)
    vectors = {
        **variables,
        "delta_weight": delta_weight,
        "delta_soma": delta_soma,
        "role": role,
    }
    return row, vectors


def aggregate_seed_rows(unit_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    numeric_keys = [
        key
        for key, value in unit_rows[0].items()
        if key not in {"seed", "period", "context", "hypothesis"}
        and isinstance(value, (int, float, np.number))
    ]
    output = []
    for seed in SEEDS:
        rows = [row for row in unit_rows if row["seed"] == seed]
        output.append({
            "seed": seed,
            **{key: float(np.mean([row[key] for row in rows])) for key in numeric_keys},
        })
    return output


def summarize_seed_metrics(seed_rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [key for key in seed_rows[0] if key != "seed"]
    return {
        key: {
            "mean": float(np.mean([row[key] for row in seed_rows])),
            "ci95": bootstrap_ci(
                np.asarray([row[key] for row in seed_rows]), 73000 + index
            ),
            "n_seeds": len(seed_rows),
        }
        for index, key in enumerate(keys)
    }


def engagement_summary(raw: dict[str, np.ndarray]) -> dict[str, Any]:
    evaluation = raw["episode_scalar"][:, :, 2].astype(bool)
    train = np.repeat(
        np.repeat((~evaluation)[:, :, None], raw["hypothesis"].shape[2], axis=2)[..., None],
        raw["soma"].shape[-1],
        axis=3,
    )
    actual_spikes = raw["spike_count"]
    no_t_spikes = raw["counterfactual_no_t_spike_count"]
    actual_latency = raw["first_latency_ms"]
    no_t_latency = raw["counterfactual_no_t_latency_ms"]
    count_changed = actual_spikes != no_t_spikes
    created = (actual_spikes > 0) & (no_t_spikes == 0)
    both = np.isfinite(actual_latency) & np.isfinite(no_t_latency)
    latency_changed = both & (
        np.abs(no_t_latency - actual_latency) > LATENCY_CHANGE_EPS_MS
    )
    frame_delta_w = raw["weight_after"] - raw["weight_before"]

    def fraction_per_seed(mask: np.ndarray, denominator: np.ndarray) -> np.ndarray:
        numerator = np.sum(mask & denominator, axis=(1, 2, 3))
        denom = np.sum(denominator, axis=(1, 2, 3))
        return numerator / denom

    results = {}
    for name, mask in (
        ("spike_count_changed_fraction", count_changed),
        ("topdown_created_spike_fraction", created),
        ("latency_changed_all_cellframes_fraction", latency_changed),
        ("latency_comparable_fraction", both),
        ("frame_delta_w_nonzero_fraction", np.abs(frame_delta_w) > ZERO_WEIGHT_EPS),
    ):
        values = fraction_per_seed(mask, train)
        results[name] = {
            "mean": float(values.mean()),
            "ci95": bootstrap_ci(values, 74000 + len(results)),
        }
    comparable_changed = []
    for seed_index in range(len(SEEDS)):
        selected = both[seed_index] & train[seed_index]
        comparable_changed.append(
            float(np.mean(latency_changed[seed_index][selected])) if np.any(selected) else 0.0
        )
    values = np.asarray(comparable_changed)
    results["latency_changed_given_comparable_fraction"] = {
        "mean": float(values.mean()),
        "ci95": bootstrap_ci(values, 74010),
    }
    deltas = frame_delta_w[train]
    results["frame_delta_w_distribution"] = {
        "minimum": float(np.min(deltas)),
        "q01": float(np.quantile(deltas, 0.01)),
        "q25": float(np.quantile(deltas, 0.25)),
        "median": float(np.median(deltas)),
        "q75": float(np.quantile(deltas, 0.75)),
        "q99": float(np.quantile(deltas, 0.99)),
        "maximum": float(np.max(deltas)),
        "unique_rounded_1e_8": len(np.unique(np.round(deltas, 8))),
    }
    return results


def engaged_subset_diagnostics(
    vectors_by_seed: dict[int, list[dict[str, np.ndarray]]]
) -> dict[str, Any]:
    seed_rows = []
    for seed, units in vectors_by_seed.items():
        delta_w = np.concatenate([unit["delta_weight"] for unit in units])
        engaged = np.abs(delta_w) > ZERO_WEIGHT_EPS
        row: dict[str, Any] = {
            "seed": seed,
            "engaged_cells": int(np.sum(engaged)),
            "total_cells": len(engaged),
        }
        for name in REPRESENTATIONS:
            values = np.concatenate([unit[name] for unit in units])
            row[f"{name}_to_delta_w_engaged"] = safe_corr(
                values[engaged], delta_w[engaged]
            )
        seed_rows.append(row)
    summary = summarize_seed_metrics(seed_rows)
    return {"per_seed": seed_rows, "summary": summary}


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metric(summary: dict[str, Any], key: str) -> tuple[float, list[float]]:
    item = summary[key]
    return float(item["mean"]), [float(value) for value in item["ci95"]]


def save_figures(summary: dict[str, Any], engagement: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True)
    role_keys = [f"{name}_to_role" for name in (
        "raw_t", "clipped_t", "g_td", "neg_g_inh",
        "net_topdown_peak_envelope", "apical_mean",
        "apical_improvement_contrast", "d_residual",
    )]
    role_labels = (
        "raw T", "clipped T", "g_td", "-g_inh", "net envelope",
        "mean apical", "apical Δerror", "D residual",
    )
    arrow_keys = [f"{name}_to_delta_w" for name in (
        "raw_t", "clipped_t", "g_td", "neg_g_inh",
        "net_topdown_peak_envelope", "latency_advance",
        "created_spike_frequency", "apical_mean",
        "apical_improvement_contrast", "d_residual",
    )] + ["net_topdown_to_d_residual", "delta_w_to_delta_s"]
    arrow_labels = (
        "raw T→ΔW", "clip T→ΔW", "g_td→ΔW", "-g_inh→ΔW", "net→ΔW",
        "latency→ΔW", "created spike→ΔW", "mean apical→ΔW",
        "apical Δerror→ΔW", "D residual→ΔW",
        "net→D residual", "ΔW→ΔS",
    )

    figure, axes = plt.subplots(1, 2, figsize=(14, 8.0), constrained_layout=True)
    for axis, keys, labels, title in (
        (axes[0], role_keys, role_labels, "Hidden-role alignment by representation"),
        (axes[1], arrow_keys, arrow_labels, "Failure localization along the causal chain"),
    ):
        means = [summary[key]["mean"] for key in keys]
        cis = [summary[key]["ci95"] for key in keys]
        errors = np.asarray([
            [mean - ci[0] for mean, ci in zip(means, cis)],
            [ci[1] - mean for mean, ci in zip(means, cis)],
        ])
        positions = np.arange(len(keys))
        colors = ["#4c78a8" if mean >= 0 else "#f2cf5b" for mean in means]
        axis.barh(positions, means, xerr=errors, color=colors, edgecolor="#263238")
        axis.axvline(0.0, color="#263238", lw=1)
        axis.set_yticks(positions, labels)
        axis.invert_yaxis()
        axis.set_xlabel("mean within-fixed-h correlation; 95% seed bootstrap CI")
        axis.set_title(title)
        axis.grid(axis="x", color="#d9dee3", lw=0.7)
    figure.savefig(output / "failure_localization.png", dpi=180)
    plt.close(figure)

    names = (
        "spike_count_changed_fraction",
        "topdown_created_spike_fraction",
        "latency_changed_all_cellframes_fraction",
        "latency_comparable_fraction",
        "frame_delta_w_nonzero_fraction",
    )
    labels = (
        "spike count changed", "spike created", "latency changed (all)",
        "latency comparable", "frame ΔW nonzero",
    )
    means = [engagement[name]["mean"] for name in names]
    cis = [engagement[name]["ci95"] for name in names]
    errors = np.asarray([
        [mean - ci[0] for mean, ci in zip(means, cis)],
        [ci[1] - mean for mean, ci in zip(means, cis)],
    ])
    figure, axis = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    positions = np.arange(len(names))
    axis.barh(positions, means, xerr=errors, color="#4c78a8", edgecolor="#263238")
    axis.set_yticks(positions, labels)
    axis.invert_yaxis()
    axis.set_xlabel("fraction of training cell-frames; 95% seed bootstrap CI")
    axis.set_title("SMART engagement is sparse in frozen EXP003b")
    axis.grid(axis="x", color="#d9dee3", lw=0.7)
    figure.savefig(output / "engagement_sparsity.png", dpi=180)
    plt.close(figure)


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("post-hoc output is append-only; choose a new version")
    evidence = verify_frozen_evidence()
    payload = np.load(RAW_PATH, allow_pickle=False)
    raw = {key: payload[key] for key in payload.files}
    cache_payload = np.load(CACHE_PATH, allow_pickle=False)
    cache = SmartResponseCache(CACHE_PATH)

    unit_rows: list[dict[str, Any]] = []
    vectors_by_seed: dict[int, list[dict[str, np.ndarray]]] = {seed: [] for seed in SEEDS}
    for seed_index, seed in enumerate(SEEDS):
        for context in (0, 1):
            for unit in UNITS:
                row, vectors = analyze_unit(
                    raw, seed_index, seed, context, *unit, cache, cache_payload
                )
                unit_rows.append(row)
                vectors_by_seed[seed].append(vectors)

    seed_rows = aggregate_seed_rows(unit_rows)
    summary = summarize_seed_metrics(seed_rows)
    engagement = engagement_summary(raw)
    engaged = engaged_subset_diagnostics(vectors_by_seed)

    # Compare against the frozen metrics. Raw W arrays were archived as float32
    # whereas the original correlations used in-memory float64 snapshots. Do
    # not replace raw values post hoc: record any precision-induced mismatch.
    frozen_seed_rows = json.loads((FROZEN / "summary.json").read_text(encoding="utf-8"))[
        "conditions"
    ]["primary_part_t_smart"]["seeds"]
    parity = {}
    for frozen_key, posthoc_key in (
        ("pre_d_to_w", "pre_d_to_w"),
        ("pre_d_to_s", "pre_d_to_s"),
        ("post_d_to_w", "post_d_to_w"),
        ("post_d_to_s", "post_d_to_s"),
    ):
        period = frozen_key.split("_")[0]
        endpoint = "d_residual_to_delta_w" if frozen_key.endswith("to_w") else "d_residual_to_delta_s"
        reconstructed = np.asarray([
            np.mean([
                row[endpoint]
                for row in unit_rows
                if row["seed"] == seed and row["period"] == period
            ])
            for seed in SEEDS
        ])
        frozen_values = np.asarray([row[frozen_key] for row in frozen_seed_rows])
        max_error = float(np.max(np.abs(reconstructed - frozen_values)))
        errors = np.abs(reconstructed - frozen_values)
        parity[posthoc_key] = {
            "max_abs_seed_error": max_error,
            "seeds_with_abs_error_le_1e_6": int(np.sum(errors <= 1e-6)),
            "seeds_with_abs_error_gt_0_1": int(np.sum(errors > 0.1)),
            "interpretation": (
                "raw float32 reconstruction; frozen metrics used float64 in-memory snapshots"
            ),
        }

    fixed_zero = np.asarray([row["delta_w_zero_neurons"] for row in unit_rows], dtype=float)
    fixed_nonzero = 8.0 - fixed_zero
    sparsity = {
        "fixed_h_delta_w_zero_neuron_fraction": float(fixed_zero.sum() / (8 * len(fixed_zero))),
        "fixed_h_nonzero_neurons_median": float(np.median(fixed_nonzero)),
        "fixed_h_nonzero_neurons_q25_q75": [
            float(np.quantile(fixed_nonzero, 0.25)),
            float(np.quantile(fixed_nonzero, 0.75)),
        ],
    }

    OUTPUT.mkdir(parents=True)
    write_csv(OUTPUT / "per_unit.csv", unit_rows)
    write_csv(OUTPUT / "per_seed.csv", seed_rows)
    write_csv(OUTPUT / "engaged_subset_per_seed.csv", engaged["per_seed"])
    result = {
        "label": "POST HOC / FAILURE LOCALIZATION — not confirmatory evidence",
        "frozen_outcome_unchanged": "C_COMPOSITION_FAILS_LONGITUDINAL_CHAIN",
        "evidence_verification": evidence,
        "method": {
            "grain": "12 seeds; four fixed-h units per seed (pre/post remap × two contexts)",
            "early_late_windows": {
                "pre": {"early": [0, 40], "late": [60, 100]},
                "post": {"early": [120, 160], "late": [200, 240]},
            },
            "net_topdown_definition": (
                "mean[(g_td_peak*(E_exc-V_peak)+g_inh_peak*(E_inh-V_peak))/tau_m]"
            ),
            "net_topdown_limitation": (
                "peak conductances and V_peak are not time-aligned; this is an "
                "equation-derived current envelope, not an instantaneous/integrated current"
            ),
            "bootstrap": "5000 seed-level resamples",
            "subset_status": "engaged-cell analyses are diagnostic only",
        },
        "frozen_metric_parity": parity,
        "metrics": summary,
        "engagement": engagement,
        "fixed_h_sparsity": sparsity,
        "engaged_subset": engaged["summary"],
    }
    with (OUTPUT / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    save_figures(summary, engagement, OUTPUT / "figures")

    manifest = {
        str(path.relative_to(OUTPUT)): sha256(path)
        for path in sorted(OUTPUT.rglob("*"))
        if path.is_file() and path.name != "SHA256SUMS.json"
    }
    with (OUTPUT / "SHA256SUMS.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "raw_t_to_role": metric(summary, "raw_t_to_role"),
        "raw_t_to_delta_w": metric(summary, "raw_t_to_delta_w"),
        "net_to_delta_w": metric(summary, "net_topdown_peak_envelope_to_delta_w"),
        "delta_w_to_delta_s": metric(summary, "delta_w_to_delta_s"),
        "zero_delta_w_fraction": sparsity["fixed_h_delta_w_zero_neuron_fraction"],
    }, indent=2))


if __name__ == "__main__":
    main()
