from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np

from part_credit.exp003a.motif import MotifConfig, run_condition
from part_credit.exp003a.plasticity import (
    PlasticityConfig,
    equation5_update,
    equation6_post_signal,
)


def _cached_results() -> dict[str, dict[str, object]]:
    if not hasattr(_cached_results, "results"):
        cfg = MotifConfig(presentations=24, probe_presentations=4)
        _cached_results.results = {
            condition: run_condition(condition, cfg)
            for condition in ("matched", "topdown_ablated", "mismatch")
        }
    return _cached_results.results


def test_equation6_piecewise_values() -> None:
    cfg = PlasticityConfig()
    d_ratio = cfg.d_ratio
    ages = np.asarray([-1.0, 0.0, 0.05, 0.10, 12.60, 25.10])
    values = equation6_post_signal(ages, cfg)
    assert values[0] == 0.0
    assert np.isclose(values[1], d_ratio + 1.0)
    assert np.isclose(values[2], d_ratio + 0.5)
    assert np.isclose(values[3], d_ratio)
    assert np.isclose(values[4], d_ratio / 2.0)
    assert values[5] == 0.0


def test_matched_update_nonzero_and_competitor_much_smaller() -> None:
    matched = _cached_results()["matched"]
    center = int(matched["center"])
    competitor = int(matched["competitor"])
    changes = np.asarray(matched["weight_change"])
    assert changes[center] > 0.015
    assert abs(changes[competitor]) < 0.25 * abs(changes[center])


def test_mismatch_and_topdown_ablation_suppress_learning() -> None:
    results = _cached_results()
    matched_change = np.max(np.abs(results["matched"]["weight_change"]))
    for condition in ("mismatch", "topdown_ablated"):
        assert np.max(np.abs(results[condition]["weight_change"])) < 0.25 * matched_change


def test_weight_change_affects_future_response() -> None:
    matched = _cached_results()["matched"]
    center = int(matched["center"])
    before = np.asarray(matched["before_probe"]["spike_counts"])
    after = np.asarray(matched["after_probe"]["spike_counts"])
    assert after[center] > before[center]


def test_local_update_has_no_topdown_or_teaching_vector_argument() -> None:
    parameters = set(inspect.signature(equation5_update).parameters)
    forbidden = {"topdown", "reward", "error", "causal_role", "cell_label", "target"}
    assert parameters.isdisjoint(forbidden)
    source = Path(inspect.getsourcefile(equation5_update)).read_text(encoding="utf-8")
    for token in ("reward *", "error *", "hidden_causal", "causal_role"):
        assert token not in source


def test_topdown_can_change_weight_only_by_changing_local_spikes() -> None:
    cfg = PlasticityConfig()
    common = {
        "weight": cfg.w_initial,
        "pre_spike_times_ms": np.asarray([20.0]),
        "post_spike_times_ms": np.asarray([25.0]),
        "start_ms": 0.0,
        "stop_ms": 55.0,
        "cfg": cfg,
    }
    first, _ = equation5_update(**common)
    second, _ = equation5_update(**common)
    assert first == second


def test_topdown_is_modulatory_without_feedforward_drive() -> None:
    matched = _cached_results()["matched"]
    cfg = matched["config"]
    relative = np.mod(
        np.asarray(matched["lower_spike_times_ms"], dtype=float),
        float(cfg["cycle_ms"]),
    )
    assert not np.any(
        (relative >= float(cfg["topdown_at_ms"]))
        & (relative < float(cfg["feedforward_at_ms"]))
    )
