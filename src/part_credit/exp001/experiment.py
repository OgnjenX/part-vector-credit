"""EXP001 conditions, held-out protocol, sweeps, and outcome classification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any

import numpy as np

from .analysis import dendritic_metrics, initialization_audit, longitudinal_prediction
from .environment import BCIConfig, CausalBCI
from .model import Condition, HypothesisLearner, LearnerConfig


@dataclass(frozen=True)
class Exp001Config:
    trials: int = 1000
    remap_fraction: float = 0.60
    evaluation_window: int = 120
    development_seeds: tuple[int, ...] = tuple(range(8))
    confirmatory_seeds: tuple[int, ...] = tuple(range(1000, 1030))
    learner: LearnerConfig = field(default_factory=LearnerConfig)
    environment: BCIConfig = field(default_factory=BCIConfig)


CONDITIONS: dict[str, Condition] = {
    "frozen_zero_plasticity": Condition(plasticity=False),
    "random_policy_feedback": Condition(plasticity=False, random_policy=True),
    "grossberg_inspired_full": Condition(),
    "no_structural_credit": Condition(structural_credit=False),
    "no_working_memory": Condition(working_memory=False),
    "no_motivated_attention": Condition(motivated_attention=False),
    "no_now_print_gating": Condition(now_print=False),
    "no_reset_search": Condition(reset_search=False),
    "no_match_resonance_gating": Condition(resonance_gate=False),
    "shuffled_top_down_feedback": Condition(shuffled_feedback=True),
    "preexisting_random_basis_only": Condition(),
    "plastic_basis_engineering_probe": Condition(plastic_basis=True),
    "apical_pathway_suppressed": Condition(apical_suppression=True),
    "explicit_vector_error_positive_control": Condition(explicit_vector_error=True),
}


def _seed_rngs(seed: int) -> tuple[np.random.Generator, np.random.Generator, np.random.Generator]:
    environment_seed, learner_seed, audit_seed = np.random.SeedSequence(seed).spawn(3)
    return (
        np.random.default_rng(environment_seed),
        np.random.default_rng(learner_seed),
        np.random.default_rng(audit_seed),
    )


def _mean(rows: list[dict[str, object]], key: str) -> float:
    return float(np.mean([float(row[key]) for row in rows]))


def run_seed(
    seed: int,
    cfg: Exp001Config,
    condition: Condition,
    *,
    partial_remap: float = 1.0,
    n_contexts: int = 1,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    env_rng, learner_rng, audit_rng = _seed_rngs(seed)
    environment = CausalBCI(cfg.environment, env_rng)
    learner = HypothesisLearner(cfg.learner, condition, learner_rng)
    initial_causal = environment.causal.copy()
    audit = initialization_audit(learner.basis, initial_causal, audit_rng)
    remap_at = int(cfg.trials * cfg.remap_fraction)
    records: list[dict[str, object]] = []
    raw = np.zeros((cfg.trials, 8), dtype=np.float32)
    neural_raw = np.zeros((cfg.trials, 4 * cfg.environment.n_neurons), dtype=np.float32)

    for trial in range(cfg.trials):
        if trial == remap_at:
            environment.remap(partial_remap)
        context = trial % n_contexts
        if n_contexts > 1 and context == 1:
            # Observable context changes the causal role without changing neurons.
            active_causal = -environment.causal
        else:
            active_causal = environment.causal
        saved_causal = environment.causal
        environment.causal = active_causal
        observation = environment.observation(context=context, n_contexts=n_contexts)
        explicit = (
            active_causal * environment.causal_weights
            if condition.explicit_vector_error else None
        )
        action = learner.act(observation, cfg.environment.action_frames, explicit)
        outcome = environment.execute(np.asarray(action["soma"]))
        # Observable global error change modulates the already-selected top-down
        # pattern. This remains a scalar-by-representation signal. Only the
        # positive control substitutes the forbidden neuron-wise causal vector.
        if condition.explicit_vector_error:
            instructive_pattern = active_causal
        else:
            instructive_pattern = np.asarray(action["feedback_pattern"])
        task_modulation = (
            np.asarray(outcome["delta_errors"])[:, None]
            * instructive_pattern[None, :]
            * float(action["feedback_gain"])
        )
        action["dendrite"] = np.asarray(action["dendrite"]) + task_modulation
        learner.delay(environment.distractors())
        learner.learn(float(outcome["global_improvement"]), float(outcome["reward"]), explicit)
        environment.causal = saved_causal
        row = {
            **action,
            **outcome,
            "trial": trial,
            "causal": active_causal.copy(),
            "remapped": trial >= remap_at,
        }
        records.append(row)
        raw[trial] = (
            trial,
            float(outcome["reward"]),
            float(outcome["global_improvement"]),
            float(np.asarray(outcome["errors"])[-1]),
            int(action["hypothesis"]),
            int(action["category"]),
            float(action["resonant"]),
            int(action["resets"]),
        )
        neural_raw[trial] = np.concatenate([
            np.asarray(action["soma"]).mean(0),
            np.asarray(action["dendrite"]).mean(0),
            np.asarray(outcome["causal_contribution"]).mean(0),
            active_causal,
        ])

    window = cfg.evaluation_window
    pre_early = records[:window]
    pre_late = records[remap_at - window:remap_at]
    post_span = cfg.trials - remap_at
    post_early = records[remap_at:remap_at + max(1, post_span // 5)]
    post_late = records[-window:]
    pre_dendritic = dendritic_metrics(pre_late, initial_causal)
    post_causal = np.asarray(post_late[0]["causal"])
    post_dendritic = dendritic_metrics(post_late, post_causal)
    metrics = {
        "seed": seed,
        "initialization_audit": audit,
        "early_success": _mean(pre_early, "reward"),
        "pre_remap_late_success": _mean(pre_late, "reward"),
        "learning_improvement": _mean(pre_late, "reward") - _mean(pre_early, "reward"),
        "post_remap_early_success": _mean(post_early, "reward"),
        "post_remap_late_success": _mean(post_late, "reward"),
        "relearning_improvement": _mean(post_late, "reward") - _mean(post_early, "reward"),
        "pre_remap_global_improvement": _mean(pre_late, "global_improvement"),
        "post_remap_global_improvement": _mean(post_late, "global_improvement"),
        "pre_dendritic_role_alignment": pre_dendritic["role_alignment"],
        "post_dendritic_role_alignment": post_dendritic["role_alignment"],
        "pre_appropriate_sign_fraction": pre_dendritic["appropriate_sign_fraction"],
        "post_appropriate_sign_fraction": post_dendritic["appropriate_sign_fraction"],
        "pre_opposite_population_signs": pre_dendritic["opposite_population_signs"],
        "post_opposite_population_signs": post_dendritic["opposite_population_signs"],
        "early_residual_predicts_later_soma": longitudinal_prediction(
            pre_early, pre_late, initial_causal
        ),
        "post_residual_predicts_later_soma": longitudinal_prediction(
            post_early, post_late, post_causal
        ),
        "resonance_rate": _mean(records, "resonant"),
        "reset_rate": float(np.mean([int(row["resets"]) > 0 for row in records])),
        "category_recruitments": learner.category_recruitments,
        "passive_sensory_mean": float(np.mean([
            np.asarray(row["passive_sensory"]).mean() for row in post_late
        ])),
        "best_initial_basis_alignment": audit["max_absolute_correlation"],
        "selected_post_basis_alignment": float(np.corrcoef(
            learner.basis[int(np.bincount(
                [int(row["hypothesis"]) for row in post_late],
                minlength=cfg.learner.n_hypotheses,
            ).argmax())], post_causal
        )[0, 1]),
    }
    return metrics, raw, neural_raw


SUMMARY_KEYS = (
    "early_success", "pre_remap_late_success", "learning_improvement",
    "post_remap_early_success", "post_remap_late_success", "relearning_improvement",
    "pre_remap_global_improvement", "post_remap_global_improvement",
    "pre_dendritic_role_alignment", "post_dendritic_role_alignment",
    "pre_appropriate_sign_fraction", "post_appropriate_sign_fraction",
    "pre_opposite_population_signs", "post_opposite_population_signs",
    "early_residual_predicts_later_soma", "post_residual_predicts_later_soma",
    "resonance_rate", "reset_rate", "category_recruitments", "passive_sensory_mean",
    "best_initial_basis_alignment", "selected_post_basis_alignment",
)


def run_condition(
    name: str,
    cfg: Exp001Config,
    seeds: tuple[int, ...],
    *,
    condition: Condition | None = None,
    partial_remap: float = 1.0,
    n_contexts: int = 1,
    detailed_raw: bool = False,
) -> dict[str, Any]:
    seed_results = []
    raw_results = []
    neural_raw_results = []
    active_condition = condition or CONDITIONS[name]
    for seed in seeds:
        metrics, raw, neural_raw = run_seed(
            seed, cfg, active_condition, partial_remap=partial_remap, n_contexts=n_contexts
        )
        seed_results.append(metrics)
        raw_results.append(raw)
        if detailed_raw:
            neural_raw_results.append(neural_raw)
    audit_signed = [row["initialization_audit"]["mean_signed_correlation"] for row in seed_results]
    audit_p = [row["initialization_audit"]["decoder_permutation_p"] for row in seed_results]
    observed_decoder = np.array([
        row["initialization_audit"]["decoder_accuracy"] for row in seed_results
    ])
    group_null = np.array([
        row["initialization_audit"]["decoder_null_accuracies"] for row in seed_results
    ]).mean(0)
    group_decoder_p = float((1 + np.sum(group_null >= observed_decoder.mean())) / (len(group_null) + 1))
    result = {
        "condition": name,
        "summary": {
            **{key: float(np.mean([row[key] for row in seed_results])) for key in SUMMARY_KEYS},
            "initial_mean_signed_correlation": float(np.mean(audit_signed)),
            "initial_decoder_mean_permutation_p": float(np.mean(audit_p)),
            "initial_decoder_significant_seed_fraction": float(np.mean(np.asarray(audit_p) < 0.05)),
            "initial_decoder_group_permutation_p": group_decoder_p,
        },
        "seeds": seed_results,
        "_raw": np.stack(raw_results),
    }
    if detailed_raw:
        result["_raw_neural"] = np.stack(neural_raw_results)
    return result


def run_primary_suite(cfg: Exp001Config, phase: str) -> dict[str, Any]:
    seeds = cfg.development_seeds if phase == "development" else cfg.confirmatory_seeds
    conditions = {name: run_condition(name, cfg, seeds, detailed_raw=True) for name in CONDITIONS}
    return {"phase": phase, "config": asdict(cfg), "conditions": conditions}


def run_capacity_sweep(cfg: Exp001Config, seeds: tuple[int, ...]) -> dict[str, Any]:
    result = {}
    for capacity in (2, 8, 32, 128, 512):
        varied = replace(cfg, learner=replace(cfg.learner, n_hypotheses=capacity))
        result[str(capacity)] = run_condition("grossberg_inspired_full", varied, seeds)
    return result


def run_robustness_sweeps(cfg: Exp001Config) -> dict[str, Any]:
    seeds = cfg.development_seeds
    specifications = {
        "vigilance": (0.60, 0.80, 0.95),
        "attention_gain": (0.45, 1.0, 1.5),
        "wm_persistence": (0.40, 0.80, 0.96),
        "reinforcement_lr": (0.04, 0.12, 0.30),
        "exploration": (0.05, 0.20, 0.45),
        "n_hypotheses": (8, 32, 128),
    }
    output = {}
    for parameter, values in specifications.items():
        output[parameter] = {}
        for value in values:
            learner = replace(cfg.learner, **{parameter: value})
            varied = replace(cfg, learner=learner)
            output[parameter][str(value)] = run_condition(
                "grossberg_inspired_full", varied, seeds
            )
    return output


def run_generalization(cfg: Exp001Config) -> dict[str, Any]:
    seeds = cfg.development_seeds
    probes: dict[str, tuple[Exp001Config, float, int]] = {
        "n6_balanced": (replace(cfg, learner=replace(cfg.learner, n_neurons=6), environment=replace(cfg.environment, n_neurons=6)), 1.0, 1),
        "n20_balanced": (replace(cfg, learner=replace(cfg.learner, n_neurons=20), environment=replace(cfg.environment, n_neurons=20)), 1.0, 1),
        "unequal_3_of_10_plus": (replace(cfg, environment=replace(cfg.environment, n_plus=3)), 1.0, 1),
        "weak_causal": (replace(cfg, environment=replace(cfg.environment, causal_strength=0.30)), 1.0, 1),
        "noisy_transition": (replace(cfg, environment=replace(cfg.environment, transition_noise=0.08)), 1.0, 1),
        "noisy_causal_weights": (replace(cfg, environment=replace(cfg.environment, causal_weight_noise=0.35)), 1.0, 1),
        "partial_remap": (cfg, 0.50, 1),
        "stochastic_reward": (replace(cfg, environment=replace(cfg.environment, stochastic_reward=0.15)), 1.0, 1),
        "long_delay": (replace(cfg, environment=replace(cfg.environment, delay_steps=12)), 1.0, 1),
        "target_075": (replace(cfg, environment=replace(cfg.environment, target=0.75)), 1.0, 1),
        "opposing_contexts": (cfg, 1.0, 2),
    }
    return {
        name: run_condition("grossberg_inspired_full", varied, seeds, partial_remap=remap, n_contexts=contexts)
        for name, (varied, remap, contexts) in probes.items()
    }


def run_art_search_probe(cfg: Exp001Config) -> dict[str, Any]:
    """Force observable context mismatch so reset and uncommitted recruitment occur."""
    output = {}
    for vigilance in (0.60, 0.80, 0.95):
        varied = replace(cfg, learner=replace(cfg.learner, vigilance=vigilance))
        output[str(vigilance)] = {
            "search_enabled": run_condition(
                "grossberg_inspired_full", varied, cfg.development_seeds, n_contexts=2
            ),
            "search_disabled": run_condition(
                "no_reset_search", varied, cfg.development_seeds, n_contexts=2
            ),
        }
    return output
