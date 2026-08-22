"""Brian2 response cache that preserves the fixed EXP003a local semantics.

The BCI cannot afford to construct a Brian2 network for every frame and condition.
This module evaluates a dense parameter grid in one vectorized Brian2 network.
Runtime lookup returns the actual grid cell's voltage, conductance, and spike
timing. The unchanged EXP003a Equation 5/6 function is then tabulated over every
observed spike pattern and interpolated only along the current weight coordinate.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from part_credit.exp003a.motif import MotifConfig
from part_credit.exp003a.plasticity import equation5_update


@dataclass(frozen=True)
class CacheGrid:
    motor: tuple[float, ...] = tuple(np.linspace(0.55, 1.10, 9))
    weight: tuple[float, ...] = tuple(np.linspace(0.50, 1.00, 21))
    topdown: tuple[float, ...] = tuple(np.linspace(0.0, 1.0, 9))
    global_topdown: tuple[float, ...] = tuple(np.linspace(0.0, 1.0, 6))
    reset: tuple[float, ...] = (0.0, 1.0)
    max_post_spikes: int = 4


def _normalizer(cfg: MotifConfig) -> float:
    rise = cfg.plasticity.tau_rise_ms
    fall = cfg.plasticity.tau_fall_ms
    peak_time = rise * fall / (fall - rise) * np.log(fall / rise)
    peak = np.exp(-peak_time / fall) - np.exp(-peak_time / rise)
    return float(1.0 / peak)


def build_cache(grid: CacheGrid | None = None) -> dict[str, Any]:
    """Evaluate every grid point in a single vectorized Brian2 motif."""

    import brian2 as b2

    cfg = MotifConfig(presentations=1)
    grid = grid or CacheGrid()
    axes = [
        np.asarray(grid.motor),
        np.asarray(grid.weight),
        np.asarray(grid.topdown),
        np.asarray(grid.global_topdown),
        np.asarray(grid.reset),
    ]
    mesh = np.meshgrid(*axes, indexing="ij")
    motor, weight, topdown, global_topdown, reset = [item.ravel() for item in mesh]
    n_cells = motor.size

    b2.start_scope()
    b2.prefs.codegen.target = "numpy"
    b2.defaultclock.dt = cfg.run_dt_ms * b2.ms
    namespace = {
        "tau_m": cfg.tau_membrane_ms * b2.ms,
        "tau_ff_rise": cfg.plasticity.tau_rise_ms * b2.ms,
        "tau_ff_fall": cfg.plasticity.tau_fall_ms * b2.ms,
        "tau_td": cfg.tau_topdown_ms * b2.ms,
        "tau_i": cfg.tau_inhibitory_ms * b2.ms,
        "tau_int": cfg.tau_interneuron_ms * b2.ms,
        "v_rest": cfg.v_rest_mv * b2.mV,
        "v_reset": cfg.v_reset_mv * b2.mV,
        "v_threshold": cfg.v_threshold_mv * b2.mV,
        "e_exc": cfg.e_excitatory_mv * b2.mV,
        "e_inh": cfg.e_inhibitory_mv * b2.mV,
        "ff_norm": _normalizer(cfg),
    }
    lower_eq = """
    dv/dt = (v_rest-v + g_ff*(e_exc-v) + g_td*(e_exc-v)
             + g_inh*(e_inh-v))/tau_m : volt (unless refractory)
    dg_ff_rise/dt = -g_ff_rise/tau_ff_rise : 1
    dg_ff_decay/dt = -g_ff_decay/tau_ff_fall : 1
    g_ff = ff_norm*(g_ff_decay-g_ff_rise) : 1
    dg_td/dt = -g_td/tau_td : 1
    dg_inh/dt = -g_inh/tau_i : 1
    v_peak : volt
    g_ff_peak : 1
    g_td_peak : 1
    g_inh_peak : 1
    """
    lower = b2.NeuronGroup(
        n_cells,
        lower_eq,
        threshold="v > v_threshold",
        reset="v = v_reset",
        refractory=cfg.refractory_ms * b2.ms,
        method="euler",
        namespace=namespace,
    )
    lower.v = namespace["v_rest"]
    lower.v_peak = namespace["v_rest"]
    lower.run_regularly(
        """
        v_peak = int(v > v_peak)*v + int(v <= v_peak)*v_peak
        g_ff_peak = int(g_ff > g_ff_peak)*g_ff + int(g_ff <= g_ff_peak)*g_ff_peak
        g_td_peak = int(g_td > g_td_peak)*g_td + int(g_td <= g_td_peak)*g_td_peak
        g_inh_peak = int(g_inh > g_inh_peak)*g_inh + int(g_inh <= g_inh_peak)*g_inh_peak
        """,
        dt=cfg.run_dt_ms * b2.ms,
    )

    indices = np.arange(n_cells)
    feedforward_source = b2.SpikeGeneratorGroup(
        n_cells, indices, np.full(n_cells, cfg.feedforward_at_ms) * b2.ms
    )
    feedforward = b2.Synapses(
        feedforward_source,
        lower,
        model="drive : 1",
        on_pre="""
        g_ff_rise_post += feedforward_gain*drive
        g_ff_decay_post += feedforward_gain*drive
        """,
        namespace={"feedforward_gain": cfg.feedforward_gain},
    )
    feedforward.connect(j="i")
    feedforward.drive = motor * weight

    topdown_source = b2.SpikeGeneratorGroup(
        n_cells, indices, np.full(n_cells, cfg.topdown_at_ms) * b2.ms
    )
    center = b2.Synapses(
        topdown_source,
        lower,
        model="profile : 1",
        on_pre="g_td_post += topdown_gain*profile",
        namespace={"topdown_gain": cfg.topdown_gain},
    )
    center.connect(j="i")
    center.profile = topdown

    interneuron_eq = """
    dv/dt = (v_rest-v + g_exc*(e_exc-v))/tau_int : volt (unless refractory)
    dg_exc/dt = -g_exc/tau_int : 1
    """
    surround = b2.NeuronGroup(
        n_cells,
        interneuron_eq,
        threshold="v > v_threshold",
        reset="v = v_reset",
        refractory=cfg.refractory_ms * b2.ms,
        method="euler",
        namespace=namespace,
    )
    surround.v = namespace["v_rest"]
    td_to_surround = b2.Synapses(
        topdown_source,
        surround,
        model="drive : 1",
        on_pre="g_exc_post += td_interneuron_gain*drive",
        namespace={"td_interneuron_gain": cfg.topdown_to_interneuron_gain},
    )
    td_to_surround.connect(j="i")
    td_to_surround.drive = global_topdown
    surround_to_lower = b2.Synapses(
        surround,
        lower,
        model="profile : 1",
        on_pre="g_inh_post += surround_gain*profile",
        namespace={"surround_gain": cfg.surround_gain},
    )
    surround_to_lower.connect(j="i")
    surround_to_lower.profile = 1.0 - topdown

    mismatch_source = b2.SpikeGeneratorGroup(
        n_cells, indices, np.full(n_cells, cfg.mismatch_at_ms) * b2.ms
    )
    reset_cells = b2.NeuronGroup(
        n_cells,
        interneuron_eq,
        threshold="v > v_threshold",
        reset="v = v_reset",
        refractory=cfg.refractory_ms * b2.ms,
        method="euler",
        namespace=namespace,
    )
    reset_cells.v = namespace["v_rest"]
    mismatch_to_reset = b2.Synapses(
        mismatch_source,
        reset_cells,
        model="active : 1",
        on_pre="g_exc_post += reset_interneuron_gain*active",
        namespace={"reset_interneuron_gain": cfg.reset_to_interneuron_gain},
    )
    mismatch_to_reset.connect(j="i")
    mismatch_to_reset.active = reset
    reset_to_lower = b2.Synapses(
        reset_cells,
        lower,
        on_pre="g_inh_post += reset_gain",
        namespace={"reset_gain": cfg.reset_gain},
    )
    reset_to_lower.connect(j="i")

    spikes = b2.SpikeMonitor(lower)
    network = b2.Network(
        lower,
        feedforward_source,
        feedforward,
        topdown_source,
        center,
        surround,
        td_to_surround,
        surround_to_lower,
        mismatch_source,
        reset_cells,
        mismatch_to_reset,
        reset_to_lower,
        spikes,
    )
    network.run(cfg.cycle_ms * b2.ms)

    spike_count = np.bincount(np.asarray(spikes.i), minlength=n_cells).astype(np.int16)
    post_times = np.full((n_cells, grid.max_post_spikes), np.nan, dtype=np.float32)
    for cell, spike_time in zip(np.asarray(spikes.i), np.asarray(spikes.t / b2.ms)):
        slot = int(np.sum(np.isfinite(post_times[cell])))
        if slot < grid.max_post_spikes:
            post_times[cell, slot] = spike_time

    # NaNs are not equal under NumPy's row comparison and would make every
    # no-spike row appear unique. A negative sentinel gives one deterministic
    # cache key for the identical no-spike history, then is restored to NaN.
    pattern_keys = np.nan_to_num(post_times, nan=-1.0)
    unique_keys, pattern_id = np.unique(pattern_keys, axis=0, return_inverse=True)
    unique_patterns = np.where(unique_keys < 0.0, np.nan, unique_keys)
    plasticity_delta = np.zeros((len(unique_patterns), len(grid.weight)))
    for pattern_index, pattern in enumerate(unique_patterns):
        posts = pattern[np.isfinite(pattern)].astype(float)
        for weight_index, initial_weight in enumerate(grid.weight):
            final_weight, _ = equation5_update(
                weight=float(initial_weight),
                pre_spike_times_ms=np.asarray([cfg.feedforward_at_ms]),
                post_spike_times_ms=posts,
                start_ms=0.0,
                stop_ms=cfg.cycle_ms,
                cfg=cfg.plasticity,
            )
            plasticity_delta[pattern_index, weight_index] = final_weight - initial_weight

    return {
        "motif_config": asdict(cfg),
        "grid": asdict(grid),
        "shape": np.asarray([len(axis) for axis in axes], dtype=np.int16),
        "axis_motor": axes[0].astype(np.float32),
        "axis_weight": axes[1].astype(np.float32),
        "axis_topdown": axes[2].astype(np.float32),
        "axis_global_topdown": axes[3].astype(np.float32),
        "axis_reset": axes[4].astype(np.float32),
        "v_peak_mv": np.asarray(lower.v_peak / b2.mV, dtype=np.float32),
        "g_ff_peak": np.asarray(lower.g_ff_peak, dtype=np.float32),
        "g_td_peak": np.asarray(lower.g_td_peak, dtype=np.float32),
        "g_inh_peak": np.asarray(lower.g_inh_peak, dtype=np.float32),
        "spike_count": spike_count,
        "post_times_ms": post_times,
        "pattern_id": pattern_id.astype(np.int32),
        "unique_post_patterns_ms": unique_patterns,
        "plasticity_delta": plasticity_delta.astype(np.float32),
    }


def save_cache(cache: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = np.asarray([repr({
        "motif_config": cache["motif_config"],
        "grid": cache["grid"],
    })])
    arrays = {
        key: value
        for key, value in cache.items()
        if isinstance(value, np.ndarray)
    }
    np.savez_compressed(path, metadata=metadata, **arrays)


class SmartResponseCache:
    """Nearest-grid Brian2 responses plus weight-interpolated canonical Eq. 5/6."""

    def __init__(self, path: Path):
        payload = np.load(path, allow_pickle=False)
        self.shape = tuple(int(value) for value in payload["shape"])
        self.v_peak_mv = payload["v_peak_mv"]
        self.g_ff_peak = payload["g_ff_peak"]
        self.g_td_peak = payload["g_td_peak"]
        self.g_inh_peak = payload["g_inh_peak"]
        self.spike_count = payload["spike_count"]
        self.post_times_ms = payload["post_times_ms"]
        self.pattern_id = payload["pattern_id"]
        self.plasticity_delta = payload["plasticity_delta"]
        self.axes = [
            payload["axis_motor"],
            payload["axis_weight"],
            payload["axis_topdown"],
            payload["axis_global_topdown"],
            payload["axis_reset"],
        ]
        self.weight_axis = self.axes[1]
        self.cfg = MotifConfig(presentations=1)

    @staticmethod
    def _nearest(axis: np.ndarray, values: np.ndarray) -> np.ndarray:
        return np.abs(axis[:, None] - values[None, :]).argmin(axis=0)

    def frame(
        self,
        *,
        motor: np.ndarray,
        weight: np.ndarray,
        topdown: np.ndarray,
        reset: bool,
        plastic: bool,
    ) -> dict[str, np.ndarray]:
        motor = np.asarray(motor, dtype=float)
        weight = np.asarray(weight, dtype=float)
        topdown = np.clip(np.asarray(topdown, dtype=float), 0.0, 1.0)
        global_topdown = np.full_like(topdown, float(np.max(topdown)))
        reset_values = np.full_like(topdown, float(reset))
        coordinates = [motor, weight, topdown, global_topdown, reset_values]
        indices = [self._nearest(axis, values) for axis, values in zip(self.axes, coordinates)]
        flat = np.ravel_multi_index(tuple(indices), self.shape)
        v_peak = self.v_peak_mv[flat].astype(float)
        posts = self.post_times_ms[flat].astype(float)
        patterns = self.pattern_id[flat]
        new_weight = weight.copy()
        if plastic:
            for neuron in range(len(weight)):
                delta = np.interp(
                    weight[neuron],
                    self.weight_axis,
                    self.plasticity_delta[patterns[neuron]],
                )
                new_weight[neuron] = np.clip(
                    weight[neuron] + delta,
                    self.cfg.plasticity.w_min,
                    self.cfg.plasticity.w_max,
                )
        voltage_range = self.cfg.v_threshold_mv - self.cfg.v_rest_mv
        soma = np.clip((v_peak - self.cfg.v_rest_mv) / voltage_range, 0.0, 1.0)
        first_latency = np.full(len(weight), np.nan)
        finite = np.isfinite(posts[:, 0])
        first_latency[finite] = posts[finite, 0] - self.cfg.feedforward_at_ms
        return {
            "soma": soma,
            "weight_after": new_weight,
            "delta_weight": new_weight - weight,
            "v_peak_mv": v_peak,
            "g_ff_peak": self.g_ff_peak[flat].astype(float),
            "g_td_peak": self.g_td_peak[flat].astype(float),
            "g_inh_peak": self.g_inh_peak[flat].astype(float),
            "spike_count": self.spike_count[flat].astype(int),
            "first_latency_ms": first_latency,
            "post_spike_times_ms": posts,
            "cache_flat_index": flat,
        }
