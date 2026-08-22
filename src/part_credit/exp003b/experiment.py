"""EXP003b paired-condition closed-loop BCI experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from part_credit.exp002.environment import BCIConfig, StepwiseCausalBCI

from .analysis import (
    bootstrap_mean_ci,
    initialization_audit,
    longitudinal_for_fixed_h,
    safe_corr,
    timing_role_alignment,
)
from .model import Condition, Exp003bController, LearnerConfig
from .spiking_cache import SmartResponseCache

PHASES = (
    "category_selection",
    "pre_action_expectation",
    "action_execution",
    "sensory_feedback",
    "outcome",
    "post_outcome",
)


@dataclass(frozen=True)
class Exp003bConfig:
    acquisition_episodes: int = 100
    evaluation_episodes: int = 20
    reacquisition_episodes: int = 120
    analysis_window: int = 40
    development_seeds: tuple[int, ...] = (41, 42, 43, 44)
    confirmatory_seeds: tuple[int, ...] = tuple(range(3100, 3112))
    learner: LearnerConfig = field(default_factory=LearnerConfig)
    environment: BCIConfig = field(default_factory=lambda: BCIConfig(
        n_neurons=8,
        action_frames=3,
        delay_steps=4,
        causal_strength=2.20,
        transition_noise=0.012,
        action_noise=0.0,
        success_error=0.25,
    ))

    @property
    def remap_at(self) -> int:
        return self.acquisition_episodes + self.evaluation_episodes

    @property
    def total_episodes(self) -> int:
        return (
            self.acquisition_episodes
            + 2 * self.evaluation_episodes
            + self.reacquisition_episodes
        )


CONDITIONS: dict[str, Condition] = {
    "frozen_no_learning": Condition(
        algorithm="bandit",
        learn_values=False,
        learn_topdown=False,
        express_topdown=False,
        smart_plasticity=False,
    ),
    "random_controller": Condition(
        algorithm="random",
        learn_values=False,
        learn_topdown=False,
        express_topdown=False,
        smart_plasticity=False,
    ),
    "contextual_bandit": Condition(
        algorithm="bandit",
        learn_topdown=False,
        express_topdown=False,
        smart_plasticity=False,
    ),
    "bandit_direct_copy_apical": Condition(
        algorithm="bandit",
        learn_topdown=False,
        direct_copy_apical=True,
        topdown_to_smart=False,
        smart_plasticity=False,
    ),
    "bandit_generic_hebb": Condition(
        algorithm="bandit",
        learn_topdown=False,
        direct_copy_apical=True,
        topdown_to_smart=False,
        smart_plasticity=False,
        generic_hebb=True,
    ),
    "part_selection_no_expectancy": Condition(
        learn_topdown=False,
        express_topdown=False,
        smart_plasticity=False,
    ),
    "part_learned_t_no_smart": Condition(smart_plasticity=False),
    "primary_part_t_smart": Condition(),
    "primary_no_structural_credit": Condition(structural_credit=False),
    "primary_no_working_memory": Condition(working_memory=False),
    "primary_no_motivated_reinforcement": Condition(
        learn_values=False, motivated_attention=False
    ),
    "primary_no_reset_search": Condition(reset_search=False),
    "primary_no_resonance_gate": Condition(resonance_gate=False),
    "primary_shuffled_topdown": Condition(shuffled_topdown=True),
    "primary_t_learning_disabled": Condition(learn_topdown=False),
    "primary_t_to_smart_blocked": Condition(topdown_to_smart=False),
    "primary_post_learning_apical_suppressed": Condition(
        suppress_expression_evaluation=True
    ),
    "corrected_motor_basis_outstar_probe": Condition(plastic_motor_basis=True),
    "explicit_vector_credit_positive_control": Condition(
        algorithm="bandit",
        learn_topdown=False,
        express_topdown=False,
        smart_plasticity=False,
        explicit_vector_credit=True,
    ),
}


def _seed_rngs(seed: int) -> tuple[np.random.Generator, ...]:
    return tuple(
        np.random.default_rng(child)
        for child in np.random.SeedSequence(seed).spawn(4)
    )


def _is_evaluation(episode: int, cfg: Exp003bConfig) -> bool:
    pre = cfg.acquisition_episodes <= episode < cfg.remap_at
    post_start = cfg.remap_at + cfg.reacquisition_episodes
    return pre or post_start <= episode < cfg.total_episodes


def _phase(episode: int, cfg: Exp003bConfig) -> str:
    if episode < cfg.acquisition_episodes:
        return "acquisition"
    if episode < cfg.remap_at:
        return "pre_remap_evaluation"
    if episode < cfg.remap_at + cfg.reacquisition_episodes:
        return "reacquisition"
    return "post_remap_evaluation"


def _probe_bank(
    cache: SmartResponseCache, controller: Exp003bController
) -> np.ndarray:
    rows = []
    zeros = np.zeros(controller.cfg.n_neurons)
    for hypothesis in range(controller.cfg.n_hypotheses):
        response = cache.frame(
            motor=controller.motor_basis[hypothesis],
            weight=controller.lower_weights[hypothesis],
            topdown=zeros,
            reset=False,
            plastic=False,
        )
        rows.append(response["soma"])
    return np.asarray(rows)


def _selected_pattern(
    records: list[dict[str, object]], field: str
) -> np.ndarray:
    if not records:
        raise ValueError("selected pattern requires records")
    return np.stack([np.asarray(row[field]) for row in records]).mean(axis=0)


def _rows(
    records: list[dict[str, object]],
    phase: str,
    context: int,
    *,
    first_episodes: int | None = None,
    last_episodes: int | None = None,
) -> list[dict[str, object]]:
    selected = [
        row for row in records
        if row["phase"] == phase and row["context"] == context
    ]
    frames = 3
    if first_episodes is not None:
        selected = selected[: first_episodes * frames // 2]
    if last_episodes is not None:
        selected = selected[-last_episodes * frames // 2 :]
    return selected


def _mean_reward(
    episode_rows: list[dict[str, object]], phase: str, *, first: int | None = None,
    last: int | None = None,
) -> float:
    selected = [row for row in episode_rows if row["phase"] == phase]
    if first is not None:
        selected = selected[:first]
    if last is not None:
        selected = selected[-last:]
    return float(np.mean([row["reward"] for row in selected])) if selected else 0.0


def _dendrite_phases(
    *,
    soma: np.ndarray,
    selected: dict[str, Any],
    response: dict[str, np.ndarray],
    explicit_vector: np.ndarray | None,
    error_improvement: float,
) -> np.ndarray:
    profile = np.asarray(selected["topdown_profile"], dtype=float)
    cfg = response
    peak_apical = 0.42 * profile
    pre_apical = peak_apical * np.exp(-4.0 / 8.0)
    feedback_apical = peak_apical * np.exp(-64.0 / 8.0)
    apical = np.stack([
        np.zeros_like(profile),
        pre_apical,
        np.asarray(cfg["g_td_peak"], dtype=float)
        if np.any(selected["circuit_topdown"]) else peak_apical,
        feedback_apical,
        np.zeros_like(profile),
        np.zeros_like(profile),
    ])
    if explicit_vector is not None:
        apical[3] += error_improvement * np.asarray(explicit_vector)
    base = 0.35 * soma + 0.20 * float(np.mean(soma))
    return base[None, :] + apical


def run_seed(
    seed: int,
    cfg: Exp003bConfig,
    condition: Condition,
    cache_path: Path,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    env_rng, learner_rng, audit_rng, _ = _seed_rngs(seed)
    environment = StepwiseCausalBCI(cfg.environment, env_rng)
    controller = Exp003bController(cfg.learner, condition, learner_rng)
    cache = SmartResponseCache(cache_path)
    initial_causal = environment.base_causal.copy()
    audits = {
        "motor": initialization_audit(
            controller.initial_motor_basis, initial_causal, audit_rng
        ),
        "topdown": initialization_audit(
            controller.initial_topdown, initial_causal, audit_rng
        ),
        "lower_weight": initialization_audit(
            controller.initial_lower_weights, initial_causal, audit_rng
        ),
        "index": initialization_audit(
            np.eye(cfg.learner.n_neurons), initial_causal, audit_rng
        ),
    }
    records: list[dict[str, object]] = []
    episode_rows: list[dict[str, object]] = []
    snapshots: dict[str, dict[str, np.ndarray]] = {
        "initial": {
            "weights": controller.lower_weights.copy(),
            "probe": _probe_bank(cache, controller),
        }
    }
    old_patterns: dict[int, np.ndarray] = {}

    total = cfg.total_episodes
    frames = cfg.environment.action_frames
    neurons = cfg.environment.n_neurons
    raw = {
        "soma": np.zeros((total, frames, neurons), dtype=np.float32),
        "dendrite_phases": np.zeros(
            (total, frames, len(PHASES), neurons), dtype=np.float32
        ),
        "topdown": np.zeros((total, frames, neurons), dtype=np.float32),
        "weight_before": np.zeros((total, frames, neurons), dtype=np.float32),
        "weight_after": np.zeros((total, frames, neurons), dtype=np.float32),
        "v_peak_mv": np.zeros((total, frames, neurons), dtype=np.float32),
        "g_ff_peak": np.zeros((total, frames, neurons), dtype=np.float32),
        "g_td_peak": np.zeros((total, frames, neurons), dtype=np.float32),
        "g_inh_peak": np.zeros((total, frames, neurons), dtype=np.float32),
        "spike_count": np.zeros((total, frames, neurons), dtype=np.int8),
        "first_latency_ms": np.full((total, frames, neurons), np.nan, dtype=np.float32),
        "counterfactual_no_t_spike_count": np.zeros(
            (total, frames, neurons), dtype=np.int8
        ),
        "counterfactual_no_t_latency_ms": np.full(
            (total, frames, neurons), np.nan, dtype=np.float32
        ),
        "hypothesis": np.zeros((total, frames), dtype=np.int16),
        "category": np.zeros((total, frames), dtype=np.int16),
        "resonant": np.zeros((total, frames), dtype=np.int8),
        "error_improvement": np.zeros((total, frames), dtype=np.float32),
        "causal": np.zeros((total, neurons), dtype=np.int8),
        "episode_scalar": np.zeros((total, 8), dtype=np.float32),
    }

    for episode in range(total):
        if episode == cfg.remap_at:
            pre_eval = [
                row for row in records if row["phase"] == "pre_remap_evaluation"
            ]
            for context in (0, 1):
                old_patterns[context] = _selected_pattern(
                    [row for row in pre_eval if row["context"] == context],
                    "raw_topdown",
                )
            environment.remap()

        context = episode % 2
        observation = environment.reset(context)
        evaluating = _is_evaluation(episode, cfg)
        phase = _phase(episode, cfg)
        controller.start_episode()
        training_position = (
            episode if episode < cfg.remap_at else episode - cfg.remap_at
        )
        denominator = max(cfg.acquisition_episodes, cfg.reacquisition_episodes) - 1
        progress = float(np.clip(training_position / denominator, 0.0, 1.0))

        for frame in range(frames):
            state_bin = environment.state_bin()
            selected = controller.select(
                observation,
                context=context,
                state_bin=state_bin,
                progress=progress,
                evaluating=evaluating,
            )
            hypothesis = int(selected["hypothesis"])
            weight_before = controller.lower_weights[hypothesis].copy()
            reset = bool(
                condition.resonance_gate and not bool(selected["resonant"])
            )
            response = cache.frame(
                motor=np.asarray(selected["motor"]),
                weight=weight_before,
                topdown=np.asarray(selected["circuit_topdown"]),
                reset=reset,
                plastic=condition.smart_plasticity and not evaluating,
            )
            counterfactual_no_t = cache.frame(
                motor=np.asarray(selected["motor"]),
                weight=weight_before,
                topdown=np.zeros(neurons),
                reset=reset,
                plastic=False,
            )
            if condition.smart_plasticity and not evaluating:
                controller.lower_weights[hypothesis] = response["weight_after"]
            soma = np.asarray(response["soma"])
            transition = environment.step(soma)
            observation = np.asarray(transition["observation"])
            explicit = (
                environment.active_causal().copy()
                if condition.explicit_vector_credit else None
            )
            dendrite = _dendrite_phases(
                soma=soma,
                selected=selected,
                response=response,
                explicit_vector=explicit,
                error_improvement=float(transition["error_improvement"]),
            )
            controller.record_frame(
                selected,
                soma=soma,
                weight_before=weight_before,
                weight_after=controller.lower_weights[hypothesis],
                context=context,
                state_bin=state_bin,
            )
            record = {
                "episode": episode,
                "frame": frame,
                "phase": phase,
                "context": context,
                "evaluating": evaluating,
                "hypothesis": hypothesis,
                "category": int(selected["category"]),
                "resonant": bool(selected["resonant"]),
                "soma": soma.copy(),
                "dendrite_phases": dendrite.copy(),
                "raw_topdown": np.asarray(selected["raw_topdown"]).copy(),
                "weight_before": weight_before,
                "weight_after": controller.lower_weights[hypothesis].copy(),
                "error_improvement": float(transition["error_improvement"]),
            }
            records.append(record)
            raw["soma"][episode, frame] = soma
            raw["dendrite_phases"][episode, frame] = dendrite
            raw["topdown"][episode, frame] = selected["raw_topdown"]
            raw["weight_before"][episode, frame] = weight_before
            raw["weight_after"][episode, frame] = controller.lower_weights[hypothesis]
            for key in (
                "v_peak_mv", "g_ff_peak", "g_td_peak", "g_inh_peak",
                "spike_count", "first_latency_ms",
            ):
                raw[key][episode, frame] = response[key]
            raw["counterfactual_no_t_spike_count"][episode, frame] = (
                counterfactual_no_t["spike_count"]
            )
            raw["counterfactual_no_t_latency_ms"][episode, frame] = (
                counterfactual_no_t["first_latency_ms"]
            )
            raw["hypothesis"][episode, frame] = hypothesis
            raw["category"][episode, frame] = int(selected["category"])
            raw["resonant"][episode, frame] = int(selected["resonant"])
            raw["error_improvement"][episode, frame] = transition["error_improvement"]

        outcome = environment.outcome()
        wm_strength = controller.delay(environment.distractors())
        if not evaluating:
            controller.learn_outcome(
                global_improvement=float(outcome["global_improvement"]),
                reward=float(outcome["reward"]),
                wm_strength=wm_strength,
                hidden_causal_positive_control=(
                    environment.active_causal().copy()
                    if condition.explicit_vector_credit else None
                ),
            )
        causal = environment.active_causal().copy()
        raw["causal"][episode] = causal
        raw["episode_scalar"][episode] = (
            episode,
            context,
            evaluating,
            outcome["reward"],
            outcome["global_improvement"],
            outcome["final_error"],
            wm_strength,
            len(controller.prototypes),
        )
        episode_rows.append({
            "episode": episode,
            "phase": phase,
            "context": context,
            "reward": float(outcome["reward"]),
            "global_improvement": float(outcome["global_improvement"]),
        })

        snapshot_points = {
            cfg.analysis_window - 1: "acquisition_early",
            cfg.acquisition_episodes - 1: "acquisition_late",
            cfg.remap_at + cfg.analysis_window - 1: "reacquisition_early",
            cfg.remap_at + cfg.reacquisition_episodes - 1: "reacquisition_late",
        }
        if episode in snapshot_points:
            snapshots[snapshot_points[episode]] = {
                "weights": controller.lower_weights.copy(),
                "probe": _probe_bank(cache, controller),
            }

    initial_role = initial_causal
    post_role = environment.base_causal.copy()
    context_metrics = []
    pre_patterns = []
    post_patterns = []
    pre_timing = []
    post_timing = []
    for context in (0, 1):
        role_pre = initial_role if context == 0 else -initial_role
        role_post = post_role if context == 0 else -post_role
        early_pre = _rows(
            records, "acquisition", context, first_episodes=cfg.analysis_window
        )
        late_pre = _rows(
            records, "acquisition", context, last_episodes=cfg.analysis_window
        )
        early_post = _rows(
            records, "reacquisition", context, first_episodes=cfg.analysis_window
        )
        late_post = _rows(
            records, "reacquisition", context, last_episodes=cfg.analysis_window
        )
        eval_pre = _rows(records, "pre_remap_evaluation", context)
        eval_post = _rows(records, "post_remap_evaluation", context)
        pre_pattern = _selected_pattern(eval_pre, "raw_topdown")
        post_pattern = _selected_pattern(eval_post, "raw_topdown")
        pre_patterns.append(pre_pattern)
        post_patterns.append(post_pattern)
        phase_index = 3 if condition.explicit_vector_credit else 1
        pre_long = longitudinal_for_fixed_h(
            early_records=early_pre,
            late_records=late_pre,
            early_probe=snapshots["acquisition_early"]["probe"],
            late_probe=snapshots["acquisition_late"]["probe"],
            early_weights=snapshots["acquisition_early"]["weights"],
            late_weights=snapshots["acquisition_late"]["weights"],
            phase_index=phase_index,
        )
        post_long = longitudinal_for_fixed_h(
            early_records=early_post,
            late_records=late_post,
            early_probe=snapshots["reacquisition_early"]["probe"],
            late_probe=snapshots["reacquisition_late"]["probe"],
            early_weights=snapshots["reacquisition_early"]["weights"],
            late_weights=snapshots["reacquisition_late"]["weights"],
            phase_index=phase_index,
        )
        pre_timing.append(timing_role_alignment(eval_pre, role_pre, len(PHASES)))
        post_timing.append(timing_role_alignment(eval_post, role_post, len(PHASES)))
        context_metrics.append({
            "pre_t_alignment": safe_corr(pre_pattern, role_pre),
            "post_t_alignment": safe_corr(post_pattern, role_post),
            "old_t_new_alignment": safe_corr(old_patterns[context], role_post),
            "pre_probe_alignment": safe_corr(
                snapshots["acquisition_late"]["probe"][pre_long["hypothesis"]],
                role_pre,
            ) if pre_long["hypothesis"] >= 0 else 0.0,
            "post_probe_alignment": safe_corr(
                snapshots["reacquisition_late"]["probe"][post_long["hypothesis"]],
                role_post,
            ) if post_long["hypothesis"] >= 0 else 0.0,
            "pre_d_to_w": pre_long["d_to_w"],
            "pre_d_to_s": pre_long["d_to_s"],
            "pre_w_to_s": pre_long["w_to_s"],
            "post_d_to_w": post_long["d_to_w"],
            "post_d_to_s": post_long["d_to_s"],
            "post_w_to_s": post_long["w_to_s"],
            "pre_fixed_h_events": pre_long["n_early"],
            "post_fixed_h_events": post_long["n_early"],
        })

    mean = lambda key: float(np.mean([row[key] for row in context_metrics]))
    metrics = {
        "seed": seed,
        "initialization_audits": audits,
        "acquisition_early_success": _mean_reward(
            episode_rows, "acquisition", first=cfg.analysis_window
        ),
        "acquisition_late_success": _mean_reward(
            episode_rows, "acquisition", last=cfg.analysis_window
        ),
        "pre_remap_evaluation_success": _mean_reward(
            episode_rows, "pre_remap_evaluation"
        ),
        "post_remap_early_success": _mean_reward(
            episode_rows, "reacquisition", first=cfg.analysis_window
        ),
        "post_remap_late_success": _mean_reward(
            episode_rows, "reacquisition", last=cfg.analysis_window
        ),
        "post_remap_evaluation_success": _mean_reward(
            episode_rows, "post_remap_evaluation"
        ),
        "pre_topdown_alignment": mean("pre_t_alignment"),
        "post_topdown_alignment": mean("post_t_alignment"),
        "old_topdown_new_alignment": mean("old_t_new_alignment"),
        "context_topdown_opposition": float(np.mean([
            -safe_corr(pre_patterns[0], pre_patterns[1]),
            -safe_corr(post_patterns[0], post_patterns[1]),
        ])),
        "pre_probe_role_alignment": mean("pre_probe_alignment"),
        "post_probe_role_alignment": mean("post_probe_alignment"),
        "pre_d_to_w": mean("pre_d_to_w"),
        "pre_d_to_s": mean("pre_d_to_s"),
        "pre_w_to_s": mean("pre_w_to_s"),
        "post_d_to_w": mean("post_d_to_w"),
        "post_d_to_s": mean("post_d_to_s"),
        "post_w_to_s": mean("post_w_to_s"),
        "pre_fixed_h_events": mean("pre_fixed_h_events"),
        "post_fixed_h_events": mean("post_fixed_h_events"),
        "timing_pre_role_alignment": np.mean(pre_timing, axis=0).tolist(),
        "timing_post_role_alignment": np.mean(post_timing, axis=0).tolist(),
        "weight_change_norm": float(np.linalg.norm(
            controller.lower_weights - controller.initial_lower_weights
        )),
        "topdown_change_norm": float(np.linalg.norm(
            controller.topdown - controller.initial_topdown
        )),
        "motor_basis_change_norm": float(np.linalg.norm(
            controller.motor_basis - controller.initial_motor_basis
        )),
        "resonance_rate": controller.resonance_events
        / max(1, controller.selection_events),
        "reset_per_selection": controller.total_resets
        / max(1, controller.selection_events),
        "category_recruitments": controller.category_recruitments,
    }
    training = raw["episode_scalar"][:, 2] == 0
    actual_spikes = raw["spike_count"][training]
    no_t_spikes = raw["counterfactual_no_t_spike_count"][training]
    metrics["topdown_created_spike_fraction"] = float(np.mean(
        (actual_spikes > 0) & (no_t_spikes == 0)
    ))
    actual_latency = raw["first_latency_ms"][training]
    no_t_latency = raw["counterfactual_no_t_latency_ms"][training]
    comparable = np.isfinite(actual_latency) & np.isfinite(no_t_latency)
    metrics["topdown_latency_advance_ms"] = (
        float(np.mean(no_t_latency[comparable] - actual_latency[comparable]))
        if np.any(comparable) else 0.0
    )
    return metrics, raw


SUMMARY_KEYS = (
    "acquisition_early_success",
    "acquisition_late_success",
    "pre_remap_evaluation_success",
    "post_remap_early_success",
    "post_remap_late_success",
    "post_remap_evaluation_success",
    "pre_topdown_alignment",
    "post_topdown_alignment",
    "old_topdown_new_alignment",
    "context_topdown_opposition",
    "pre_probe_role_alignment",
    "post_probe_role_alignment",
    "pre_d_to_w",
    "pre_d_to_s",
    "pre_w_to_s",
    "post_d_to_w",
    "post_d_to_s",
    "post_w_to_s",
    "pre_fixed_h_events",
    "post_fixed_h_events",
    "weight_change_norm",
    "topdown_change_norm",
    "motor_basis_change_norm",
    "resonance_rate",
    "reset_per_selection",
    "category_recruitments",
    "topdown_created_spike_fraction",
    "topdown_latency_advance_ms",
)


def run_condition(
    name: str,
    cfg: Exp003bConfig,
    seeds: tuple[int, ...],
    cache_path: Path,
) -> dict[str, Any]:
    seed_rows = []
    raw_rows: dict[str, list[np.ndarray]] = {}
    for seed in seeds:
        metrics, raw = run_seed(seed, cfg, CONDITIONS[name], cache_path)
        seed_rows.append(metrics)
        for key, value in raw.items():
            raw_rows.setdefault(key, []).append(value)
    summary = {
        key: float(np.mean([float(row[key]) for row in seed_rows]))
        for key in SUMMARY_KEYS
    }
    for key in ("pre_d_to_w", "pre_d_to_s", "post_d_to_w", "post_d_to_s"):
        values = np.asarray([row[key] for row in seed_rows])
        summary[f"{key}_ci95"] = list(
            bootstrap_mean_ci(values, np.random.default_rng(80303))
        )
    summary["timing_pre_role_alignment"] = np.mean(
        [row["timing_pre_role_alignment"] for row in seed_rows], axis=0
    ).tolist()
    summary["timing_post_role_alignment"] = np.mean(
        [row["timing_post_role_alignment"] for row in seed_rows], axis=0
    ).tolist()
    for bank in ("motor", "topdown", "lower_weight", "index"):
        for metric in (
            "mean_signed_correlation", "decoder_accuracy", "decoder_null_mean",
        ):
            summary[f"initial_{bank}_{metric}"] = float(np.mean([
                row["initialization_audits"][bank][metric] for row in seed_rows
            ]))
    return {
        "condition": name,
        "summary": summary,
        "seeds": seed_rows,
        "_raw": {key: np.stack(value) for key, value in raw_rows.items()},
    }


def run_suite(
    cfg: Exp003bConfig,
    seeds: tuple[int, ...],
    cache_path: Path,
    condition_names: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    names = condition_names or tuple(CONDITIONS)
    return {
        "config": asdict(cfg),
        "conditions": {
            name: run_condition(name, cfg, seeds, cache_path) for name in names
        },
    }
