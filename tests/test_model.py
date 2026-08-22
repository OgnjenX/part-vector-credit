import numpy as np

from part_credit.experiment import ExperimentConfig, run_condition
from part_credit.model import ModelConfig, PARTModel


def test_reward_is_scalar_and_apical_has_neuron_shape():
    model = PARTModel(ModelConfig(), np.random.default_rng(1))
    row = model.trial(np.linspace(0.1, 0.9, 10), target_action=0)
    assert isinstance(row["reward"], float)
    assert row["apical"].shape == (10,)


def test_small_run_is_deterministic():
    cfg = ExperimentConfig(seeds=2, trials=40, analysis_window=20)
    assert run_condition("full", cfg) == run_condition("full", cfg)


def test_shuffled_feedback_is_an_ablation():
    cfg = ExperimentConfig(seeds=3, trials=100, analysis_window=40)
    full = run_condition("full", cfg)["summary"]["opposition_index"]
    shuffled = run_condition("shuffled_feedback", cfg)["summary"]["opposition_index"]
    assert full > shuffled

