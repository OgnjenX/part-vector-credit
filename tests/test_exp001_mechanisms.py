import numpy as np

from part_credit.exp001.environment import BCIConfig, CausalBCI
from part_credit.exp001.model import Condition, HypothesisLearner, LearnerConfig

OBS_A = np.array([1.0, 0.0, 0.0, 1.0])
OBS_B = np.array([0.0, 1.0, 0.0, 1.0])


def test_frozen_network_does_not_update_values_or_basis():
    learner = HypothesisLearner(LearnerConfig(), Condition(plasticity=False), np.random.default_rng(1))
    before_basis = learner.basis.copy()
    learner.act(OBS_A, 3)
    learner.delay([np.zeros(4)] * 4)
    learner.learn(1.0, 1.0)
    np.testing.assert_allclose(learner.values, 0)
    np.testing.assert_allclose(learner.basis, before_basis)


def test_working_memory_retains_causal_hypothesis_across_distractors():
    learner = HypothesisLearner(LearnerConfig(), Condition(), np.random.default_rng(2))
    action = learner.act(OBS_A, 3)
    learner.delay([np.ones(4)] * 4)
    learner.learn(1.0, 1.0)
    assert learner.values[int(action["category"]), int(action["hypothesis"])] > 0


def test_uncommitted_category_is_recruited_after_mismatch():
    cfg = LearnerConfig(vigilance=0.95)
    learner = HypothesisLearner(cfg, Condition(), np.random.default_rng(3))
    learner.act(OBS_A, 2)
    second = learner.act(OBS_B, 2)
    assert learner.category_recruitments == 2
    assert second["resets"] >= 1


def test_apical_suppression_preserves_observation_but_removes_control_drive():
    normal = HypothesisLearner(LearnerConfig(), Condition(), np.random.default_rng(5))
    suppressed = HypothesisLearner(
        LearnerConfig(), Condition(apical_suppression=True), np.random.default_rng(5)
    )
    normal_action = normal.act(OBS_A, 20)
    suppressed_action = suppressed.act(OBS_A, 20)
    np.testing.assert_allclose(normal_action["passive_sensory"], suppressed_action["passive_sensory"])
    assert np.var(suppressed_action["apical"]) < np.var(normal_action["apical"])


def test_environment_control_is_mean_plus_minus_difference():
    env = CausalBCI(BCIConfig(action_frames=1, transition_noise=0), np.random.default_rng(7))
    soma = np.where(env.causal > 0, 1.0, 0.0)[None, :]
    outcome = env.execute(soma)
    assert outcome["states"][0] == 0.5

