from __future__ import annotations

import inspect

import numpy as np

from part_credit.exp004.banks import (
    COVERAGE_TARGETS,
    balanced_role,
    composition_bank,
    controlled_coverage_bank,
    random_nested_bank,
)
from part_credit.exp004.environment import TopologyTaskConfig
from part_credit.exp004.experiment import Exp004Config, Scenario, run_seed, scenario_suite
from part_credit.exp004.model import (
    TopologyCondition,
    TopologyController,
    TopologyLearnerConfig,
)
from part_credit.exp004.oracles import coverage_metrics, repertoire_oracles


def _controller(condition: TopologyCondition | None = None) -> TopologyController:
    task = TopologyTaskConfig(n_neurons=8, action_noise=0.0)
    bank = np.stack([
        np.r_[np.full(4, 0.65), np.full(4, 0.35)],
        np.r_[np.full(4, 0.35), np.full(4, 0.65)],
    ])
    return TopologyController(
        learner_cfg=TopologyLearnerConfig(max_categories=16),
        task_cfg=task,
        condition=condition or TopologyCondition(),
        motor_bank=bank,
        rng=np.random.default_rng(1),
    )


def test_random_banks_are_nested_and_antithetic() -> None:
    args = {
        "n_neurons": 32,
        "max_hypotheses": 128,
        "amplitude": 0.15,
    }
    small = random_nested_bank(
        np.random.default_rng(2), n_hypotheses=8, **args
    )
    large = random_nested_bank(
        np.random.default_rng(2), n_hypotheses=16, **args
    )
    np.testing.assert_array_equal(small.patterns, large.patterns[:8])
    for pair in range(0, 8, 2):
        np.testing.assert_array_equal(
            small.patterns[pair] - 0.5, -(small.patterns[pair + 1] - 0.5)
        )


def test_controlled_banks_hit_coverage_without_norm_cue() -> None:
    role = balanced_role(np.random.default_rng(3), 32)
    norms = []
    for index, label in enumerate(("low", "medium", "high")):
        bank = controlled_coverage_bank(
            np.random.default_rng(10 + index),
            role,
            n_hypotheses=16,
            coverage=label,
            amplitude=0.15,
        )
        metrics = coverage_metrics(bank.patterns, role)
        assert np.isclose(metrics["A_single"], COVERAGE_TARGETS[label])
        assert np.allclose(bank.patterns.mean(axis=1), 0.5)
        norms.append(np.linalg.norm(bank.patterns, axis=1))
    np.testing.assert_allclose(norms[0], norms[1])
    np.testing.assert_allclose(norms[1], norms[2])


def test_composition_bank_is_low_single_but_sequence_solvable() -> None:
    cfg = TopologyTaskConfig(n_neurons=32, action_noise=0.0)
    role = balanced_role(np.random.default_rng(4), 32)
    rng = np.random.default_rng(5)
    for _ in range(100):
        bank = composition_bank(
            rng,
            role,
            n_hypotheses=16,
            action_frames=cfg.action_frames,
            amplitude=0.15,
        )
        oracle = repertoire_oracles(bank.patterns, role, cfg, bank.phase_masks)
        if oracle["allowed_sequence_advantage"] >= 0.20:
            break
    else:
        raise AssertionError("no preregisterable composition bank was generated")
    metrics = coverage_metrics(bank.patterns, role)
    assert metrics["A_single"] <= 0.25 + 1e-12
    assert oracle["best_allowed_sequence"]["success"] == 1.0
    assert oracle["allowed_sequence_advantage"] > 0.0


def test_art_recruits_and_modifies_categories_without_changing_motor_bank() -> None:
    controller = _controller()
    initial_motor = controller.motor_basis.copy()
    first = controller.select(
        np.asarray([1.0, 0.0, 0.0, 0.0]),
        context=0,
        frame=0,
        state_bin=0,
        progress=0.0,
        evaluating=False,
        episode=0,
    )
    assert controller.recruitments == 1
    second = controller.select(
        np.asarray([1.0, 0.0, 0.0, 0.1]),
        context=0,
        frame=0,
        state_bin=0,
        progress=0.1,
        evaluating=False,
        episode=1,
    )
    assert controller.modifications >= 1
    controller.start_episode()
    controller.record_frame(
        second,
        soma=np.asarray(second["motor"]),
        perturbation=np.zeros(8),
        context=0,
        episode=1,
        frame=0,
    )
    controller.learn_outcome(outcome=1.0)
    np.testing.assert_array_equal(controller.motor_basis, initial_motor)
    assert first["category"] == second["category"]


def test_outstar_update_is_convex_and_reconstructible() -> None:
    controller = _controller()
    selected = controller.select(
        np.asarray([1.0, 0.0, 0.0, 0.0]),
        context=0,
        frame=0,
        state_bin=0,
        progress=0.0,
        evaluating=False,
        episode=0,
    )
    controller.start_episode()
    soma = np.asarray(selected["motor"])
    target = soma - soma.mean()
    controller.record_frame(
        selected,
        soma=soma,
        perturbation=np.zeros(8),
        context=0,
        episode=0,
        frame=0,
    )
    controller.learn_outcome(outcome=1.0)
    update = controller.topdown_updates[0]
    assert 0.0 <= update["eta_eff"] <= 1.0
    expected = update["eta_eff"] * target
    np.testing.assert_allclose(update["after"], expected)


def test_primary_information_boundary_has_no_hidden_role_input() -> None:
    for method in (
        TopologyController.select,
        TopologyController.record_frame,
    ):
        parameters = set(inspect.signature(method).parameters)
        assert parameters.isdisjoint({"role", "causal", "coverage", "oracle"})
    condition = TopologyCondition()
    assert not condition.explicit_vector_control


def test_small_exp004_run_preserves_reachability() -> None:
    cfg = Exp004Config(
        development_seeds=(11,),
        fixed_training_episodes=12,
        evaluation_episodes=4,
        controlled_bank_size=16,
        task=TopologyTaskConfig(n_neurons=32, action_noise=0.005),
    )
    scenario = Scenario(
        name="smoke",
        family="controlled",
        n_hypotheses=16,
        experience_regime="fixed",
        condition="primary_art_outstar",
        coverage="medium",
    )
    metrics, raw = run_seed(11, scenario, cfg)
    assert metrics["best_allowed_success"] == 1.0
    assert metrics["reconstruction_rmse"] < 1e-12
    assert metrics["motor_basis_change_norm"] == 0.0
    assert raw["topdown_update_eta_eff"].max() < 1.0


def test_scenario_names_are_unique() -> None:
    names = [scenario.name for scenario in scenario_suite(Exp004Config())]
    assert len(names) == len(set(names))
