"""SMART-derived reduced implementation of Grossberg & Versace Eqs. 5/6.

The original SMART model uses multi-compartment Hodgkin--Huxley neurons. EXP003a
retains the local bounded learning law and the exact piecewise timing signal, but
represents the postsynaptic voltage term by a normalized post-spike voltage proxy.
It is therefore deliberately named SMART-derived reduced STDP.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PlasticityConfig:
    """Parameters of the reduced local SMART synapse, with time in milliseconds."""

    dt_ms: float = 0.01
    tau_rise_ms: float = 0.5
    tau_fall_ms: float = 30.0
    learning_rate_per_ms: float = 0.02
    w_min: float = 0.05
    w_max: float = 1.00
    w_baseline: float = 0.50
    w_initial: float = 0.60
    timing_transition_ms: float = 0.10
    timing_recovery_ms: float = 25.0

    @property
    def d_ratio(self) -> float:
        """Equation 6's D=(w_min-w0)/(w_min-w_max), constrained to (0, 1)."""

        return (self.w_min - self.w_baseline) / (self.w_min - self.w_max)


def equation6_post_signal(age_ms: np.ndarray, cfg: PlasticityConfig) -> np.ndarray:
    """Equation 6 as a local function of time since the last postsynaptic spike.

    At the spike, the signal is D+1. It linearly transitions to D during the
    first 0.1 ms, then linearly returns from D to zero over the next 25 ms.
    Negative ages and ages at/after 25.1 ms are zero.
    """

    age = np.asarray(age_ms, dtype=float)
    output = np.zeros_like(age)
    d_ratio = cfg.d_ratio
    transition = cfg.timing_transition_ms
    recovery = cfg.timing_recovery_ms
    first = (age >= 0.0) & (age < transition)
    output[first] = d_ratio + 1.0 - age[first] / transition
    second = (age >= transition) & (age < transition + recovery)
    output[second] = d_ratio * (
        1.0 - (age[second] - transition) / recovery
    )
    return output


def normalized_presynaptic_conductance(
    time_ms: np.ndarray,
    pre_spike_times_ms: np.ndarray,
    cfg: PlasticityConfig,
) -> np.ndarray:
    """Equation 3 dual-exponential conductance, normalized to a peak of one."""

    time = np.asarray(time_ms, dtype=float)
    spikes = np.asarray(pre_spike_times_ms, dtype=float)
    if spikes.size == 0:
        return np.zeros_like(time)
    tau_rise = cfg.tau_rise_ms
    tau_fall = cfg.tau_fall_ms
    peak_time = tau_rise * tau_fall / (tau_fall - tau_rise) * np.log(
        tau_fall / tau_rise
    )
    peak = np.exp(-peak_time / tau_fall) - np.exp(-peak_time / tau_rise)
    conductance = np.zeros_like(time)
    for spike_time in spikes:
        age = time - spike_time
        active = age >= 0.0
        conductance[active] += (
            np.exp(-age[active] / tau_fall) - np.exp(-age[active] / tau_rise)
        ) / peak
    return conductance


def local_post_signal(
    time_ms: np.ndarray,
    post_spike_times_ms: np.ndarray,
    cfg: PlasticityConfig,
) -> np.ndarray:
    """Equation 6 signal for the most recent postsynaptic spike at every time."""

    time = np.asarray(time_ms, dtype=float)
    spikes = np.sort(np.asarray(post_spike_times_ms, dtype=float))
    if spikes.size == 0:
        return np.zeros_like(time)
    indices = np.searchsorted(spikes, time, side="right") - 1
    valid = indices >= 0
    age = np.full_like(time, -1.0)
    age[valid] = time[valid] - spikes[indices[valid]]
    return equation6_post_signal(age, cfg)


def equation5_update(
    *,
    weight: float,
    pre_spike_times_ms: np.ndarray,
    post_spike_times_ms: np.ndarray,
    start_ms: float,
    stop_ms: float,
    cfg: PlasticityConfig,
) -> tuple[float, dict[str, np.ndarray]]:
    """Numerically integrate the reduced Equation 5 using only synapse-local state.

    Exact retained structure::

        dw/dt = lambda f_G [g_pre f_N (w_max-w_min) + w0-w]

    Equation 6 supplies ``f_N``. For SMART's postsynaptic gating
    ``f_G(V_k,g_jk)=V_k^2``, the reduced normalized voltage/activity proxy is
    Equation 6's local post-spike signal, hence ``f_G=f_N**2``. No top-down,
    cell identity, reward, error, or causal-role variable enters this function.
    """

    if stop_ms <= start_ms:
        raise ValueError("stop_ms must be after start_ms")
    time = np.arange(start_ms, stop_ms, cfg.dt_ms, dtype=float)
    pre_conductance = normalized_presynaptic_conductance(
        time, pre_spike_times_ms, cfg
    )
    f_n = local_post_signal(time, post_spike_times_ms, cfg)
    f_g = f_n**2
    weights = np.empty_like(time)
    current = float(weight)
    weight_range = cfg.w_max - cfg.w_min
    derivatives = np.empty_like(time)
    for index in range(time.size):
        derivative = cfg.learning_rate_per_ms * f_g[index] * (
            pre_conductance[index] * f_n[index] * weight_range
            + cfg.w_baseline
            - current
        )
        current = float(np.clip(current + cfg.dt_ms * derivative, cfg.w_min, cfg.w_max))
        weights[index] = current
        derivatives[index] = derivative
    return current, {
        "time_ms": time,
        "pre_conductance": pre_conductance,
        "f_n": f_n,
        "f_g": f_g,
        "dw_dt_per_ms": derivatives,
        "weight_trace": weights,
    }


def timing_curve(
    offsets_ms: np.ndarray, cfg: PlasticityConfig
) -> np.ndarray:
    """Pair protocol: offset is postsynaptic time minus presynaptic time."""

    offsets = np.asarray(offsets_ms, dtype=float)
    changes = np.zeros_like(offsets)
    pre_time = 35.0
    for index, offset in enumerate(offsets):
        final, _ = equation5_update(
            weight=cfg.w_initial,
            pre_spike_times_ms=np.asarray([pre_time]),
            post_spike_times_ms=np.asarray([pre_time + offset]),
            start_ms=0.0,
            stop_ms=90.0,
            cfg=cfg,
        )
        changes[index] = final - cfg.w_initial
    return changes
