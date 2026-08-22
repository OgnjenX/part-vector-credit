"""Deterministic seed-bootstrap confidence intervals for EXP001 confirmation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def interval(values: np.ndarray, rng: np.random.Generator) -> dict[str, float]:
    draws = rng.choice(values, (10_000, len(values)), replace=True).mean(1)
    return {
        "mean": float(values.mean()),
        "bootstrap_95_low": float(np.quantile(draws, 0.025)),
        "bootstrap_95_high": float(np.quantile(draws, 0.975)),
    }


def main() -> None:
    source = Path("results/exp001/frozen_v1/exp001_confirmatory.json")
    data = json.loads(source.read_text())["primary"]["conditions"]
    rng = np.random.default_rng(20260822)
    keys = (
        "pre_remap_late_success",
        "post_remap_late_success",
        "post_dendritic_role_alignment",
        "post_opposite_population_signs",
        "post_residual_predicts_later_soma",
        "selected_post_basis_alignment",
    )
    full_rows = data["grossberg_inspired_full"]["seeds"]
    output: dict[str, object] = {
        "method": "10,000 seed-level nonparametric bootstrap draws; deterministic seed 20260822",
        "full": {
            key: interval(np.array([row[key] for row in full_rows]), rng) for key in keys
        },
        "paired_post_remap_success_effects": {},
    }
    for comparison in (
        "frozen_zero_plasticity",
        "random_policy_feedback",
        "no_structural_credit",
        "no_working_memory",
        "no_now_print_gating",
        "shuffled_top_down_feedback",
        "apical_pathway_suppressed",
    ):
        comparison_rows = data[comparison]["seeds"]
        differences = np.array([
            full["post_remap_late_success"] - control["post_remap_late_success"]
            for full, control in zip(full_rows, comparison_rows, strict=True)
        ])
        output["paired_post_remap_success_effects"][comparison] = interval(differences, rng)
    target = Path("results/exp001/frozen_v1/exp001_confirmatory_statistics.json")
    target.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

