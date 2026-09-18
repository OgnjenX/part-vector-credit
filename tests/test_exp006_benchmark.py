from __future__ import annotations

import inspect

import numpy as np

from part_credit.exp006.environment import (
    FrancioniBCI,
    FrancioniTaskConfig,
    balanced_role,
    independent_remap,
)
from part_credit.exp006.experiment import Exp006Config, Scenario, run_seed, scenario_suite
from part_credit.exp006.model import (
    ARTRepertoireLearner,
    Condition,
    HybridLearner,
    LearnerConfig,
    LocalEligibilityLearner,
    VectorOracle,
    random_balanced_repertoire,
)
from part_credit.exp006.observation import ObservationConfig, simulate_residuals


def test_environment_uses_opposite_hidden_roles_and_binned_feedback() -> None:
    cfg = FrancioniTaskConfig(n_neurons=10, max_frames=4, state_gain=0.2)
    role = np.r_[np.ones(5), -np.ones(5)]
    env = FrancioniBCI(cfg, role)
    env.reset()
    aligned = np.r_[np.full(5, 0.8), np.full(5, 0.2)]
    transition = env.step(aligned)
    assert transition["drive"] > 0.0
    assert transition["state_after"] > transition["state_before"]
    assert transition["displayed_after"] in np.linspace(0.0, 1.0, 7)


def test_roles_are_balanced_and_remap_is_nontrivial() -> None:
    rng = np.random.default_rng(2)
    role = balanced_role(rng, 10)
    remap = independent_remap(rng, role)
    assert role.sum() == 0.0
    assert remap.sum() == 0.0
    assert 0.2 <= np.mean(role != remap) <= 0.8


def test_repertoire_is_balanced_antithetic_and_hidden_role_independent() -> None:
    bank = random_balanced_repertoire(
        np.random.default_rng(3),
        n_neurons=10,
        size=64,
        amplitude=0.2,
    )
    np.testing.assert_allclose(bank.mean(axis=1), 0.5)
    centered = bank - 0.5
    assert len({row.tobytes() for row in centered}) == 64
    assert all(any(np.allclose(-row, other) for other in centered) for row in centered)


def test_hidden_role_is_accepted_only_by_vector_oracle() -> None:
    ordinary = (
        ARTRepertoireLearner.__init__,
        LocalEligibilityLearner.__init__,
        HybridLearner.__init__,
    )
    forbidden = {"role", "hidden_role", "causal_role", "target_vector"}
    for method in ordinary:
        assert set(inspect.signature(method).parameters).isdisjoint(forbidden)
    assert "role" in inspect.signature(VectorOracle.__init__).parameters


def test_observation_layer_removes_linear_somatic_component() -> None:
    rng = np.random.default_rng(4)
    soma = rng.normal(0.5, 0.1, (12, 4, 10))
    feedback = rng.normal(0.0, 1.0, soma.shape)
    valid = np.ones(soma.shape[:2], dtype=bool)
    post_soma = rng.normal(0.5, 0.1, (12, 10))
    post_feedback = rng.normal(0.0, 1.0, (12, 10))
    result = simulate_residuals(
        soma=soma,
        feedback=feedback,
        valid_mask=valid,
        post_soma=post_soma,
        post_feedback=post_feedback,
        cfg=ObservationConfig(noise_sd=0.0),
        rng=np.random.default_rng(5),
    )
    for neuron in range(10):
        corr = np.corrcoef(
            soma[..., neuron].ravel(), result["residual"][..., neuron].ravel()
        )[0, 1]
        assert abs(corr) < 1e-10


def test_small_vector_run_learns_both_mappings_deterministically() -> None:
    cfg = Exp006Config(
        development_seeds=(11,),
        trials_per_block=8,
        acquisition_blocks=2,
        remap_blocks=2,
        task=FrancioniTaskConfig(n_neurons=10, max_frames=12, state_gain=0.18),
        learner=LearnerConfig(repertoire_size=32, oracle_lr=0.25),
    )
    scenario = Scenario("vector", "vector", Condition("vector"))
    first_metrics, first_raw = run_seed(11, scenario, cfg)
    second_metrics, second_raw = run_seed(11, scenario, cfg)
    for key, first in first_metrics.items():
        second = second_metrics[key]
        if isinstance(first, float) and np.isnan(first):
            assert np.isnan(second)
        else:
            assert first == second
    assert first_metrics["pre_remap_alignment"] > 0.95
    assert first_metrics["post_remap_alignment"] > 0.95
    np.testing.assert_array_equal(first_raw["success"], second_raw["success"])


def test_scenario_names_are_unique() -> None:
    names = [scenario.name for scenario in scenario_suite()]
    assert len(names) == len(set(names))


def test_hybrid_archives_unscaled_components_and_combines_each_once() -> None:
    cfg = LearnerConfig(repertoire_size=32)
    bank = random_balanced_repertoire(
        np.random.default_rng(6),
        n_neurons=10,
        size=cfg.repertoire_size,
        amplitude=cfg.motor_amplitude,
    )
    learner = HybridLearner(
        bank,
        cfg,
        Condition("hybrid"),
        np.random.default_rng(7),
        np.random.default_rng(8),
    )
    learner.start_trial()
    action = learner.act(np.asarray([0.0, 0.0, 0.5]), 0.0)
    combined = learner.observe_transition(action, 1.0)
    np.testing.assert_allclose(
        combined,
        cfg.hybrid_art_gain * action.metadata["feedback_art"]
        + cfg.hybrid_eligibility_gain * action.metadata["feedback_eligibility"],
    )


def test_shuffled_modulator_uses_only_prior_history() -> None:
    cfg = LearnerConfig(repertoire_size=32)
    bank = random_balanced_repertoire(
        np.random.default_rng(9),
        n_neurons=10,
        size=cfg.repertoire_size,
        amplitude=cfg.motor_amplitude,
    )
    learner = ARTRepertoireLearner(
        bank,
        cfg,
        Condition("shuffled", shuffle_modulators=True),
        np.random.default_rng(10),
    )
    assert learner.art._assigned_modulator(3.0) == 0.0
    assert learner.art._assigned_modulator(-4.0) == 3.0
