from __future__ import annotations

import inspect

import numpy as np

from part_credit.exp005.experiment import (
    Exp005Config,
    Scenario,
    TaskConfig,
    balanced_role,
    run_seed,
    scenario_suite,
)
from part_credit.exp005.model import (
    Condition,
    GenericNodePerturbationLearner,
    HiddenVectorOracle,
    LearnerConfig,
)


def test_balanced_roles_are_random_and_balanced() -> None:
    first = balanced_role(np.random.default_rng(1), 32)
    second = balanced_role(np.random.default_rng(2), 32)
    assert first.sum() == 0.0
    assert second.sum() == 0.0
    assert not np.array_equal(first, second)


def test_primary_learner_has_no_hidden_role_argument() -> None:
    methods = (
        GenericNodePerturbationLearner.emit,
        GenericNodePerturbationLearner.close_episode,
        GenericNodePerturbationLearner.apply_pending,
    )
    forbidden = {"role", "hidden_role", "causal", "gradient", "target_vector"}
    for method in methods:
        assert set(inspect.signature(method).parameters).isdisjoint(forbidden)
    assert "privileged_update" not in GenericNodePerturbationLearner.__dict__
    assert "privileged_update" in HiddenVectorOracle.__dict__


def test_local_update_is_reconstructible_from_eligibility_and_scalar_outcome() -> None:
    cfg = LearnerConfig(
        learning_rate=0.002,
        initial_weight_sd=0.0,
        batch_size=2,
        weight_bound=10.0,
    )
    learner = GenericNodePerturbationLearner(
        8, cfg, Condition("test"), np.random.default_rng(3)
    )
    rng = np.random.default_rng(4)
    for episode, reward in enumerate((0.4, -0.2)):
        learner.start_episode()
        learner.emit(rng)
        learner.close_episode(reward, episode)
    learner.apply_pending(np.random.default_rng(5))
    for row in learner.update_log:
        effective_rate = cfg.learning_rate * 8 / cfg.learning_rate_reference_neurons
        expected_unclipped = effective_rate * row["advantage"] * row["eligibility"]
        expected = expected_unclipped - expected_unclipped.mean()
        np.testing.assert_allclose(row["delta"], expected, atol=1e-12)


def test_no_exploration_or_no_eligibility_prevents_generic_update() -> None:
    cfg = LearnerConfig(batch_size=1)
    for condition in (
        Condition("no_exploration", exploration=False),
        Condition("no_eligibility", temporal_eligibility=False),
    ):
        learner = GenericNodePerturbationLearner(
            8, cfg, condition, np.random.default_rng(6)
        )
        initial = learner.weights.copy()
        learner.start_episode()
        learner.emit(np.random.default_rng(7))
        learner.close_episode(1.0, 0)
        learner.apply_pending(np.random.default_rng(8))
        np.testing.assert_array_equal(learner.weights, initial)


def test_small_generic_run_learns_and_remaps_without_hidden_vector() -> None:
    cfg = Exp005Config(
        development_seeds=(12,),
        neuron_counts=(16,),
        acquisition_episodes=400,
        remap_episodes=400,
        learner=LearnerConfig(batch_size=16),
        task=TaskConfig(),
    )
    metrics, raw = run_seed(
        12,
        Scenario("smoke", 16, "generic_node_perturbation"),
        cfg,
    )
    assert metrics["pre_remap_alignment"] > 0.65
    assert metrics["post_remap_alignment"] > 0.65
    assert metrics["reconstruction_rmse"] < 1e-12
    assert metrics["legal_update_reconstruction_rmse"] < 1e-12
    assert raw["perturbation"].shape == (800, 3, 16)


def test_scenarios_are_unique_and_explicitly_non_grossberg() -> None:
    names = [scenario.name for scenario in scenario_suite(Exp005Config())]
    assert len(names) == len(set(names))
    assert all("grossberg" not in name for name in names)
