import numpy as np

from part_credit.exp002.model import Condition, Exp002Controller, LearnerConfig


def _observation() -> np.ndarray:
    observation = np.zeros(16)
    observation[0] = 1.0
    observation[2] = 1.0
    observation[-1] = 1.0
    return observation


def _one_trace(controller: Exp002Controller, *, evaluating: bool = False) -> dict[str, object]:
    controller.start_episode()
    return controller.select(
        _observation(), context=0, state_bin=0, progress=0.0, evaluating=evaluating
    )


def test_outstar_expectancy_update_is_local_and_nonzero() -> None:
    controller = Exp002Controller(
        LearnerConfig(), Condition(), np.random.default_rng(10)
    )
    _one_trace(controller)
    before = controller.topdown.copy()
    strength = controller.delay([np.zeros(2) for _ in range(3)])
    controller.learn(
        global_improvement=0.7,
        reward=1.0,
        wm_strength=strength,
        active_causal_for_positive_control=None,
    )
    assert np.linalg.norm(controller.topdown - before) > 0


def test_suppressed_apical_learning_leaves_topdown_unchanged() -> None:
    controller = Exp002Controller(
        LearnerConfig(),
        Condition(suppress_apical_learning=True),
        np.random.default_rng(11),
    )
    _one_trace(controller)
    before = controller.topdown.copy()
    controller.learn(
        global_improvement=0.8,
        reward=1.0,
        wm_strength=1.0,
        active_causal_for_positive_control=None,
    )
    assert np.array_equal(controller.topdown, before)


def test_corrected_plastic_basis_probe_is_not_exp001_noop() -> None:
    controller = Exp002Controller(
        LearnerConfig(), Condition(plastic_basis=True), np.random.default_rng(12)
    )
    _one_trace(controller)
    before = controller.motor_basis.copy()
    controller.learn(
        global_improvement=0.8,
        reward=1.0,
        wm_strength=1.0,
        active_causal_for_positive_control=None,
    )
    assert np.linalg.norm(controller.motor_basis - before) > 0


def test_expression_suppression_does_not_change_motor_output() -> None:
    cfg = LearnerConfig()
    normal = Exp002Controller(cfg, Condition(), np.random.default_rng(13))
    suppressed = Exp002Controller(
        cfg, Condition(suppress_apical_expression=True), np.random.default_rng(13)
    )
    normal_action = _one_trace(normal, evaluating=True)
    suppressed_action = _one_trace(suppressed, evaluating=True)
    assert np.array_equal(normal_action["soma"], suppressed_action["soma"])
    assert np.linalg.norm(normal_action["topdown_pattern"]) > 0
    assert np.linalg.norm(suppressed_action["topdown_pattern"]) == 0


def test_direct_copy_baseline_has_no_learned_topdown_weights() -> None:
    controller = Exp002Controller(
        LearnerConfig(),
        Condition(algorithm="bandit", topdown="copy"),
        np.random.default_rng(14),
    )
    action = _one_trace(controller)
    assert np.allclose(action["topdown_pattern"], action["motor_pattern"])
    before = controller.topdown.copy()
    controller.learn(
        global_improvement=0.5,
        reward=0.0,
        wm_strength=1.0,
        active_causal_for_positive_control=None,
    )
    assert np.array_equal(controller.topdown, before)


def test_vector_control_is_the_only_condition_that_requires_hidden_roles() -> None:
    controller = Exp002Controller(
        LearnerConfig(),
        Condition(algorithm="bandit", topdown="vector", explicit_vector_error=True),
        np.random.default_rng(15),
    )
    _one_trace(controller)
    try:
        controller.learn(
            global_improvement=0.5,
            reward=0.0,
            wm_strength=1.0,
            active_causal_for_positive_control=None,
        )
    except ValueError as error:
        assert "hidden causal roles" in str(error)
    else:
        raise AssertionError("positive control accepted a missing hidden vector")
