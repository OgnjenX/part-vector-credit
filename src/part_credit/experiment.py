"""Preregistered-style experiment runner and summary statistics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .model import ModelConfig, PARTModel
from .task import population_masks, sample_trial


@dataclass(frozen=True)
class ExperimentConfig:
    seeds: int = 30
    trials: int = 1200
    analysis_window: int = 300
    n_neurons: int = 10


CONDITIONS: dict[str, dict[str, bool]] = {
    "full": {},
    "no_motivated_attention": {"motivated_attention": False},
    "no_reset": {"reset_enabled": False},
    "no_working_memory": {"working_memory": False},
    "shuffled_feedback": {"shuffled_feedback": True},
    "explicit_vector_error_positive_control": {"explicit_vector_error": True},
    "high_vigilance_mismatch_stress": {},
}


def run_condition(name: str, cfg: ExperimentConfig) -> dict[str, Any]:
    options = CONDITIONS[name]
    seed_rows = []
    plus_mask, minus_mask = population_masks(cfg.n_neurons)
    for seed in range(cfg.seeds):
        rng = np.random.default_rng(seed)
        vigilance = 0.90 if name == "high_vigilance_mismatch_stress" else 0.72
        model = PARTModel(ModelConfig(n_neurons=cfg.n_neurons, vigilance=vigilance), rng)
        rows = []
        for trial in range(cfg.trials):
            soma, target = sample_trial(rng, cfg.n_neurons)
            row = model.trial(soma, target, **options)
            if trial >= cfg.trials - cfg.analysis_window:
                rows.append(row)
        rewards = np.array([r["reward"] for r in rows])
        apical = np.stack([r["apical"] for r in rows])
        targets = np.array([r["target_action"] for r in rows])
        # Task-related modulation: target-0 minus target-1 activity per population.
        delta = apical[targets == 0].mean(0) - apical[targets == 1].mean(0)
        plus_delta = float(delta[plus_mask].mean())
        minus_delta = float(delta[minus_mask].mean())
        seed_rows.append({
            "seed": seed,
            "accuracy": float(rewards.mean()),
            "p_plus_modulation": plus_delta,
            "p_minus_modulation": minus_delta,
            "opposition_index": plus_delta - minus_delta,
            "opposite_signs": bool(plus_delta * minus_delta < 0),
            "resonance_rate": float(np.mean([r["resonant"] for r in rows])),
            "reset_rate": float(np.mean([r["resets"] > 0 for r in rows])),
            "now_print_rate": float(np.mean([r["now_print"] for r in rows])),
        })
    return {
        "condition": name,
        "summary": {
            key: float(np.mean([row[key] for row in seed_rows]))
            for key in ("accuracy", "p_plus_modulation", "p_minus_modulation", "opposition_index", "opposite_signs", "resonance_rate", "reset_rate", "now_print_rate")
        },
        "seeds": seed_rows,
    }


def run_suite(cfg: ExperimentConfig) -> dict[str, Any]:
    return {
        "experiment": asdict(cfg),
        "conditions": {name: run_condition(name, cfg) for name in CONDITIONS},
        "decision_rule": {
            "learned": "mean late accuracy >= 0.70",
            "vectorized": "mean opposition index > 0 and opposite signs in >= 0.80 of seeds",
            "full_success": "both learned and vectorized in full condition",
        },
    }
