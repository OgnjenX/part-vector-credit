"""EXP005 generic de-novo topology diagnostic after the Outcome-E hard stop."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from .model import Condition, GenericNodePerturbationLearner, HiddenVectorOracle, LearnerConfig


@dataclass(frozen=True)
class TaskConfig:
    action_frames: int = 3
    state_gain: float = 0.65
    success_threshold: float = 0.60


@dataclass(frozen=True)
class Exp005Config:
    development_seeds: tuple[int, ...] = (501, 502, 503, 504)
    confirmatory_seeds: tuple[int, ...] = tuple(range(9500, 9516))
    neuron_counts: tuple[int, ...] = (8, 16, 32, 64)
    acquisition_episodes: int = 1280
    remap_episodes: int = 2560
    learner: LearnerConfig = field(default_factory=LearnerConfig)
    task: TaskConfig = field(default_factory=TaskConfig)


@dataclass(frozen=True)
class Scenario:
    name: str
    n_neurons: int
    condition: str


CONDITIONS = {
    "generic_node_perturbation": Condition("generic_node_perturbation"),
    "plasticity_disabled": Condition("plasticity_disabled", plasticity=False),
    "outcome_shuffled": Condition("outcome_shuffled", shuffle_outcomes=True),
    "temporal_eligibility_disabled": Condition(
        "temporal_eligibility_disabled", temporal_eligibility=False
    ),
    "exploration_removed": Condition("exploration_removed", exploration=False),
    "random_no_learning": Condition(
        "random_no_learning",
        plasticity=False,
        exploration=True,
        zero_initial_topology=True,
    ),
    "hidden_vector_oracle": Condition(
        "hidden_vector_oracle", exploration=False, hidden_vector_oracle=True
    ),
}


def scenario_suite(cfg: Exp005Config) -> tuple[Scenario, ...]:
    scenarios = []
    for n in cfg.neuron_counts:
        for condition in (
            "generic_node_perturbation",
            "outcome_shuffled",
            "hidden_vector_oracle",
        ):
            scenarios.append(Scenario(f"n{n}_{condition}", n, condition))
    for condition in (
        "plasticity_disabled",
        "temporal_eligibility_disabled",
        "exploration_removed",
        "random_no_learning",
    ):
        scenarios.append(Scenario(f"n32_{condition}", 32, condition))
    return tuple(scenarios)


def _rng(seed: int, stream: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, 5005, stream]))


def balanced_role(rng: np.random.Generator, n_neurons: int) -> np.ndarray:
    if n_neurons % 2:
        raise ValueError("balanced roles require an even neuron count")
    role = np.r_[np.ones(n_neurons // 2), -np.ones(n_neurons // 2)]
    return role[rng.permutation(n_neurons)]


def independent_remap(
    rng: np.random.Generator, role: np.ndarray
) -> np.ndarray:
    for _ in range(1000):
        candidate = balanced_role(rng, role.size)
        fraction_changed = float(np.mean(candidate != role))
        if 0.25 <= fraction_changed <= 0.75:
            return candidate
    raise RuntimeError("failed to generate a balanced, nontrivial remap")


def safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.size < 2 or y.size < 2 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _episode(
    learner: GenericNodePerturbationLearner | HiddenVectorOracle,
    role: np.ndarray,
    cfg: Exp005Config,
    rng: np.random.Generator,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    if isinstance(learner, GenericNodePerturbationLearner):
        learner.start_episode()
    state = 0.0
    somas = []
    perturbations = []
    states = [state]
    for _ in range(cfg.task.action_frames):
        soma, perturbation = learner.emit(rng)
        drive = 2.0 * float(np.dot(soma - 0.5, role)) / role.size
        state = float(np.clip(state + cfg.task.state_gain * drive, -1.0, 1.0))
        somas.append(soma)
        perturbations.append(perturbation)
        states.append(state)
    return state, np.stack(somas), np.stack(perturbations), np.asarray(states)


def _stable_behavior(weights: np.ndarray, role: np.ndarray, cfg: Exp005Config) -> float:
    soma = np.clip(0.5 + weights, 0.0, 1.0)
    drive = 2.0 * float(np.dot(soma - 0.5, role)) / role.size
    return float(np.clip(cfg.task.action_frames * cfg.task.state_gain * drive, -1.0, 1.0))


def run_seed(
    seed: int, scenario: Scenario, cfg: Exp005Config
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    role_rng = _rng(seed, 1)
    role = balanced_role(role_rng, scenario.n_neurons)
    remapped_role = independent_remap(role_rng, role)
    condition = CONDITIONS[scenario.condition]
    learner_rng = _rng(seed, 2)
    if condition.hidden_vector_oracle:
        learner: GenericNodePerturbationLearner | HiddenVectorOracle = HiddenVectorOracle(
            scenario.n_neurons, cfg.learner, learner_rng
        )
    else:
        learner = GenericNodePerturbationLearner(
            scenario.n_neurons, cfg.learner, condition, learner_rng
        )
    initial_weights = learner.weights.copy()
    initial_alignment = safe_corr(initial_weights, role)

    total_episodes = cfg.acquisition_episodes + cfg.remap_episodes
    weights_trajectory = [initial_weights.copy()]
    soma_rows = []
    perturbation_rows = []
    state_rows = []
    rewards = []
    role_phase = []
    episode_alignment = []
    pre_remap_weights = initial_weights.copy()
    episode_rng = _rng(seed, 3)
    shuffle_rng = _rng(seed, 4)

    for episode in range(total_episodes):
        if episode == cfg.acquisition_episodes:
            if isinstance(learner, GenericNodePerturbationLearner):
                learner.apply_pending(shuffle_rng)
            pre_remap_weights = learner.weights.copy()
            weights_trajectory.append(pre_remap_weights.copy())
        active_role = role if episode < cfg.acquisition_episodes else remapped_role
        reward, somas, perturbations, states = _episode(
            learner, active_role, cfg, episode_rng
        )
        if isinstance(learner, HiddenVectorOracle):
            learner.privileged_update(active_role, episode)
        else:
            learner.close_episode(reward, episode)
            if learner.batch_ready():
                learner.apply_pending(shuffle_rng)
        soma_rows.append(somas)
        perturbation_rows.append(perturbations)
        state_rows.append(states)
        rewards.append(reward)
        role_phase.append(0 if episode < cfg.acquisition_episodes else 1)
        episode_alignment.append(safe_corr(learner.weights, active_role))
        if (episode + 1) % cfg.learner.batch_size == 0:
            weights_trajectory.append(learner.weights.copy())

    if isinstance(learner, GenericNodePerturbationLearner):
        learner.apply_pending(shuffle_rng)
    final_weights = learner.weights.copy()
    weights_trajectory.append(final_weights.copy())

    all_somas = np.stack(soma_rows)
    sample_alignments_pre = np.asarray([
        safe_corr(pattern - 0.5, role)
        for pattern in all_somas[: cfg.acquisition_episodes].reshape(-1, scenario.n_neurons)
    ])
    sample_alignments_post = np.asarray([
        safe_corr(pattern - 0.5, remapped_role)
        for pattern in all_somas[cfg.acquisition_episodes :].reshape(-1, scenario.n_neurons)
    ])
    updates = learner.update_log
    update_delta = np.stack([row["delta"] for row in updates])
    eligibility = np.stack([row["eligibility"] for row in updates])
    assigned_reward = np.asarray([row["assigned_reward"] for row in updates])
    true_reward = np.asarray([row["true_reward"] for row in updates])
    advantage = np.asarray([row["advantage"] for row in updates])
    update_episode = np.asarray([row["episode"] for row in updates], dtype=int)

    reconstructed = initial_weights.copy()
    for delta in update_delta:
        reconstructed += delta
    reconstruction_rmse = float(np.sqrt(np.mean((reconstructed - final_weights) ** 2)))
    legal_update_errors = []
    legal_reconstruction = initial_weights.copy()
    if isinstance(learner, GenericNodePerturbationLearner):
        for recorded_delta, local_eligibility, local_advantage in zip(
            update_delta, eligibility, advantage, strict=True
        ):
            before = legal_reconstruction.copy()
            proposed = learner.effective_learning_rate * local_advantage * local_eligibility
            if condition.plasticity and np.any(proposed):
                legal_reconstruction += proposed
                legal_reconstruction = np.clip(
                    legal_reconstruction,
                    -cfg.learner.weight_bound,
                    cfg.learner.weight_bound,
                )
                legal_reconstruction -= legal_reconstruction.mean()
                legal_reconstruction = np.clip(
                    legal_reconstruction,
                    -cfg.learner.weight_bound,
                    cfg.learner.weight_bound,
                )
            predicted_delta = legal_reconstruction - before
            legal_update_errors.append(predicted_delta - recorded_delta)
    else:
        legal_update_errors.append(np.zeros_like(update_delta))
    legal_update_reconstruction_rmse = float(
        np.sqrt(np.mean(np.asarray(legal_update_errors) ** 2))
    )
    changed = role != remapped_role
    sign_reversal_accuracy = float(
        np.mean(np.sign(final_weights[changed]) == np.sign(remapped_role[changed]))
    )
    pre_alignment = safe_corr(pre_remap_weights, role)
    post_alignment = safe_corr(final_weights, remapped_role)
    best_pre_sample = float(np.max(sample_alignments_pre))
    best_post_sample = float(np.max(sample_alignments_post))

    valid_local = np.isfinite(advantage)
    predicted = np.zeros_like(update_delta)
    if isinstance(learner, GenericNodePerturbationLearner):
        predicted = learner.effective_learning_rate * advantage[:, None] * eligibility
    flat_delta = update_delta[valid_local].ravel()
    flat_eligibility = eligibility[valid_local].ravel()
    local_eligibility_update_corr = safe_corr(flat_eligibility, flat_delta)
    local_prediction_corr = safe_corr(predicted[valid_local].ravel(), flat_delta)
    pre_mask = update_episode < cfg.acquisition_episodes
    post_mask = ~pre_mask

    def covariance_role_alignment(mask: np.ndarray, active_role: np.ndarray) -> float:
        if not np.any(mask) or not np.all(np.isfinite(true_reward[mask])):
            return 0.0
        cell_correlations = np.asarray([
            safe_corr(eligibility[mask, neuron], true_reward[mask])
            for neuron in range(scenario.n_neurons)
        ])
        return safe_corr(cell_correlations, active_role)

    update_norm = np.linalg.norm(update_delta, axis=1)

    metrics = {
        "seed": seed,
        "n_neurons": scenario.n_neurons,
        "condition": scenario.condition,
        "initial_alignment": initial_alignment,
        "pre_remap_alignment": pre_alignment,
        "old_topology_to_new_role": safe_corr(pre_remap_weights, remapped_role),
        "post_remap_alignment": post_alignment,
        "pre_correct_sign_fraction": float(np.mean(np.sign(pre_remap_weights) == role)),
        "post_correct_sign_fraction": float(
            np.mean(np.sign(final_weights) == remapped_role)
        ),
        "sign_reversal_accuracy": sign_reversal_accuracy,
        "pre_behavior": _stable_behavior(pre_remap_weights, role, cfg),
        "post_behavior": _stable_behavior(final_weights, remapped_role, cfg),
        "pre_success": float(
            _stable_behavior(pre_remap_weights, role, cfg) >= cfg.task.success_threshold
        ),
        "post_success": float(
            _stable_behavior(final_weights, remapped_role, cfg) >= cfg.task.success_threshold
        ),
        "best_pre_exploratory_sample_alignment": best_pre_sample,
        "best_post_exploratory_sample_alignment": best_post_sample,
        "pre_minus_best_sample": pre_alignment - best_pre_sample,
        "post_minus_best_sample": post_alignment - best_post_sample,
        "weight_distance": float(np.linalg.norm(final_weights - initial_weights)),
        "reconstruction_rmse": reconstruction_rmse,
        "legal_update_reconstruction_rmse": legal_update_reconstruction_rmse,
        "local_eligibility_update_corr": local_eligibility_update_corr,
        "local_prediction_update_corr": local_prediction_corr,
        "pre_local_variation_outcome_role_alignment": covariance_role_alignment(
            pre_mask, role
        ),
        "post_local_variation_outcome_role_alignment": covariance_role_alignment(
            post_mask, remapped_role
        ),
        "outcome_update_magnitude_corr": safe_corr(np.abs(advantage), update_norm),
        "initial_to_final_prediction": safe_corr(initial_weights, final_weights),
    }
    raw = {
        "role_initial": role,
        "role_remap": remapped_role,
        "weights_initial": initial_weights,
        "weights_pre_remap": pre_remap_weights,
        "weights_final": final_weights,
        "weights_trajectory": np.stack(weights_trajectory).astype(np.float32),
        "soma": all_somas.astype(np.float32),
        "perturbation": np.stack(perturbation_rows).astype(np.float32),
        "state": np.stack(state_rows).astype(np.float32),
        "episode_reward": np.asarray(rewards),
        "role_phase": np.asarray(role_phase),
        "episode_alignment": np.asarray(episode_alignment),
        "update_delta": update_delta,
        "update_eligibility": eligibility,
        "update_assigned_reward": assigned_reward,
        "update_true_reward": true_reward,
        "update_advantage": advantage,
        "update_episode": update_episode,
        "sample_alignment_pre": sample_alignments_pre,
        "sample_alignment_post": sample_alignments_post,
    }
    return metrics, raw


def run_scenario(
    scenario: Scenario, cfg: Exp005Config, seeds: tuple[int, ...]
) -> dict[str, Any]:
    rows = []
    raw = []
    for seed in seeds:
        metrics, arrays = run_seed(seed, scenario, cfg)
        rows.append(metrics)
        raw.append(arrays)
    return {"scenario": asdict(scenario), "seeds": rows, "_raw": raw}
