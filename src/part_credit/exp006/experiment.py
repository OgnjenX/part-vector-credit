"""Prospective EXP006 benchmark runner."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from .environment import (
    FrancioniBCI,
    FrancioniTaskConfig,
    balanced_role,
    independent_remap,
)
from .model import (
    Action,
    ARTRepertoireLearner,
    Condition,
    HybridLearner,
    LearnerConfig,
    LocalEligibilityLearner,
    RandomNoLearning,
    VectorOracle,
    random_balanced_repertoire,
    safe_corr,
)
from .observation import (
    ObservationConfig,
    cross_validated_linear_decode,
    simulate_residuals,
    standardize_feedback,
)


@dataclass(frozen=True)
class Exp006Config:
    development_seeds: tuple[int, ...] = tuple(range(601, 609))
    confirmatory_seeds: tuple[int, ...] = tuple(range(12000, 12032))
    trials_per_block: int = 64
    acquisition_blocks: int = 14
    remap_blocks: int = 14
    task: FrancioniTaskConfig = field(default_factory=FrancioniTaskConfig)
    learner: LearnerConfig = field(default_factory=LearnerConfig)
    observation: ObservationConfig = field(default_factory=ObservationConfig)

    @property
    def acquisition_trials(self) -> int:
        return self.trials_per_block * self.acquisition_blocks

    @property
    def remap_trials(self) -> int:
        return self.trials_per_block * self.remap_blocks


@dataclass(frozen=True)
class Scenario:
    name: str
    model: str
    condition: Condition


def scenario_suite() -> tuple[Scenario, ...]:
    return (
        Scenario("vector_oracle", "vector", Condition("vector_oracle")),
        Scenario("art_repertoire", "art", Condition("art_repertoire")),
        Scenario("local_eligibility", "eligibility", Condition("local_eligibility")),
        Scenario("art_eligibility_hybrid", "hybrid", Condition("art_eligibility_hybrid")),
        Scenario("random_no_learning", "random", Condition("random_no_learning")),
        Scenario(
            "art_outcome_shuffled",
            "art",
            Condition("art_outcome_shuffled", shuffle_modulators=True),
        ),
        Scenario(
            "eligibility_outcome_shuffled",
            "eligibility",
            Condition("eligibility_outcome_shuffled", shuffle_modulators=True),
        ),
        Scenario(
            "eligibility_exploration_removed",
            "eligibility",
            Condition("eligibility_exploration_removed", exploration=False),
        ),
        Scenario(
            "eligibility_trace_removed",
            "eligibility",
            Condition("eligibility_trace_removed", temporal_eligibility=False),
        ),
        Scenario(
            "hybrid_no_eligibility",
            "hybrid",
            Condition("hybrid_no_eligibility", eligibility_plasticity=False),
        ),
    )


def _rng(seed: int, stream: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, 6006, stream]))


def _build_learner(
    *,
    seed: int,
    scenario: Scenario,
    cfg: Exp006Config,
    role: np.ndarray,
    bank: np.ndarray,
) -> Any:
    if scenario.model == "vector":
        return VectorOracle(role, cfg.learner, _rng(seed, 30))
    if scenario.model == "art":
        return ARTRepertoireLearner(
            bank, cfg.learner, scenario.condition, _rng(seed, 31)
        )
    if scenario.model == "eligibility":
        return LocalEligibilityLearner(
            cfg.task.n_neurons,
            cfg.learner,
            scenario.condition,
            _rng(seed, 32),
        )
    if scenario.model == "hybrid":
        return HybridLearner(
            bank,
            cfg.learner,
            scenario.condition,
            _rng(seed, 31),
            _rng(seed, 32),
        )
    if scenario.model == "random":
        return RandomNoLearning(cfg.task.n_neurons, _rng(seed, 33))
    raise ValueError(f"unknown model: {scenario.model}")


def _late_slice(start: int, stop: int, trials_per_block: int) -> slice:
    return slice(max(start, stop - 2 * trials_per_block), stop)


def _trial_vectors(residual: np.ndarray, valid: np.ndarray) -> np.ndarray:
    vectors = np.zeros((residual.shape[0], residual.shape[-1]), dtype=float)
    for trial in range(residual.shape[0]):
        indices = np.flatnonzero(valid[trial])
        if indices.size:
            selected = indices[-2:]
            vectors[trial] = np.nanmean(residual[trial, selected], axis=0)
    return vectors


def _vectorization_score(
    signal: np.ndarray,
    visible_delta: np.ndarray,
    valid: np.ndarray,
    trial_roles: np.ndarray,
    trial_mask: np.ndarray,
) -> float:
    selected_trials = np.flatnonzero(trial_mask)
    values = []
    for trial in selected_trials:
        frame_mask = valid[trial] & (np.abs(visible_delta[trial]) > 1e-12)
        if not np.any(frame_mask):
            continue
        direction = np.sign(visible_delta[trial, frame_mask])[:, None]
        values.append(
            signal[trial, frame_mask]
            * direction
            * trial_roles[trial][None, :]
        )
    return float(np.nanmean(np.concatenate(values))) if values else 0.0


def _matched_vectorization_score(
    signal: np.ndarray,
    soma: np.ndarray,
    visible_delta: np.ndarray,
    valid: np.ndarray,
    trial_roles: np.ndarray,
    trial_mask: np.ndarray,
    *,
    bins: int = 10,
) -> tuple[float, int]:
    """Match the four role-by-direction groups within fixed soma bins."""
    groups: dict[tuple[int, int, int], list[float]] = {}
    selected_trials = np.flatnonzero(trial_mask)
    edges = np.linspace(0.0, 1.0, bins + 1)
    for trial in selected_trials:
        for frame in np.flatnonzero(
            valid[trial] & (np.abs(visible_delta[trial]) > 1e-12)
        ):
            direction = int(np.sign(visible_delta[trial, frame]))
            for neuron, role in enumerate(trial_roles[trial].astype(int)):
                activity = float(soma[trial, frame, neuron])
                bin_index = min(bins - 1, int(np.searchsorted(edges, activity, side="right") - 1))
                key = (bin_index, role, direction)
                groups.setdefault(key, []).append(
                    float(signal[trial, frame, neuron]) * role * direction
                )
    matched: list[float] = []
    role_directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    for bin_index in range(bins):
        rows = [groups.get((bin_index, role, direction), []) for role, direction in role_directions]
        count = min(map(len, rows))
        if count == 0:
            continue
        for row in rows:
            indices = np.linspace(0, len(row) - 1, count, dtype=int)
            matched.extend(row[index] for index in indices)
    if not matched:
        return float("nan"), 0
    return float(np.mean(matched)), len(matched)


def _blocks_to_criterion(
    success: np.ndarray,
    start: int,
    stop: int,
    trials_per_block: int,
    *,
    threshold: float = 0.70,
    consecutive: int = 2,
) -> int:
    block_rates = np.asarray([
        np.mean(success[index : index + trials_per_block])
        for index in range(start, stop, trials_per_block)
    ])
    for index in range(block_rates.size - consecutive + 1):
        if np.all(block_rates[index : index + consecutive] >= threshold):
            return index + consecutive
    return int(block_rates.size + 1)


def _prospective_score(
    residual: np.ndarray,
    soma: np.ndarray,
    visible_delta: np.ndarray,
    valid: np.ndarray,
    start: int,
    stop: int,
) -> float:
    width = max(1, (stop - start) // 4)
    early_trials = np.arange(start, start + width)
    late_trials = np.arange(stop - width, stop)
    early_signal = []
    early_activity = []
    late_activity = []
    for neuron in range(soma.shape[-1]):
        signal_values = []
        for trial in early_trials:
            mask = valid[trial] & (np.abs(visible_delta[trial]) > 1e-12)
            if np.any(mask):
                signal_values.extend(
                    (
                        residual[trial, mask, neuron]
                        * np.sign(visible_delta[trial, mask])
                    ).tolist()
                )
        later = [
            soma[trial, valid[trial], neuron]
            for trial in late_trials
            if np.any(valid[trial])
        ]
        early_signal.append(float(np.mean(signal_values)) if signal_values else 0.0)
        baseline_values = soma[start, valid[start], neuron]
        early_activity.append(
            float(np.mean(baseline_values)) if baseline_values.size else 0.0
        )
        late_activity.append(
            float(np.mean(np.concatenate(later))) if later else 0.0
        )
    baseline = np.asarray(early_activity)
    change = np.asarray(late_activity) - baseline
    design = np.column_stack([np.ones(baseline.size), baseline])
    adjusted_change = change - design @ np.linalg.lstsq(design, change, rcond=None)[0]
    return safe_corr(np.asarray(early_signal), adjusted_change)


def run_seed(
    seed: int,
    scenario: Scenario,
    cfg: Exp006Config,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    role_rng = _rng(seed, 1)
    role = balanced_role(role_rng, cfg.task.n_neurons)
    remapped_role = independent_remap(role_rng, role)
    bank = random_balanced_repertoire(
        _rng(seed, 2),
        n_neurons=cfg.task.n_neurons,
        size=cfg.learner.repertoire_size,
        amplitude=cfg.learner.motor_amplitude,
    )
    learner = _build_learner(
        seed=seed,
        scenario=scenario,
        cfg=cfg,
        role=role,
        bank=bank,
    )
    environment = FrancioniBCI(cfg.task, role)
    total_trials = cfg.acquisition_trials + cfg.remap_trials
    shape = (total_trials, cfg.task.max_frames, cfg.task.n_neurons)
    soma = np.full(shape, np.nan, dtype=float)
    deterministic = np.full(shape, np.nan, dtype=float)
    perturbation = np.full(shape, np.nan, dtype=float)
    feedback = np.full(shape, np.nan, dtype=float)
    feedback_art = np.full(shape, np.nan, dtype=float)
    feedback_eligibility = np.full(shape, np.nan, dtype=float)
    feedback_vector = np.full(shape, np.nan, dtype=float)
    visible_delta = np.full(shape[:2], np.nan, dtype=float)
    latent_delta = np.full(shape[:2], np.nan, dtype=float)
    displayed_state = np.full(shape[:2], np.nan, dtype=float)
    valid = np.zeros(shape[:2], dtype=bool)
    success = np.zeros(total_trials, dtype=float)
    frames_used = np.zeros(total_trials, dtype=int)
    post_soma = np.zeros((total_trials, cfg.task.n_neurons), dtype=float)
    post_feedback = np.zeros_like(post_soma)
    post_feedback_art = np.zeros_like(post_soma)
    post_feedback_eligibility = np.zeros_like(post_soma)
    post_feedback_vector = np.zeros_like(post_soma)
    trial_roles = np.zeros_like(post_soma)
    canonical_observation = np.asarray([0.0, 0.0, 0.5])
    initial_topology = learner.representative_action(canonical_observation) - 0.5
    pre_remap_topology = initial_topology.copy()

    for trial in range(total_trials):
        remapped = trial >= cfg.acquisition_trials
        active_role = remapped_role if remapped else role
        if trial == cfg.acquisition_trials:
            pre_remap_topology = (
                learner.representative_action(canonical_observation) - 0.5
            )
            if isinstance(learner, VectorOracle):
                learner.set_role(remapped_role)
        observation = environment.reset(active_role)
        learner.start_trial()
        phase_index = trial if not remapped else trial - cfg.acquisition_trials
        phase_total = cfg.acquisition_trials if not remapped else cfg.remap_trials
        progress = phase_index / max(1, phase_total - 1)
        last_action: Action | None = None
        for frame in range(cfg.task.max_frames):
            action = learner.act(observation, progress)
            transition = environment.step(action.soma)
            score = float(transition["visible_delta"]) / cfg.task.bin_width
            local_feedback = learner.observe_transition(action, score)
            soma[trial, frame] = action.soma
            deterministic[trial, frame] = action.deterministic
            perturbation[trial, frame] = action.perturbation
            feedback[trial, frame] = local_feedback
            zeros = np.zeros(cfg.task.n_neurons, dtype=float)
            feedback_art[trial, frame] = action.metadata.get(
                "feedback_art", zeros
            )
            feedback_eligibility[trial, frame] = action.metadata.get(
                "feedback_eligibility", zeros
            )
            feedback_vector[trial, frame] = action.metadata.get(
                "feedback_vector", zeros
            )
            visible_delta[trial, frame] = float(transition["visible_delta"])
            latent_delta[trial, frame] = float(transition["latent_delta"])
            displayed_state[trial, frame] = float(transition["displayed_after"])
            valid[trial, frame] = True
            frames_used[trial] = frame + 1
            observation = np.asarray(transition["observation"])
            last_action = action
            if bool(transition["success"]):
                success[trial] = 1.0
                break
        reward = float(success[trial])
        post_feedback[trial] = learner.end_trial(reward)
        components = learner.last_post_components
        post_feedback_art[trial] = components["art"]
        post_feedback_eligibility[trial] = components["eligibility"]
        post_feedback_vector[trial] = components["vector"]
        if last_action is None:
            raise AssertionError("trial completed without an action")
        post_soma[trial] = last_action.soma
        trial_roles[trial] = active_role

    final_topology = learner.representative_action(canonical_observation) - 0.5
    observed = simulate_residuals(
        soma=soma,
        feedback=feedback,
        valid_mask=valid,
        post_soma=post_soma,
        post_feedback=post_feedback,
        cfg=cfg.observation,
        rng=_rng(seed, 50),
    )
    acquisition_mask = np.arange(total_trials) < cfg.acquisition_trials
    remap_mask = ~acquisition_mask
    pre_late = _late_slice(0, cfg.acquisition_trials, cfg.trials_per_block)
    post_late = _late_slice(
        cfg.acquisition_trials,
        total_trials,
        cfg.trials_per_block,
    )
    sample_pre = np.asarray([
        safe_corr(soma[trial, frame] - 0.5, role)
        for trial in range(cfg.acquisition_trials)
        for frame in np.flatnonzero(valid[trial])
    ])
    sample_post = np.asarray([
        safe_corr(soma[trial, frame] - 0.5, remapped_role)
        for trial in range(cfg.acquisition_trials, total_trials)
        for frame in np.flatnonzero(valid[trial])
    ])
    trial_vectors = _trial_vectors(observed["residual"], valid)
    matched_acquisition, matched_acquisition_samples = _matched_vectorization_score(
        observed["residual"],
        soma,
        visible_delta,
        valid,
        trial_roles,
        acquisition_mask,
    )
    matched_remap, matched_remap_samples = _matched_vectorization_score(
        observed["residual"],
        soma,
        visible_delta,
        valid,
        trial_roles,
        remap_mask,
    )
    feedback_art_standardized = standardize_feedback(feedback_art, valid)[0]
    feedback_eligibility_standardized = standardize_feedback(
        feedback_eligibility, valid
    )[0]
    feedback_vector_standardized = standardize_feedback(feedback_vector, valid)[0]
    if scenario.model == "hybrid":
        reconstructed_feedback = (
            cfg.learner.hybrid_art_gain * feedback_art
            + cfg.learner.hybrid_eligibility_gain * feedback_eligibility
        )
        reconstructed_post_feedback = (
            cfg.learner.hybrid_art_gain * post_feedback_art
            + cfg.learner.hybrid_eligibility_gain * post_feedback_eligibility
        )
    else:
        reconstructed_feedback = (
            feedback_art + feedback_eligibility + feedback_vector
        )
        reconstructed_post_feedback = (
            post_feedback_art + post_feedback_eligibility + post_feedback_vector
        )
    metrics = {
        "seed": seed,
        "scenario": scenario.name,
        "model": scenario.model,
        "initial_alignment": safe_corr(initial_topology, role),
        "pre_remap_alignment": safe_corr(pre_remap_topology, role),
        "old_topology_to_new_role": safe_corr(pre_remap_topology, remapped_role),
        "post_remap_alignment": safe_corr(final_topology, remapped_role),
        "pre_correct_sign_fraction": float(
            np.mean(np.sign(pre_remap_topology) == role)
        ),
        "post_correct_sign_fraction": float(
            np.mean(np.sign(final_topology) == remapped_role)
        ),
        "changed_cell_sign_reversal": float(np.mean(
            np.sign(final_topology[role != remapped_role])
            == remapped_role[role != remapped_role]
        )),
        "acquisition_late_success": float(np.mean(success[pre_late])),
        "remap_late_success": float(np.mean(success[post_late])),
        "acquisition_blocks_to_criterion": _blocks_to_criterion(
            success,
            0,
            cfg.acquisition_trials,
            cfg.trials_per_block,
        ),
        "remap_blocks_to_criterion": _blocks_to_criterion(
            success,
            cfg.acquisition_trials,
            total_trials,
            cfg.trials_per_block,
        ),
        "acquisition_mean_frames": float(np.mean(frames_used[pre_late])),
        "remap_mean_frames": float(np.mean(frames_used[post_late])),
        "best_pre_sample_alignment": float(np.max(sample_pre)),
        "best_post_sample_alignment": float(np.max(sample_post)),
        "pre_minus_best_sample": safe_corr(pre_remap_topology, role) - float(np.max(sample_pre)),
        "post_minus_best_sample": safe_corr(final_topology, remapped_role) - float(np.max(sample_post)),
        "best_bank_alignment_initial": float(np.max([
            safe_corr(row - 0.5, role) for row in bank
        ])),
        "best_bank_alignment_remap": float(np.max([
            safe_corr(row - 0.5, remapped_role) for row in bank
        ])),
        "residual_vectorization_acquisition": _vectorization_score(
            observed["residual"], visible_delta, valid, trial_roles, acquisition_mask
        ),
        "residual_vectorization_remap": _vectorization_score(
            observed["residual"], visible_delta, valid, trial_roles, remap_mask
        ),
        "latent_vectorization_acquisition": _vectorization_score(
            observed["feedback_standardized"],
            visible_delta,
            valid,
            trial_roles,
            acquisition_mask,
        ),
        "latent_vectorization_remap": _vectorization_score(
            observed["feedback_standardized"],
            visible_delta,
            valid,
            trial_roles,
            remap_mask,
        ),
        "matched_residual_vectorization_acquisition": matched_acquisition,
        "matched_residual_vectorization_remap": matched_remap,
        "matched_residual_samples_acquisition": matched_acquisition_samples,
        "matched_residual_samples_remap": matched_remap_samples,
        "art_component_vectorization_acquisition": _vectorization_score(
            feedback_art_standardized,
            visible_delta,
            valid,
            trial_roles,
            acquisition_mask,
        ),
        "art_component_vectorization_remap": _vectorization_score(
            feedback_art_standardized,
            visible_delta,
            valid,
            trial_roles,
            remap_mask,
        ),
        "eligibility_component_vectorization_acquisition": _vectorization_score(
            feedback_eligibility_standardized,
            visible_delta,
            valid,
            trial_roles,
            acquisition_mask,
        ),
        "eligibility_component_vectorization_remap": _vectorization_score(
            feedback_eligibility_standardized,
            visible_delta,
            valid,
            trial_roles,
            remap_mask,
        ),
        "vector_component_vectorization_acquisition": _vectorization_score(
            feedback_vector_standardized,
            visible_delta,
            valid,
            trial_roles,
            acquisition_mask,
        ),
        "vector_component_vectorization_remap": _vectorization_score(
            feedback_vector_standardized,
            visible_delta,
            valid,
            trial_roles,
            remap_mask,
        ),
        "feedback_component_reconstruction_error": float(np.nanmax(np.abs(
            feedback[valid] - reconstructed_feedback[valid]
        ))),
        "post_feedback_component_reconstruction_error": float(np.max(np.abs(
            post_feedback - reconstructed_post_feedback
        ))),
        "pre_outcome_decode_balanced_accuracy": cross_validated_linear_decode(
            trial_vectors, success
        ),
        "post_outcome_decode_balanced_accuracy": cross_validated_linear_decode(
            observed["post_residual"], success
        ),
        "prospective_activity_prediction_acquisition": _prospective_score(
            observed["residual"],
            soma,
            visible_delta,
            valid,
            0,
            cfg.acquisition_trials,
        ),
        "prospective_activity_prediction_remap": _prospective_score(
            observed["residual"],
            soma,
            visible_delta,
            valid,
            cfg.acquisition_trials,
            total_trials,
        ),
    }
    raw = {
        "role_initial": role,
        "role_remap": remapped_role,
        "motor_bank": bank,
        "topology_initial": initial_topology,
        "topology_pre_remap": pre_remap_topology,
        "topology_final": final_topology,
        "soma": soma.astype(np.float32),
        "deterministic": deterministic.astype(np.float32),
        "perturbation": perturbation.astype(np.float32),
        "feedback": feedback.astype(np.float32),
        "feedback_art": feedback_art.astype(np.float32),
        "feedback_eligibility": feedback_eligibility.astype(np.float32),
        "feedback_vector": feedback_vector.astype(np.float32),
        "feedback_standardized": observed["feedback_standardized"].astype(np.float32),
        "dendrite": observed["dendrite"].astype(np.float32),
        "residual": observed["residual"].astype(np.float32),
        "post_soma": post_soma.astype(np.float32),
        "post_feedback": post_feedback.astype(np.float32),
        "post_feedback_art": post_feedback_art.astype(np.float32),
        "post_feedback_eligibility": post_feedback_eligibility.astype(np.float32),
        "post_feedback_vector": post_feedback_vector.astype(np.float32),
        "post_residual": observed["post_residual"].astype(np.float32),
        "visible_delta": visible_delta.astype(np.float32),
        "latent_delta": latent_delta.astype(np.float32),
        "displayed_state": displayed_state.astype(np.float32),
        "valid": valid,
        "success": success,
        "frames_used": frames_used,
        "trial_roles": trial_roles,
    }
    return metrics, raw


def run_scenario(
    scenario: Scenario,
    cfg: Exp006Config,
    seeds: tuple[int, ...],
) -> dict[str, Any]:
    rows = []
    raw = []
    for seed in seeds:
        metrics, arrays = run_seed(seed, scenario, cfg)
        rows.append(metrics)
        raw.append(arrays)
    numeric = {}
    for key in rows[0]:
        if key in {"seed", "scenario", "model"}:
            continue
        values = np.asarray([row[key] for row in rows], dtype=float)
        numeric[key] = (
            float(np.nanmean(values)) if np.any(np.isfinite(values)) else float("nan")
        )
    return {
        "scenario": scenario.name,
        "model": scenario.model,
        "config": asdict(cfg),
        "seeds": rows,
        "means": numeric,
        "_raw": raw,
    }
