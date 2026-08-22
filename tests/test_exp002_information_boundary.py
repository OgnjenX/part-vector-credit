import inspect

import numpy as np

from part_credit.exp002.analysis import initialization_audit
from part_credit.exp002.environment import BCIConfig, StepwiseCausalBCI
from part_credit.exp002.model import Condition, Exp002Controller, LearnerConfig


def test_stepwise_action_changes_next_visible_state() -> None:
    cfg = BCIConfig(n_neurons=10, transition_noise=0.0)
    environment = StepwiseCausalBCI(cfg, np.random.default_rng(1))
    environment.reset(context=0)
    causal = environment.active_causal()
    helpful = np.where(causal > 0, 1.0, 0.0)
    before = environment.state
    transition = environment.step(helpful)
    assert transition["state"] > before
    assert np.argmax(np.asarray(transition["observation"])[2:9]) == transition["state_bin"]


def test_hidden_roles_are_not_controller_inputs_or_attributes() -> None:
    source = inspect.getsource(Exp002Controller)
    assert "active_causal_for_positive_control" in source
    controller = Exp002Controller(
        LearnerConfig(), Condition(), np.random.default_rng(2)
    )
    assert not hasattr(controller, "causal")
    assert not hasattr(controller, "p_plus")


def test_motor_and_topdown_initializations_are_independent() -> None:
    controller = Exp002Controller(
        LearnerConfig(), Condition(), np.random.default_rng(3)
    )
    row_correlations = [
        np.corrcoef(motor, topdown)[0, 1]
        for motor, topdown in zip(controller.motor_basis, controller.topdown, strict=True)
    ]
    assert abs(float(np.mean(row_correlations))) < 0.20
    assert not np.allclose(controller.motor_basis, controller.topdown)


def test_permutation_audit_reports_every_candidate() -> None:
    rng = np.random.default_rng(4)
    patterns = rng.normal(size=(17, 10))
    causal = rng.permutation(np.r_[np.ones(5), -np.ones(5)])
    audit = initialization_audit(patterns, causal, rng, permutations=20)
    assert len(audit["candidate_correlations"]) == 17
    assert 0.0 <= audit["decoder_permutation_p"] <= 1.0
