"""Minimal Brian2 circuit for EXP003a SMART mechanism validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

import numpy as np

from .plasticity import PlasticityConfig, equation5_update

ConditionName = Literal["matched", "topdown_ablated", "shuffled", "mismatch"]


@dataclass(frozen=True)
class MotifConfig:
    """Small conductance-based LIF motif; numerical units are documented in EXP003a."""

    n_lower: int = 2
    presentations: int = 24
    cycle_ms: float = 80.0
    feedforward_at_ms: float = 20.0
    topdown_at_ms: float = 16.0
    mismatch_at_ms: float = 17.0
    run_dt_ms: float = 0.05
    plasticity: PlasticityConfig = field(default_factory=PlasticityConfig)
    tau_membrane_ms: float = 10.0
    tau_topdown_ms: float = 8.0
    tau_inhibitory_ms: float = 8.0
    tau_interneuron_ms: float = 5.0
    v_rest_mv: float = -65.0
    v_reset_mv: float = -65.0
    v_threshold_mv: float = -50.0
    e_excitatory_mv: float = 0.0
    e_inhibitory_mv: float = -80.0
    refractory_ms: float = 2.0
    feedforward_gain: float = 0.60
    topdown_gain: float = 0.42
    topdown_to_interneuron_gain: float = 3.5
    surround_gain: float = 1.35
    reset_to_interneuron_gain: float = 4.5
    reset_gain: float = 2.5
    probe_presentations: int = 8


def _spike_schedule(
    presentations: int, cycle_ms: float, offset_ms: float
) -> np.ndarray:
    return np.arange(presentations, dtype=float) * cycle_ms + offset_ms


def _feedforward_normalizer(cfg: MotifConfig) -> float:
    tau_rise = cfg.plasticity.tau_rise_ms
    tau_fall = cfg.plasticity.tau_fall_ms
    peak_time = tau_rise * tau_fall / (tau_fall - tau_rise) * np.log(
        tau_fall / tau_rise
    )
    peak = np.exp(-peak_time / tau_fall) - np.exp(-peak_time / tau_rise)
    return float(1.0 / peak)


def _build_training_network(
    condition: ConditionName, cfg: MotifConfig
) -> dict[str, object]:
    import brian2 as b2

    b2.start_scope()
    b2.prefs.codegen.target = "numpy"
    b2.defaultclock.dt = cfg.run_dt_ms * b2.ms
    namespace = {
        "tau_m": cfg.tau_membrane_ms * b2.ms,
        "tau_ff_rise": cfg.plasticity.tau_rise_ms * b2.ms,
        "tau_ff_fall": cfg.plasticity.tau_fall_ms * b2.ms,
        "tau_td": cfg.tau_topdown_ms * b2.ms,
        "tau_i": cfg.tau_inhibitory_ms * b2.ms,
        "v_rest": cfg.v_rest_mv * b2.mV,
        "v_reset": cfg.v_reset_mv * b2.mV,
        "v_threshold": cfg.v_threshold_mv * b2.mV,
        "e_exc": cfg.e_excitatory_mv * b2.mV,
        "e_inh": cfg.e_inhibitory_mv * b2.mV,
    }
    lower_equations = """
    dv/dt = (v_rest-v + g_ff*(e_exc-v) + g_td*(e_exc-v)
             + g_inh*(e_inh-v))/tau_m : volt (unless refractory)
    dg_ff_rise/dt = -g_ff_rise/tau_ff_rise : 1
    dg_ff_decay/dt = -g_ff_decay/tau_ff_fall : 1
    g_ff = ff_norm*(g_ff_decay-g_ff_rise) : 1
    dg_td/dt = -g_td/tau_td : 1
    dg_inh/dt = -g_inh/tau_i : 1
    """
    lower = b2.NeuronGroup(
        cfg.n_lower,
        lower_equations,
        threshold="v > v_threshold",
        reset="v = v_reset",
        refractory=cfg.refractory_ms * b2.ms,
        method="euler",
        namespace=dict(namespace, ff_norm=_feedforward_normalizer(cfg)),
        name="lower_cells",
    )
    lower.v = namespace["v_rest"]

    pre_times = _spike_schedule(cfg.presentations, cfg.cycle_ms, cfg.feedforward_at_ms)
    pre = b2.SpikeGeneratorGroup(
        cfg.n_lower,
        np.tile(np.arange(cfg.n_lower), cfg.presentations),
        np.repeat(pre_times, cfg.n_lower) * b2.ms,
        name="feedforward_inputs",
    )
    feedforward = b2.Synapses(
        pre,
        lower,
        model="w : 1",
        on_pre="""
        g_ff_rise_post += feedforward_gain*w
        g_ff_decay_post += feedforward_gain*w
        """,
        namespace={"feedforward_gain": cfg.feedforward_gain},
        name="plastic_feedforward",
    )
    feedforward.connect(j="i")
    feedforward.w = cfg.plasticity.w_initial

    td_times = (
        _spike_schedule(cfg.presentations, cfg.cycle_ms, cfg.topdown_at_ms)
        if condition != "topdown_ablated"
        else np.asarray([], dtype=float)
    )
    topdown = b2.SpikeGeneratorGroup(
        1,
        np.zeros(td_times.size, dtype=int),
        td_times * b2.ms,
        name="topdown_expectation",
    )
    center = 1 if condition == "shuffled" else 0
    competitor = 1 - center
    td_center = b2.Synapses(
        topdown,
        lower,
        on_pre="g_td_post += topdown_gain",
        namespace={"topdown_gain": cfg.topdown_gain},
        name="topdown_on_center",
    )
    td_center.connect(i=0, j=center)

    interneuron_equations = """
    dv/dt = (v_rest-v + g_exc*(e_exc-v))/tau_int : volt (unless refractory)
    dg_exc/dt = -g_exc/tau_int : 1
    """
    int_namespace = dict(namespace, tau_int=cfg.tau_interneuron_ms * b2.ms)
    surround_interneuron = b2.NeuronGroup(
        1,
        interneuron_equations,
        threshold="v > v_threshold",
        reset="v = v_reset",
        refractory=cfg.refractory_ms * b2.ms,
        method="euler",
        namespace=int_namespace,
        name="surround_interneuron",
    )
    surround_interneuron.v = namespace["v_rest"]
    td_to_surround = b2.Synapses(
        topdown,
        surround_interneuron,
        on_pre="g_exc_post += td_interneuron_gain",
        namespace={"td_interneuron_gain": cfg.topdown_to_interneuron_gain},
        name="topdown_to_surround",
    )
    td_to_surround.connect()
    surround_to_lower = b2.Synapses(
        surround_interneuron,
        lower,
        on_pre="g_inh_post += surround_gain",
        namespace={"surround_gain": cfg.surround_gain},
        name="surround_to_competitor",
    )
    surround_to_lower.connect(i=0, j=competitor)

    mismatch_times = (
        _spike_schedule(cfg.presentations, cfg.cycle_ms, cfg.mismatch_at_ms)
        if condition == "mismatch"
        else np.asarray([], dtype=float)
    )
    mismatch_source = b2.SpikeGeneratorGroup(
        1,
        np.zeros(mismatch_times.size, dtype=int),
        mismatch_times * b2.ms,
        name="mismatch_reset_source",
    )
    reset_interneuron = b2.NeuronGroup(
        1,
        interneuron_equations,
        threshold="v > v_threshold",
        reset="v = v_reset",
        refractory=cfg.refractory_ms * b2.ms,
        method="euler",
        namespace=int_namespace,
        name="reset_interneuron",
    )
    reset_interneuron.v = namespace["v_rest"]
    mismatch_to_reset = b2.Synapses(
        mismatch_source,
        reset_interneuron,
        on_pre="g_exc_post += reset_interneuron_gain",
        namespace={"reset_interneuron_gain": cfg.reset_to_interneuron_gain},
        name="mismatch_to_reset",
    )
    mismatch_to_reset.connect()
    reset_to_lower = b2.Synapses(
        reset_interneuron,
        lower,
        on_pre="g_inh_post += reset_gain",
        namespace={"reset_gain": cfg.reset_gain},
        name="reset_to_all_lower",
    )
    reset_to_lower.connect()

    lower_spikes = b2.SpikeMonitor(lower, name="lower_spike_monitor")
    pre_spikes = b2.SpikeMonitor(pre, name="pre_spike_monitor")
    inhibitory_spikes = b2.SpikeMonitor(
        surround_interneuron, name="surround_spike_monitor"
    )
    reset_spikes = b2.SpikeMonitor(reset_interneuron, name="reset_spike_monitor")
    voltage = b2.StateMonitor(
        lower, ("v", "g_ff", "g_td", "g_inh"), record=True, name="lower_state_monitor"
    )
    network = b2.Network(
        lower,
        pre,
        feedforward,
        topdown,
        td_center,
        surround_interneuron,
        td_to_surround,
        surround_to_lower,
        mismatch_source,
        reset_interneuron,
        mismatch_to_reset,
        reset_to_lower,
        lower_spikes,
        pre_spikes,
        inhibitory_spikes,
        reset_spikes,
        voltage,
    )
    return {
        "network": network,
        "feedforward": feedforward,
        "lower_spikes": lower_spikes,
        "pre_spikes": pre_spikes,
        "inhibitory_spikes": inhibitory_spikes,
        "reset_spikes": reset_spikes,
        "voltage": voltage,
        "center": center,
        "competitor": competitor,
    }


def _latencies_for_cycle(
    spike_indices: np.ndarray,
    spike_times_ms: np.ndarray,
    cycle_start_ms: float,
    pre_time_ms: float,
    n_lower: int,
) -> np.ndarray:
    latencies = np.full(n_lower, np.nan)
    for neuron in range(n_lower):
        candidates = spike_times_ms[
            (spike_indices == neuron)
            & (spike_times_ms >= pre_time_ms)
            & (spike_times_ms < cycle_start_ms + 50.0)
        ]
        if candidates.size:
            latencies[neuron] = float(candidates[0] - pre_time_ms)
    return latencies


def run_probe(weights: np.ndarray, cfg: MotifConfig) -> dict[str, np.ndarray]:
    """Learning-off feedforward probe; identical schedule for pre/post comparisons."""

    import brian2 as b2

    b2.start_scope()
    b2.prefs.codegen.target = "numpy"
    b2.defaultclock.dt = cfg.run_dt_ms * b2.ms
    namespace = {
        "tau_m": cfg.tau_membrane_ms * b2.ms,
        "tau_ff_rise": cfg.plasticity.tau_rise_ms * b2.ms,
        "tau_ff_fall": cfg.plasticity.tau_fall_ms * b2.ms,
        "v_rest": cfg.v_rest_mv * b2.mV,
        "v_reset": cfg.v_reset_mv * b2.mV,
        "v_threshold": cfg.v_threshold_mv * b2.mV,
        "e_exc": cfg.e_excitatory_mv * b2.mV,
    }
    equations = """
    dv/dt = (v_rest-v + g_ff*(e_exc-v))/tau_m : volt (unless refractory)
    dg_ff_rise/dt = -g_ff_rise/tau_ff_rise : 1
    dg_ff_decay/dt = -g_ff_decay/tau_ff_fall : 1
    g_ff = ff_norm*(g_ff_decay-g_ff_rise) : 1
    """
    lower = b2.NeuronGroup(
        cfg.n_lower,
        equations,
        threshold="v > v_threshold",
        reset="v = v_reset",
        refractory=cfg.refractory_ms * b2.ms,
        method="euler",
        namespace=dict(namespace, ff_norm=_feedforward_normalizer(cfg)),
    )
    lower.v = namespace["v_rest"]
    times = _spike_schedule(
        cfg.probe_presentations, cfg.cycle_ms, cfg.feedforward_at_ms
    )
    pre = b2.SpikeGeneratorGroup(
        cfg.n_lower,
        np.tile(np.arange(cfg.n_lower), cfg.probe_presentations),
        np.repeat(times, cfg.n_lower) * b2.ms,
    )
    synapses = b2.Synapses(
        pre,
        lower,
        model="w : 1",
        on_pre="""
        g_ff_rise_post += feedforward_gain*w
        g_ff_decay_post += feedforward_gain*w
        """,
        namespace={"feedforward_gain": cfg.feedforward_gain},
    )
    synapses.connect(j="i")
    synapses.w = np.asarray(weights)
    spikes = b2.SpikeMonitor(lower)
    voltage = b2.StateMonitor(lower, "v", record=True)
    network = b2.Network(lower, pre, synapses, spikes, voltage)
    network.run(cfg.probe_presentations * cfg.cycle_ms * b2.ms)
    spike_indices = np.asarray(spikes.i, dtype=int)
    spike_times_ms = np.asarray(spikes.t / b2.ms, dtype=float)
    counts = np.bincount(spike_indices, minlength=cfg.n_lower)
    latencies = []
    for presentation, pre_time in enumerate(times):
        latencies.append(
            _latencies_for_cycle(
                spike_indices,
                spike_times_ms,
                presentation * cfg.cycle_ms,
                pre_time,
                cfg.n_lower,
            )
        )
    latency_array = np.asarray(latencies)
    finite = np.isfinite(latency_array)
    mean_latency = np.divide(
        np.nansum(latency_array, axis=0),
        finite.sum(axis=0),
        out=np.full(cfg.n_lower, np.nan),
        where=finite.sum(axis=0) > 0,
    )
    return {
        "spike_indices": spike_indices,
        "spike_times_ms": spike_times_ms,
        "spike_counts": counts,
        "mean_latency_ms": mean_latency,
        "voltage_time_ms": np.asarray(voltage.t / b2.ms, dtype=float),
        "voltage_mv": np.asarray(voltage.v / b2.mV, dtype=float),
    }


def run_condition(condition: ConditionName, cfg: MotifConfig | None = None) -> dict[str, object]:
    """Run one mechanistic condition and freeze learning before future probes."""

    import brian2 as b2

    if cfg is None:
        cfg = MotifConfig()
    if condition not in {"matched", "topdown_ablated", "shuffled", "mismatch"}:
        raise ValueError(f"unknown condition: {condition}")
    built = _build_training_network(condition, cfg)
    network = built["network"]
    feedforward = built["feedforward"]
    lower_spikes = built["lower_spikes"]
    weights = np.full(cfg.n_lower, cfg.plasticity.w_initial, dtype=float)
    initial_weights = weights.copy()
    presentation_weights = [weights.copy()]
    presentation_latencies = []
    presentation_updates = []

    for presentation in range(cfg.presentations):
        cycle_start = presentation * cfg.cycle_ms
        cycle_stop = cycle_start + cfg.cycle_ms
        network.run(cfg.cycle_ms * b2.ms)
        spike_indices = np.asarray(lower_spikes.i, dtype=int)
        spike_times_ms = np.asarray(lower_spikes.t / b2.ms, dtype=float)
        pre_time = cycle_start + cfg.feedforward_at_ms
        latencies = _latencies_for_cycle(
            spike_indices,
            spike_times_ms,
            cycle_start,
            pre_time,
            cfg.n_lower,
        )
        presentation_latencies.append(latencies)
        updates = np.zeros(cfg.n_lower)
        for neuron in range(cfg.n_lower):
            posts = spike_times_ms[
                (spike_indices == neuron)
                & (spike_times_ms >= cycle_start)
                & (spike_times_ms < cycle_stop)
            ]
            final_weight, _ = equation5_update(
                weight=weights[neuron],
                pre_spike_times_ms=np.asarray([pre_time]),
                post_spike_times_ms=posts,
                start_ms=cycle_start,
                stop_ms=cycle_stop,
                cfg=cfg.plasticity,
            )
            updates[neuron] = final_weight - weights[neuron]
            weights[neuron] = final_weight
        feedforward.w = weights
        presentation_updates.append(updates)
        presentation_weights.append(weights.copy())

    before_probe = run_probe(initial_weights, cfg)
    after_probe = run_probe(weights, cfg)
    voltage = built["voltage"]
    spike_indices = np.asarray(lower_spikes.i, dtype=int)
    spike_times_ms = np.asarray(lower_spikes.t / b2.ms, dtype=float)
    latency_array = np.asarray(presentation_latencies)
    window_occupancy = np.mean(
        np.isfinite(latency_array)
        & (latency_array >= 0.0)
        & (latency_array <= cfg.plasticity.timing_recovery_ms),
        axis=0,
    )
    return {
        "condition": condition,
        "config": asdict(cfg),
        "center": int(built["center"]),
        "competitor": int(built["competitor"]),
        "initial_weights": initial_weights,
        "final_weights": weights,
        "weight_change": weights - initial_weights,
        "presentation_weights": np.asarray(presentation_weights),
        "presentation_updates": np.asarray(presentation_updates),
        "presentation_latencies_ms": latency_array,
        "stdp_window_occupancy": window_occupancy,
        "lower_spike_indices": spike_indices,
        "lower_spike_times_ms": spike_times_ms,
        "inhibitory_spike_times_ms": np.asarray(
            built["inhibitory_spikes"].t / b2.ms, dtype=float
        ),
        "reset_spike_times_ms": np.asarray(
            built["reset_spikes"].t / b2.ms, dtype=float
        ),
        "voltage_time_ms": np.asarray(voltage.t / b2.ms, dtype=float),
        "voltage_mv": np.asarray(voltage.v / b2.mV, dtype=float),
        "g_ff": np.asarray(voltage.g_ff, dtype=float),
        "g_td": np.asarray(voltage.g_td, dtype=float),
        "g_inh": np.asarray(voltage.g_inh, dtype=float),
        "before_probe": before_probe,
        "after_probe": after_probe,
    }
