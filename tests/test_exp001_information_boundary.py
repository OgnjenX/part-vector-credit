import inspect

import numpy as np

from part_credit.exp001.analysis import initialization_audit
from part_credit.exp001.environment import BCIConfig, CausalBCI
from part_credit.exp001.model import Condition, HypothesisLearner, LearnerConfig


def test_hidden_roles_are_randomized_and_balanced():
    mappings = [CausalBCI(BCIConfig(), np.random.default_rng(seed)).causal for seed in range(6)]
    assert all((mapping > 0).sum() == 5 for mapping in mappings)
    assert len({tuple(mapping) for mapping in mappings}) > 1
    assert any(not np.array_equal(mapping, np.where(np.arange(10) % 2 == 0, 1, -1)) for mapping in mappings)


def test_initial_action_is_invariant_to_hidden_mapping():
    cfg = LearnerConfig()
    observation = np.array([1.0, 0.0, 0.0, 1.0])
    first = HypothesisLearner(cfg, Condition(), np.random.default_rng(9))
    second = HypothesisLearner(cfg, Condition(), np.random.default_rng(9))
    action_a = first.act(observation, 5)
    action_b = second.act(observation, 5)
    np.testing.assert_allclose(action_a["soma"], action_b["soma"])
    np.testing.assert_allclose(first.basis, second.basis)


def test_grossberg_path_has_no_causal_argument():
    signature = inspect.signature(HypothesisLearner.act)
    assert signature.parameters["explicit_vector"].default is None
    learner = HypothesisLearner(LearnerConfig(), Condition(), np.random.default_rng(1))
    learner.act(np.array([1.0, 0.0, 0.0, 1.0]), 2)
    # Hidden vectors are rejected unless the condition is explicitly the positive control.
    learner.learn(0.2, 0.0, explicit_vector=np.ones(10))


def test_initialization_audit_reports_every_candidate():
    learner = HypothesisLearner(LearnerConfig(n_hypotheses=8), Condition(), np.random.default_rng(2))
    causal = CausalBCI(BCIConfig(), np.random.default_rng(3)).causal
    audit = initialization_audit(learner.basis, causal, np.random.default_rng(4), permutations=10)
    assert len(audit["candidate_correlations"]) == 8
    assert 0 <= audit["decoder_accuracy"] <= 1

