"""Preregistered EXP002 suite and shared-data execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any

import numpy as np

from .analysis import (
    bootstrap_mean_ci,
    francioni_signal,
    initialization_audit,
    longitudinal_prediction,
    safe_corr,
    selected_pattern,
    timing_alignments,
)
from .environment import BCIConfig, StepwiseCausalBCI
from .model import Condition, Exp002Controller, LearnerConfig


@dataclass(frozen=True)
class Exp002Config:
    acquisition_episodes: int = 220
    evaluation_episodes: int = 40
    reacquisition_episodes: int = 220
    analysis_window: int = 50
    development_seeds: tuple[int, ...] = tuple(range(20, 28))
    confirmatory_seeds: tuple[int, ...] = tuple(range(2000, 2030))
    learner: LearnerConfig = field(default_factory=LearnerConfig)
    environment: BCIConfig = field(default_factory=BCIConfig)

    @property
    def remap_at(self) -> int:
        return self.acquisition_episodes + self.evaluation_episodes

    @property
    def total_episodes(self) -> int:
        return (
            self.acquisition_episodes + 2 * self.evaluation_episodes
            + self.reacquisition_episodes
        )


CONDITIONS: dict[str, Condition] = {
    "frozen_no_learning": Condition(plasticity=False),
    "random_controller": Condition(algorithm="random", topdown="none", plasticity=False),
    "contextual_bandit": Condition(algorithm="bandit", topdown="none"),
    "bandit_selected_pattern_copy": Condition(algorithm="bandit", topdown="copy"),
    "part_selection_no_expectancy": Condition(topdown="none"),
    "part_outstar_expectancy_primary": Condition(),
    "primary_no_structural_credit": Condition(structural_credit=False),
    "primary_no_working_memory": Condition(working_memory=False),
    "primary_no_motivated_attention": Condition(motivated_attention=False),
    "primary_no_reset_search": Condition(reset_search=False),
    "primary_no_resonance_gate": Condition(resonance_gate=False),
    "primary_shuffled_topdown": Condition(shuffled_topdown=True),
    "primary_apical_learning_suppressed": Condition(suppress_apical_learning=True),
    "primary_apical_expression_suppressed": Condition(suppress_apical_expression=True),
    "corrected_plastic_basis_outstar_probe": Condition(plastic_basis=True),
    "explicit_vector_error_positive_control": Condition(
        algorithm="bandit", topdown="vector", explicit_vector_error=True
    ),
}


SUMMARY_KEYS = (
    "acquisition_early_success",
    "acquisition_late_success",
    "pre_remap_evaluation_success",
    "post_remap_early_success",
    "post_remap_late_success",
    "post_remap_evaluation_success",
    "early_selected_topdown_alignment",
    "pre_remap_topdown_alignment",
    "old_topdown_new_mapping_alignment",
    "post_remap_topdown_alignment",
    "context_topdown_opposition",
    "pre_francioni_role_alignment",
    "post_francioni_role_alignment",
    "pre_longitudinal_prediction",
    "post_longitudinal_prediction",
    "resonance_rate",
    "reset_per_selection",
    "category_recruitments",
)


def _seed_rngs(seed: int) -> tuple[np.random.Generator, ...]:
    children = np.random.SeedSequence(seed).spawn(4)
    return tuple(np.random.default_rng(child) for child in children)


def _is_evaluation(episode: int, cfg: Exp002Config) -> bool:
    first = cfg.acquisition_episodes <= episode < cfg.remap_at
    second_start = cfg.remap_at + cfg.reacquisition_episodes
    second = second_start <= episode < cfg.total_episodes
    return first or second


def _phase_name(episode: int, cfg: Exp002Config) -> str:
    if episode < cfg.acquisition_episodes:
        return "acquisition"
    if episode < cfg.remap_at:
        return "pre_remap_evaluation"
    if episode < cfg.remap_at + cfg.reacquisition_episodes:
        return "reacquisition"
    return "post_remap_evaluation"


def _records_for(
    records: list[dict[str, object]],
    phase: str,
    context: int,
    *,
    first: int | None = None,
    last: int | None = None,
) -> list[dict[str, object]]:
    selected = [row for row in records if row["phase"] == phase and row["context"] == context]
    if first is not None:
        selected = selected[:first]
    if last is not None:
        selected = selected[-last:]
    return selected


def _mean_reward(rows: list[dict[str, object]]) -> float:
    return float(np.mean([float(row["reward"]) for row in rows])) if rows else 0.0


def _context_average(metric: list[float]) -> float:
    return float(np.mean(metric))


def run_seed(
    seed: int,
    cfg: Exp002Config,
    condition: Condition,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    env_rng, learner_rng, audit_rng, _ = _seed_rngs(seed)
    environment = StepwiseCausalBCI(cfg.environment, env_rng)
    learner = Exp002Controller(cfg.learner, condition, learner_rng)
    initial_causal = environment.base_causal.copy()
    motor_audit = initialization_audit(learner.initial_motor_basis, initial_causal, audit_rng)
    topdown_audit = initialization_audit(learner.initial_topdown, initial_causal, audit_rng)
    records: list[dict[str, object]] = []
    old_selected_patterns: dict[int, np.ndarray] = {}

    scalar_raw = np.zeros((cfg.total_episodes, 10), dtype=np.float32)
    soma_raw = np.zeros(
        (cfg.total_episodes, cfg.environment.action_frames, cfg.environment.n_neurons),
        dtype=np.float32,
    )
    dendrite_raw = np.zeros(
        (cfg.total_episodes, 5, cfg.environment.n_neurons), dtype=np.float32
    )
    topdown_raw = np.zeros(
        (cfg.total_episodes, cfg.environment.action_frames, cfg.environment.n_neurons),
        dtype=np.float32,
    )
    hypothesis_raw = np.zeros(
        (cfg.total_episodes, cfg.environment.action_frames), dtype=np.int16
    )
    causal_raw = np.zeros((cfg.total_episodes, cfg.environment.n_neurons), dtype=np.int8)

    for episode in range(cfg.total_episodes):
        if episode == cfg.remap_at:
            # Freeze the old learned expression before the hidden remapping.
            for context in (0, 1):
                prior = _records_for(records, "pre_remap_evaluation", context)
                old_selected_patterns[context] = selected_pattern(prior, "topdown_frames")
            environment.remap()

        context = episode % 2
        observation = environment.reset(context)
        evaluating = _is_evaluation(episode, cfg)
        phase = _phase_name(episode, cfg)
        learner.start_episode()
        soma_frames = []
        dendrite_frames = []
        topdown_frames = []
        motor_frames = []
        frame_improvements = []
        hypotheses = []
        categories = []
        resonances = []
        resets = []
        training_position = (
            episode if episode < cfg.remap_at else episode - cfg.remap_at
        )
        training_denominator = max(cfg.acquisition_episodes, cfg.reacquisition_episodes) - 1
        progress = float(np.clip(training_position / training_denominator, 0.0, 1.0))

        for _frame in range(cfg.environment.action_frames):
            selected = learner.select(
                observation,
                context=context,
                state_bin=environment.state_bin(),
                progress=progress,
                evaluating=evaluating,
            )
            transition = environment.step(np.asarray(selected["soma"]))
            observation = np.asarray(transition["observation"])
            soma_frames.append(np.asarray(selected["soma"]))
            phase_dendrite = learner.phase_dendrites(selected)
            if condition.explicit_vector_error:
                # Deliberately forbidden positive-control signal: a neuron-wise
                # causal direction scaled by current task-error improvement.
                # It is injected only after sensory feedback is available.
                vector_teaching = (
                    3.0 * float(transition["error_improvement"])
                    * environment.active_causal()
                )
                phase_dendrite[2:] += vector_teaching[None, :]
            dendrite_frames.append(phase_dendrite)
            topdown_frames.append(np.asarray(selected["topdown_pattern"]))
            motor_frames.append(np.asarray(selected["motor_pattern"]))
            frame_improvements.append(float(transition["error_improvement"]))
            hypotheses.append(int(selected["hypothesis"]))
            categories.append(int(selected["category"]))
            resonances.append(bool(selected["resonant"]))
            resets.append(int(selected["resets"]))

        outcome = environment.outcome()
        wm_strength = learner.delay(environment.distractors())
        learner.learn(
            global_improvement=float(outcome["global_improvement"]),
            reward=float(outcome["reward"]),
            wm_strength=wm_strength,
            active_causal_for_positive_control=(
                environment.active_causal().copy()
                if condition.explicit_vector_error else None
            ),
        )
        causal = environment.active_causal().copy()
        row = {
            "episode": episode,
            "phase": phase,
            "context": context,
            "evaluating": evaluating,
            "reward": float(outcome["reward"]),
            "global_improvement": float(outcome["global_improvement"]),
            "final_error": float(outcome["final_error"]),
            "soma_frames": np.asarray(soma_frames),
            "dendrite_frames": np.asarray(dendrite_frames),
            "topdown_frames": np.asarray(topdown_frames),
            "motor_frames": np.asarray(motor_frames),
            "frame_improvements": np.asarray(frame_improvements),
            "hypotheses": np.asarray(hypotheses),
            "categories": np.asarray(categories),
            "resonances": np.asarray(resonances),
            "resets": np.asarray(resets),
            "causal": causal,
        }
        records.append(row)
        scalar_raw[episode] = (
            episode,
            context,
            evaluating,
            float(outcome["reward"]),
            float(outcome["global_improvement"]),
            float(outcome["final_error"]),
            float(np.mean(resonances)),
            float(np.sum(resets)),
            hypotheses[-1],
            categories[-1],
        )
        soma_raw[episode] = row["soma_frames"]
        dendrite_raw[episode] = np.asarray(row["dendrite_frames"]).mean(axis=0)
        topdown_raw[episode] = row["topdown_frames"]
        hypothesis_raw[episode] = row["hypotheses"]
        causal_raw[episode] = causal

    acquisition = [row for row in records if row["phase"] == "acquisition"]
    reacquisition = [row for row in records if row["phase"] == "reacquisition"]
    pre_eval = [row for row in records if row["phase"] == "pre_remap_evaluation"]
    post_eval = [row for row in records if row["phase"] == "post_remap_evaluation"]
    window_per_context = max(4, cfg.analysis_window // 2)

    initial_alignments = []
    pre_alignments = []
    old_new_alignments = []
    post_alignments = []
    pre_francioni = []
    post_francioni = []
    pre_longitudinal = []
    post_longitudinal = []
    timing_pre = []
    timing_post = []
    context_patterns_pre = []
    context_patterns_post = []
    for context in (0, 1):
        initial_role = initial_causal if context == 0 else -initial_causal
        post_role = environment.base_causal if context == 0 else -environment.base_causal
        early_pre = _records_for(
            records, "acquisition", context, first=window_per_context
        )
        late_pre = _records_for(
            records, "acquisition", context, last=window_per_context
        )
        early_post = _records_for(
            records, "reacquisition", context, first=window_per_context
        )
        late_post = _records_for(
            records, "reacquisition", context, last=window_per_context
        )
        eval_pre_context = _records_for(records, "pre_remap_evaluation", context)
        eval_post_context = _records_for(records, "post_remap_evaluation", context)
        initial_pattern = selected_pattern(early_pre, "topdown_frames")
        pre_pattern = selected_pattern(eval_pre_context, "topdown_frames")
        post_pattern = selected_pattern(eval_post_context, "topdown_frames")
        initial_alignments.append(safe_corr(initial_pattern, initial_role))
        pre_alignments.append(safe_corr(pre_pattern, initial_role))
        old_new_alignments.append(safe_corr(old_selected_patterns[context], post_role))
        post_alignments.append(safe_corr(post_pattern, post_role))
        pre_francioni.append(francioni_signal(eval_pre_context, initial_role)["role_alignment"])
        post_francioni.append(francioni_signal(eval_post_context, post_role)["role_alignment"])
        pre_longitudinal.append(longitudinal_prediction(early_pre, late_pre, initial_role))
        post_longitudinal.append(longitudinal_prediction(early_post, late_post, post_role))
        timing_pre.append(timing_alignments(eval_pre_context, initial_role))
        timing_post.append(timing_alignments(eval_post_context, post_role))
        context_patterns_pre.append(pre_pattern)
        context_patterns_post.append(post_pattern)

    metrics = {
        "seed": seed,
        "motor_initialization_audit": motor_audit,
        "topdown_initialization_audit": topdown_audit,
        "acquisition_early_success": _mean_reward(acquisition[: cfg.analysis_window]),
        "acquisition_late_success": _mean_reward(acquisition[-cfg.analysis_window :]),
        "pre_remap_evaluation_success": _mean_reward(pre_eval),
        "post_remap_early_success": _mean_reward(reacquisition[: cfg.analysis_window]),
        "post_remap_late_success": _mean_reward(reacquisition[-cfg.analysis_window :]),
        "post_remap_evaluation_success": _mean_reward(post_eval),
        "early_selected_topdown_alignment": _context_average(initial_alignments),
        "pre_remap_topdown_alignment": _context_average(pre_alignments),
        "old_topdown_new_mapping_alignment": _context_average(old_new_alignments),
        "post_remap_topdown_alignment": _context_average(post_alignments),
        "context_topdown_opposition": _context_average([
            -safe_corr(context_patterns_pre[0], context_patterns_pre[1]),
            -safe_corr(context_patterns_post[0], context_patterns_post[1]),
        ]),
        "pre_francioni_role_alignment": _context_average(pre_francioni),
        "post_francioni_role_alignment": _context_average(post_francioni),
        "pre_longitudinal_prediction": _context_average(pre_longitudinal),
        "post_longitudinal_prediction": _context_average(post_longitudinal),
        "timing_pre_role_alignment": np.mean(timing_pre, axis=0).tolist(),
        "timing_post_role_alignment": np.mean(timing_post, axis=0).tolist(),
        "resonance_rate": learner.resonance_events / max(1, learner.selection_events),
        "reset_per_selection": learner.total_resets / max(1, learner.selection_events),
        "category_recruitments": learner.category_recruitments,
        "motor_basis_change_norm": float(np.linalg.norm(
            learner.motor_basis - learner.initial_motor_basis
        )),
        "topdown_change_norm": float(np.linalg.norm(
            learner.topdown - learner.initial_topdown
        )),
    }
    raw = {
        "scalar": scalar_raw,
        "soma_frames": soma_raw,
        "dendrite_phase_means": dendrite_raw,
        "topdown_frames": topdown_raw,
        "hypothesis_frames": hypothesis_raw,
        "causal": causal_raw,
    }
    return metrics, raw


def run_condition(
    name: str,
    cfg: Exp002Config,
    seeds: tuple[int, ...],
    *,
    condition: Condition | None = None,
) -> dict[str, Any]:
    active = condition or CONDITIONS[name]
    seed_rows = []
    raw_rows: dict[str, list[np.ndarray]] = {}
    for seed in seeds:
        metrics, raw = run_seed(seed, cfg, active)
        seed_rows.append(metrics)
        for key, value in raw.items():
            raw_rows.setdefault(key, []).append(value)
    summary = {
        key: float(np.mean([float(row[key]) for row in seed_rows]))
        for key in SUMMARY_KEYS
    }
    summary["timing_pre_role_alignment"] = np.mean(
        [row["timing_pre_role_alignment"] for row in seed_rows], axis=0
    ).tolist()
    summary["timing_post_role_alignment"] = np.mean(
        [row["timing_post_role_alignment"] for row in seed_rows], axis=0
    ).tolist()
    for key in ("pre_longitudinal_prediction", "post_longitudinal_prediction"):
        values = np.asarray([row[key] for row in seed_rows])
        ci = bootstrap_mean_ci(values, np.random.default_rng(88002))
        summary[f"{key}_ci95"] = list(ci)
    summary["initial_motor_mean_signed_correlation"] = float(np.mean([
        row["motor_initialization_audit"]["mean_signed_correlation"] for row in seed_rows
    ]))
    summary["initial_topdown_mean_signed_correlation"] = float(np.mean([
        row["topdown_initialization_audit"]["mean_signed_correlation"] for row in seed_rows
    ]))
    summary["initial_motor_decoder_accuracy"] = float(np.mean([
        row["motor_initialization_audit"]["decoder_accuracy"] for row in seed_rows
    ]))
    summary["initial_topdown_decoder_accuracy"] = float(np.mean([
        row["topdown_initialization_audit"]["decoder_accuracy"] for row in seed_rows
    ]))
    return {
        "condition": name,
        "summary": summary,
        "seeds": seed_rows,
        "_raw": {key: np.stack(values) for key, values in raw_rows.items()},
    }


def run_primary_suite(cfg: Exp002Config, phase: str) -> dict[str, Any]:
    if phase not in {"development", "confirmatory"}:
        raise ValueError("phase must be development or confirmatory")
    seeds = cfg.development_seeds if phase == "development" else cfg.confirmatory_seeds
    conditions = {name: run_condition(name, cfg, seeds) for name in CONDITIONS}
    return {"phase": phase, "config": asdict(cfg), "conditions": conditions}


def run_robustness(cfg: Exp002Config) -> dict[str, Any]:
    output = {}
    for parameter, values in {
        "vigilance": (0.78, 0.88, 0.96),
        "wm_persistence": (0.55, 0.80, 0.94),
        "reinforcement_lr": (0.10, 0.22, 0.36),
        "outstar_lr": (0.025, 0.075, 0.16),
        "n_hypotheses": (12, 48, 192),
    }.items():
        output[parameter] = {}
        for value in values:
            varied = replace(cfg, learner=replace(cfg.learner, **{parameter: value}))
            output[parameter][str(value)] = run_condition(
                "part_outstar_expectancy_primary", varied, cfg.development_seeds
            )
    return output
