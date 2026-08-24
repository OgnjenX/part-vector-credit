"""Prospective EXP004 fixed-repertoire topology experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from .banks import (
    BankResult,
    balanced_role,
    bank_geometry,
    composition_bank,
    controlled_coverage_bank,
    random_nested_bank,
)
from .environment import TopologyBCI, TopologyTaskConfig
from .model import TopologyCondition, TopologyController, TopologyLearnerConfig
from .oracles import coverage_metrics, repertoire_oracles, safe_corr


@dataclass(frozen=True)
class Exp004Config:
    development_seeds: tuple[int, ...] = (101, 102, 103, 104)
    confirmatory_seeds: tuple[int, ...] = tuple(range(7000, 7016))
    bank_sizes: tuple[int, ...] = (2, 4, 8, 16, 32, 64, 128)
    controlled_bank_size: int = 16
    fixed_training_episodes: int = 512
    normalized_episodes_per_hypothesis: int = 16
    evaluation_episodes: int = 80
    motor_amplitude: float = 0.15
    maximum_bank_size: int = 128
    task: TopologyTaskConfig = field(default_factory=TopologyTaskConfig)
    learner: TopologyLearnerConfig = field(default_factory=TopologyLearnerConfig)


@dataclass(frozen=True)
class Scenario:
    name: str
    family: str
    n_hypotheses: int
    experience_regime: str
    condition: str
    coverage: str = "uncontrolled"


CONDITIONS: dict[str, TopologyCondition] = {
    "random_selector": TopologyCondition(
        algorithm="random", learn_values=False, learn_topdown=False
    ),
    "contextual_bandit": TopologyCondition(
        algorithm="bandit", category_recruitment=False, category_modification=False
    ),
    "primary_art_outstar": TopologyCondition(),
    "fixed_categories": TopologyCondition(
        fixed_categories=True,
        category_recruitment=False,
        category_modification=False,
    ),
    "no_new_category": TopologyCondition(category_recruitment=False),
    "no_category_modification": TopologyCondition(category_modification=False),
    "outcome_shuffled": TopologyCondition(outcome_shuffled=True),
    "random_reinforcement_target": TopologyCondition(
        random_reinforcement_target=True
    ),
    "generic_scalar_motor_plasticity": TopologyCondition(motor_plasticity=True),
    "explicit_hidden_vector_control": TopologyCondition(
        algorithm="bandit",
        learn_topdown=False,
        category_recruitment=False,
        category_modification=False,
        explicit_vector_control=True,
    ),
}


def scenario_suite(cfg: Exp004Config) -> tuple[Scenario, ...]:
    scenarios: list[Scenario] = []
    for regime in ("fixed", "search_normalized"):
        for size in cfg.bank_sizes:
            for condition in (
                "random_selector", "contextual_bandit", "primary_art_outstar"
            ):
                scenarios.append(Scenario(
                    name=f"random_m{size}_{regime}_{condition}",
                    family="random",
                    n_hypotheses=size,
                    experience_regime=regime,
                    condition=condition,
                ))
    for coverage in ("low", "medium", "high"):
        for condition in ("contextual_bandit", "primary_art_outstar"):
            scenarios.append(Scenario(
                name=f"controlled_{coverage}_{condition}",
                family="controlled",
                n_hypotheses=cfg.controlled_bank_size,
                experience_regime="fixed",
                condition=condition,
                coverage=coverage,
            ))
    for condition in (
        "fixed_categories",
        "no_new_category",
        "no_category_modification",
        "outcome_shuffled",
        "random_reinforcement_target",
    ):
        scenarios.append(Scenario(
            name=f"controlled_medium_{condition}",
            family="controlled",
            n_hypotheses=cfg.controlled_bank_size,
            experience_regime="fixed",
            condition=condition,
            coverage="medium",
        ))
    for condition in (
        "generic_scalar_motor_plasticity", "explicit_hidden_vector_control"
    ):
        scenarios.append(Scenario(
            name=f"controlled_low_{condition}",
            family="controlled",
            n_hypotheses=cfg.controlled_bank_size,
            experience_regime="fixed",
            condition=condition,
            coverage="low",
        ))
    for condition in (
        "random_selector", "contextual_bandit", "primary_art_outstar"
    ):
        scenarios.append(Scenario(
            name=f"composition_{condition}",
            family="composition",
            n_hypotheses=cfg.controlled_bank_size,
            experience_regime="fixed",
            condition=condition,
            coverage="low_single_solvable",
        ))
    return tuple(scenarios)


def training_episodes(cfg: Exp004Config, scenario: Scenario) -> int:
    if scenario.experience_regime == "fixed":
        return cfg.fixed_training_episodes
    if scenario.experience_regime == "search_normalized":
        return cfg.normalized_episodes_per_hypothesis * scenario.n_hypotheses
    raise ValueError(f"unknown experience regime: {scenario.experience_regime}")


def _rng(seed: int, stream: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, 4004, stream]))


def _build_bank(
    seed: int,
    scenario: Scenario,
    cfg: Exp004Config,
    role: np.ndarray,
) -> BankResult:
    rng = _rng(seed, 2)
    if scenario.family == "random":
        return random_nested_bank(
            rng,
            n_neurons=cfg.task.n_neurons,
            max_hypotheses=cfg.maximum_bank_size,
            n_hypotheses=scenario.n_hypotheses,
            amplitude=cfg.motor_amplitude,
        )
    if scenario.family == "controlled":
        return controlled_coverage_bank(
            rng,
            role,
            n_hypotheses=scenario.n_hypotheses,
            coverage=scenario.coverage,
            amplitude=cfg.motor_amplitude,
        )
    if scenario.family == "composition":
        for _ in range(100):
            result = composition_bank(
                rng,
                role,
                n_hypotheses=scenario.n_hypotheses,
                action_frames=cfg.task.action_frames,
                amplitude=cfg.motor_amplitude,
            )
            oracle = repertoire_oracles(
                result.patterns, role, cfg.task, result.phase_masks
            )
            if (
                oracle["best_allowed_sequence"]["success"] == 1.0
                and oracle["allowed_sequence_advantage"] >= 0.20
            ):
                return result
        raise RuntimeError("composition bank failed preregisterable solvability")
    raise ValueError(f"unknown bank family: {scenario.family}")


def _normalized_mutual_information(categories: np.ndarray, contexts: np.ndarray) -> float:
    if categories.size == 0:
        return 0.0
    _, category_ids = np.unique(categories, return_inverse=True)
    _, context_ids = np.unique(contexts, return_inverse=True)
    joint = np.zeros((category_ids.max() + 1, context_ids.max() + 1), dtype=float)
    np.add.at(joint, (category_ids, context_ids), 1.0)
    joint /= joint.sum()
    p_category = joint.sum(axis=1, keepdims=True)
    p_context = joint.sum(axis=0, keepdims=True)
    expected = p_category @ p_context
    nonzero = joint > 0
    mutual = float(np.sum(joint[nonzero] * np.log(joint[nonzero] / expected[nonzero])))
    h_category = float(-np.sum(p_category[p_category > 0] * np.log(p_category[p_category > 0])))
    h_context = float(-np.sum(p_context[p_context > 0] * np.log(p_context[p_context > 0])))
    denominator = max(1e-12, np.sqrt(h_category * h_context))
    return mutual / denominator


def _reconstruct_pair(
    updates: list[dict[str, Any]], category: int, hypothesis: int, n_neurons: int
) -> tuple[np.ndarray, float, float]:
    current = np.zeros(n_neurons, dtype=float)
    residual_initial = 1.0
    selected = [
        row for row in updates
        if row["category"] == category and row["credited_hypothesis"] == hypothesis
    ]
    for row in selected:
        eta = float(row["eta_eff"])
        current += eta * (np.asarray(row["target"]) - current)
        residual_initial *= 1.0 - eta
    minimum_eta = min((float(row["eta_eff"]) for row in selected), default=0.0)
    return current, residual_initial, minimum_eta


def _counterfactual_shuffled_t(
    controller: TopologyController,
    rng: np.random.Generator,
) -> np.ndarray:
    """Keep visits/targets fixed and permute episode outcomes in the local replay."""
    updates = controller.topdown_updates
    if not updates:
        return np.zeros_like(controller.topdown)
    episodes = np.asarray(sorted({int(row["episode"]) for row in updates}))
    outcomes = np.asarray([
        next(float(row["actual_outcome"]) for row in updates if row["episode"] == episode)
        for episode in episodes
    ])
    permuted = outcomes[rng.permutation(outcomes.size)]
    outcome_map = dict(zip(episodes.tolist(), permuted.tolist(), strict=True))
    values = np.zeros_like(controller.values)
    topdown = np.zeros_like(controller.topdown)
    for row in updates:
        category = int(row["category"])
        hypothesis = int(row["credited_hypothesis"])
        strength = float(row["strength"])
        outcome = outcome_map[int(row["episode"])]
        values[category, hypothesis] += (
            controller.cfg.reinforcement_lr
            * strength
            * (outcome - values[category, hypothesis])
        )
        eta = (
            controller.cfg.outstar_lr
            * (1.0 + max(0.0, values[category, hypothesis]))
            * strength
        )
        target = np.asarray(row["target"])
        topdown[category, hypothesis] += eta * (
            target - topdown[category, hypothesis]
        )
    return topdown


def _representation_metrics(
    *,
    controller: TopologyController,
    evaluation_pairs: dict[tuple[int, int], list[tuple[int, int]]],
    roles: dict[int, np.ndarray],
    initial_patterns: np.ndarray,
    shuffled_topdown: np.ndarray,
    phase_masks: np.ndarray | None,
) -> dict[str, float]:
    context_rows = []
    selected_vectors: dict[int, list[np.ndarray]] = {}
    for (context, frame), pairs in evaluation_pairs.items():
        unique, counts = np.unique(np.asarray(pairs), axis=0, return_counts=True)
        index = int(np.argmax(counts))
        category, hypothesis = (int(value) for value in unique[index])
        role = roles[context]
        mask = (
            np.ones(role.size, dtype=bool)
            if phase_masks is None else np.asarray(phase_masks[frame], dtype=bool)
        )
        learned = controller.topdown[category, hypothesis]
        updates = [
            row for row in controller.topdown_updates
            if row["category"] == category
            and row["credited_hypothesis"] == hypothesis
        ]
        targets = (
            np.stack([np.asarray(row["target"]) for row in updates])
            if updates else np.zeros((1, controller.n_neurons))
        )
        reconstruction, initial_coefficient, minimum_eta = _reconstruct_pair(
            controller.topdown_updates, category, hypothesis, controller.n_neurons
        )
        target_alignments = np.asarray([safe_corr(target, role) for target in targets])
        initial_alignments = np.asarray([
            safe_corr(pattern, role) for pattern in initial_patterns
        ])
        simple_average = targets.mean(axis=0)
        context_rows.append({
            "selected_category": category,
            "selected_hypothesis": hypothesis,
            "selected_fraction": float(counts[index] / counts.sum()),
            "t_alignment": safe_corr(learned, role),
            "t_effective_alignment": safe_corr(learned[mask], role[mask]),
            "shuffled_t_alignment": safe_corr(
                shuffled_topdown[category, hypothesis], role
            ),
            "selected_initial_alignment": safe_corr(
                initial_patterns[hypothesis], role
            ),
            "selected_initial_effective_alignment": safe_corr(
                initial_patterns[hypothesis, mask], role[mask]
            ),
            "best_initial_alignment": float(np.max(initial_alignments)),
            "t_improvement_over_best_initial": (
                safe_corr(learned, role) - float(np.max(initial_alignments))
            ),
            "t_improvement_over_best_target": (
                safe_corr(learned, role) - float(np.max(target_alignments))
            ),
            "t_to_selected_initial": safe_corr(
                learned, initial_patterns[hypothesis] - initial_patterns[hypothesis].mean()
            ),
            "t_to_best_target": float(np.max([
                safe_corr(learned, target) for target in targets
            ])),
            "t_to_simple_average": safe_corr(learned, simple_average),
            "simple_average_alignment": safe_corr(simple_average, role),
            "target_count": float(len(updates)),
            "target_alignment_std": float(np.std(target_alignments)),
            "reconstruction_rmse": float(np.sqrt(np.mean((learned - reconstruction) ** 2))),
            "initial_convex_coefficient": initial_coefficient,
            "minimum_eta": minimum_eta,
        })
        selected_vectors.setdefault(hypothesis, []).append(learned)
    same_h_distances = []
    for vectors in selected_vectors.values():
        for left in range(len(vectors)):
            for right in range(left + 1, len(vectors)):
                denominator = np.linalg.norm(vectors[left]) + np.linalg.norm(vectors[right])
                same_h_distances.append(
                    float(np.linalg.norm(vectors[left] - vectors[right]) / max(1e-12, denominator))
                )
    keys = context_rows[0]
    return {
        key: float(np.mean([row[key] for row in context_rows]))
        for key in keys
        if key not in {"selected_category", "selected_hypothesis"}
    } | {
        "selected_categories": [int(row["selected_category"]) for row in context_rows],
        "selected_hypotheses": [int(row["selected_hypothesis"]) for row in context_rows],
        "same_h_category_t_distance": (
            float(np.mean(same_h_distances)) if same_h_distances else 0.0
        ),
    }


def _raw_event_arrays(rows: list[dict[str, Any]], prefix: str) -> dict[str, np.ndarray]:
    if not rows:
        return {
            f"{prefix}_episode": np.empty(0, dtype=np.int32),
            f"{prefix}_frame": np.empty(0, dtype=np.int8),
        }
    arrays: dict[str, np.ndarray] = {
        f"{prefix}_episode": np.asarray([row["episode"] for row in rows], dtype=np.int32),
        f"{prefix}_frame": np.asarray([row["frame"] for row in rows], dtype=np.int8),
    }
    for key in (
        "category", "selected_hypothesis", "credited_hypothesis", "hypothesis"
    ):
        if key in rows[0]:
            arrays[f"{prefix}_{key}"] = np.asarray([row[key] for row in rows], dtype=np.int16)
    for key in (
        "actual_outcome", "credited_outcome", "strength", "eta_eff", "before",
        "after", "delta_norm", "advantage",
    ):
        if key in rows[0] and np.isscalar(rows[0][key]):
            arrays[f"{prefix}_{key}"] = np.asarray([row[key] for row in rows], dtype=np.float32)
    vector_keys = {
        "category_event": ("after",),
        "topdown_update": ("target",),
        "motor_update": ("after",),
    }.get(prefix, ())
    for key in vector_keys:
        if key in rows[0] and not np.isscalar(rows[0][key]):
            arrays[f"{prefix}_{key}"] = np.stack([row[key] for row in rows]).astype(np.float32)
    if "event" in rows[0]:
        event_codes = {name: index for index, name in enumerate(sorted({row["event"] for row in rows}))}
        arrays[f"{prefix}_event_code"] = np.asarray(
            [event_codes[row["event"]] for row in rows], dtype=np.int8
        )
    return arrays


def run_seed(
    seed: int, scenario: Scenario, cfg: Exp004Config
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    role = balanced_role(_rng(seed, 1), cfg.task.n_neurons)
    bank = _build_bank(seed, scenario, cfg, role)
    geometry = bank_geometry(bank.patterns)
    initial_soma = bank.patterns.copy()
    coverage_by_context = {
        context: coverage_metrics(
            initial_soma, role if context == 0 else -role
        )
        for context in range(cfg.task.n_contexts)
    }
    oracle_by_context = {
        context: repertoire_oracles(
            initial_soma,
            role if context == 0 else -role,
            cfg.task,
            bank.phase_masks,
        )
        for context in range(cfg.task.n_contexts)
    }
    if scenario.family in {"controlled", "composition"} and any(
        row["best_allowed_sequence"]["success"] != 1.0
        for row in oracle_by_context.values()
    ):
        raise RuntimeError("bank admitted without an allowed successful sequence")

    condition = CONDITIONS[scenario.condition]
    controller = TopologyController(
        learner_cfg=cfg.learner,
        task_cfg=cfg.task,
        condition=condition,
        motor_bank=bank.patterns,
        rng=_rng(seed, 4),
    )
    environment = TopologyBCI(
        cfg.task, _rng(seed, 3), role, bank.phase_masks
    )
    train_episodes = training_episodes(cfg, scenario)
    total = train_episodes + cfg.evaluation_episodes
    frames = cfg.task.action_frames
    observation_dim = cfg.task.n_contexts + 2
    raw: dict[str, np.ndarray] = {
        "observation": np.zeros((total, frames, observation_dim), dtype=np.float32),
        "soma": np.zeros((total, frames, cfg.task.n_neurons), dtype=np.float32),
        "perturbation": np.zeros((total, frames, cfg.task.n_neurons), dtype=np.float32),
        "hypothesis": np.zeros((total, frames), dtype=np.int16),
        "category": np.zeros((total, frames), dtype=np.int16),
        "resonant": np.zeros((total, frames), dtype=np.int8),
        "state_before": np.zeros((total, frames), dtype=np.float32),
        "state_after": np.zeros((total, frames), dtype=np.float32),
        "causal_score": np.zeros((total, frames), dtype=np.float32),
        "context": np.zeros(total, dtype=np.int8),
        "evaluating": np.zeros(total, dtype=np.int8),
        "reward": np.zeros(total, dtype=np.float32),
        "actual_outcome": np.zeros(total, dtype=np.float32),
        "credited_outcome": np.zeros(total, dtype=np.float32),
        "category_count": np.zeros(total, dtype=np.int16),
    }
    evaluation_pairs: dict[tuple[int, int], list[tuple[int, int]]] = {
        (context, frame): []
        for context in range(cfg.task.n_contexts)
        for frame in range(frames)
    }
    successful_unique_h: list[int] = []

    for episode in range(total):
        evaluating = episode >= train_episodes
        context = episode % cfg.task.n_contexts
        observation = environment.reset(context)
        controller.start_episode()
        progress = float(np.clip(episode / max(1, train_episodes - 1), 0.0, 1.0))
        episode_hypotheses = []
        for frame in range(frames):
            raw["observation"][episode, frame] = observation
            selected = controller.select(
                observation,
                context=context,
                frame=frame,
                state_bin=environment.state_bin(),
                progress=progress,
                evaluating=evaluating,
                episode=episode,
            )
            transition = environment.execute(np.asarray(selected["motor"]))
            soma = np.asarray(transition["soma"])
            controller.record_frame(
                selected,
                soma=soma,
                perturbation=np.asarray(transition["perturbation"]),
                context=context,
                episode=episode,
                frame=frame,
            )
            hypothesis = int(selected["hypothesis"])
            category = int(selected["category"])
            episode_hypotheses.append(hypothesis)
            if evaluating:
                evaluation_pairs[(context, frame)].append((category, hypothesis))
            raw["soma"][episode, frame] = soma
            raw["perturbation"][episode, frame] = transition["perturbation"]
            raw["hypothesis"][episode, frame] = hypothesis
            raw["category"][episode, frame] = category
            raw["resonant"][episode, frame] = int(selected["resonant"])
            raw["state_before"][episode, frame] = transition["state_before"]
            raw["state_after"][episode, frame] = transition["state_after"]
            raw["causal_score"][episode, frame] = transition["causal_score"]
            observation = np.asarray(transition["observation"])
        outcome = environment.outcome()
        learned = {
            "actual_outcome": float(outcome["outcome"]),
            "credited_outcome": float(outcome["outcome"]),
        }
        if not evaluating:
            learned = controller.learn_outcome(
                outcome=float(outcome["outcome"]),
                hidden_role_positive_control=(
                    environment.active_role().copy()
                    if condition.explicit_vector_control else None
                ),
            )
        if evaluating and outcome["reward"] > 0:
            successful_unique_h.append(len(set(episode_hypotheses)))
        raw["context"][episode] = context
        raw["evaluating"][episode] = int(evaluating)
        raw["reward"][episode] = outcome["reward"]
        raw["actual_outcome"][episode] = outcome["outcome"]
        raw["credited_outcome"][episode] = learned["credited_outcome"]
        raw["category_count"][episode] = len(controller.prototypes)

    shuffled_topdown = _counterfactual_shuffled_t(controller, _rng(seed, 8))
    roles = {0: role, 1: -role}
    representation = _representation_metrics(
        controller=controller,
        evaluation_pairs=evaluation_pairs,
        roles=roles,
        initial_patterns=initial_soma,
        shuffled_topdown=shuffled_topdown,
        phase_masks=bank.phase_masks,
    )
    training_mask = raw["evaluating"] == 0
    evaluation_mask = ~training_mask
    training_categories = raw["category"][training_mask].ravel()
    training_contexts = np.repeat(raw["context"][training_mask], frames)
    eval_h = raw["hypothesis"][evaluation_mask].ravel()
    counts = np.bincount(eval_h, minlength=scenario.n_hypotheses).astype(float)
    probabilities = counts / max(1.0, counts.sum())
    nonzero = probabilities > 0
    entropy = float(-np.sum(probabilities[nonzero] * np.log(probabilities[nonzero])))
    max_entropy = np.log(scenario.n_hypotheses)
    mean_coverage = lambda key: float(np.mean([
        coverage_by_context[context][key] for context in coverage_by_context
    ]))
    mean_oracle = lambda oracle, key: float(np.mean([
        oracle_by_context[context][oracle][key]
        for context in oracle_by_context
    ]))
    metrics: dict[str, Any] = {
        "seed": seed,
        "scenario": scenario.name,
        "family": scenario.family,
        "coverage_label": scenario.coverage,
        "condition": scenario.condition,
        "experience_regime": scenario.experience_regime,
        "n_hypotheses": scenario.n_hypotheses,
        "training_episodes": train_episodes,
        "A_single": mean_coverage("A_single"),
        "Q_single": mean_coverage("Q_single"),
        "mean_absolute_alignment": mean_coverage("mean_absolute_alignment"),
        "top_k_alignment": mean_coverage("top_k_alignment"),
        "best_single_success": mean_oracle("best_single", "success"),
        "best_single_behavior": mean_oracle("best_single", "normalized_state"),
        "best_allowed_success": mean_oracle("best_allowed_sequence", "success"),
        "best_allowed_behavior": mean_oracle(
            "best_allowed_sequence", "normalized_state"
        ),
        "allowed_sequence_advantage": float(np.mean([
            oracle_by_context[context]["allowed_sequence_advantage"]
            for context in oracle_by_context
        ])),
        "evaluation_success": float(np.mean(raw["reward"][evaluation_mask])),
        "evaluation_behavior": float(np.mean(
            raw["state_after"][evaluation_mask, -1] / cfg.task.target
        )),
        "behavior_minus_best_single": float(np.mean(
            raw["state_after"][evaluation_mask, -1] / cfg.task.target
        )) - mean_oracle("best_single", "normalized_state"),
        "behavior_oracle_gap": mean_oracle(
            "best_allowed_sequence", "normalized_state"
        ) - float(np.mean(raw["state_after"][evaluation_mask, -1] / cfg.task.target)),
        "mean_successful_unique_h": (
            float(np.mean(successful_unique_h)) if successful_unique_h else 0.0
        ),
        "sequence_diversity": float(len({
            tuple(row) for row in raw["hypothesis"][evaluation_mask]
        }) / max(1, np.sum(evaluation_mask))),
        "category_count": len(controller.prototypes),
        "category_recruitments": controller.recruitments,
        "category_modifications": controller.modifications,
        "prototype_total_change": float(np.sum([
            row["delta_norm"] for row in controller.category_events
        ])),
        "reset_per_selection": controller.total_resets / max(1, controller.selection_events),
        "category_context_nmi": _normalized_mutual_information(
            training_categories, training_contexts
        ),
        "structural_credit_entropy": entropy,
        "structural_credit_concentration": (
            1.0 - entropy / max_entropy if max_entropy > 0 else 1.0
        ),
        "motor_basis_change_norm": float(np.linalg.norm(
            controller.motor_basis - controller.initial_motor_basis
        )),
        "bank_mean_abs_pairwise_similarity": geometry[
            "mean_abs_pairwise_similarity"
        ],
        **representation,
    }
    active_slots = (
        max(1, len(controller.prototypes))
        if condition.algorithm == "art" else controller.n_bandit_states
    )
    raw.update({
        "initial_motor_bank": bank.patterns.astype(np.float32),
        "initial_soma_response": initial_soma.astype(np.float32),
        "hidden_role": role.astype(np.int8),
        "pairwise_similarity": np.asarray(
            geometry["pairwise_similarity"], dtype=np.float32
        ),
        "row_norms": np.asarray(geometry["row_norms"], dtype=np.float32),
        "row_means": np.asarray(geometry["row_means"], dtype=np.float32),
        "row_variances": np.asarray(geometry["row_variances"], dtype=np.float32),
        "phase_masks": (
            np.asarray(bank.phase_masks, dtype=np.int8)
            if bank.phase_masks is not None
            else np.ones((frames, cfg.task.n_neurons), dtype=np.int8)
        ),
        "oracle_frame_scores_context0": np.asarray(
            oracle_by_context[0]["frame_hypothesis_scores"], dtype=np.float32
        ),
        "oracle_frame_scores_context1": np.asarray(
            oracle_by_context[1]["frame_hypothesis_scores"], dtype=np.float32
        ),
        "final_topdown": controller.topdown[:active_slots].astype(
            np.float32
        ),
        "final_values": controller.values[:active_slots].astype(
            np.float32
        ),
        "final_prototypes": (
            np.stack(controller.prototypes).astype(np.float32)
            if controller.prototypes else np.empty((0, observation_dim * 2), dtype=np.float32)
        ),
        **_raw_event_arrays(controller.category_events, "category_event"),
        **_raw_event_arrays(controller.value_updates, "value_update"),
        **_raw_event_arrays(controller.topdown_updates, "topdown_update"),
        **_raw_event_arrays(controller.motor_updates, "motor_update"),
    })
    return metrics, raw


def run_scenario(
    scenario: Scenario, cfg: Exp004Config, seeds: tuple[int, ...]
) -> dict[str, Any]:
    seed_rows = []
    raw_rows = []
    for seed in seeds:
        metrics, raw = run_seed(seed, scenario, cfg)
        seed_rows.append(metrics)
        raw_rows.append(raw)
    return {
        "scenario": asdict(scenario),
        "config": asdict(cfg),
        "seeds": seed_rows,
        "_raw": raw_rows,
    }
