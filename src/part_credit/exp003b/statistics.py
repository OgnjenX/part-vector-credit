"""Frozen paired-seed statistics and A/B/C/D/E classifier for EXP003b."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from .analysis import bootstrap_mean_ci

LONGITUDINAL_KEYS = (
    "pre_d_to_w",
    "pre_d_to_s",
    "post_d_to_w",
    "post_d_to_s",
)


def _seed_values(suite: Mapping[str, Any], condition: str, key: str) -> np.ndarray:
    return np.asarray([
        float(row[key]) for row in suite["conditions"][condition]["seeds"]
    ])


def _paired(
    suite: Mapping[str, Any], left: str, right: str, key: str
) -> dict[str, object]:
    difference = _seed_values(suite, left, key) - _seed_values(suite, right, key)
    ci = bootstrap_mean_ci(difference, np.random.default_rng(90303))
    return {"mean": float(difference.mean()), "ci95": list(ci)}


def analyze_suite(suite: Mapping[str, Any]) -> dict[str, Any]:
    primary = suite["conditions"]["primary_part_t_smart"]["summary"]
    frozen = suite["conditions"]["frozen_no_learning"]["summary"]
    random = suite["conditions"]["random_controller"]["summary"]
    expression = suite["conditions"][
        "primary_post_learning_apical_suppressed"
    ]["summary"]
    generic = suite["conditions"]["bandit_generic_hebb"]["summary"]
    vector = suite["conditions"][
        "explicit_vector_credit_positive_control"
    ]["summary"]

    comparisons: dict[str, object] = {}
    for period in ("pre_remap_evaluation_success", "post_remap_evaluation_success"):
        comparisons[f"primary_minus_frozen_{period}"] = _paired(
            suite, "primary_part_t_smart", "frozen_no_learning", period
        )
        comparisons[f"primary_minus_random_{period}"] = _paired(
            suite, "primary_part_t_smart", "random_controller", period
        )
    for key in LONGITUDINAL_KEYS:
        comparisons[f"primary_minus_blocked_{key}"] = _paired(
            suite, "primary_part_t_smart", "primary_t_to_smart_blocked", key
        )
        comparisons[f"primary_minus_generic_{key}"] = _paired(
            suite, "primary_part_t_smart", "bandit_generic_hebb", key
        )

    initial_topdown = abs(float(primary["initial_topdown_mean_signed_correlation"]))
    criteria = {
        "behavior_pre": all(
            comparisons[f"primary_minus_{control}_pre_remap_evaluation_success"]["mean"]
            >= 0.10
            and comparisons[
                f"primary_minus_{control}_pre_remap_evaluation_success"
            ]["ci95"][0] > 0.0
            for control in ("frozen", "random")
        ),
        "behavior_post": all(
            comparisons[f"primary_minus_{control}_post_remap_evaluation_success"]["mean"]
            >= 0.10
            and comparisons[
                f"primary_minus_{control}_post_remap_evaluation_success"
            ]["ci95"][0] > 0.0
            for control in ("frozen", "random")
        ),
        "no_initial_vector": (
            abs(float(primary["initial_motor_mean_signed_correlation"])) < 0.05
            and initial_topdown < 0.05
            and abs(float(primary["initial_lower_weight_mean_signed_correlation"]))
            < 0.05
            and abs(
                float(primary["initial_motor_decoder_accuracy"])
                - float(primary["initial_motor_decoder_null_mean"])
            ) <= 0.15
            and abs(
                float(primary["initial_topdown_decoder_accuracy"])
                - float(primary["initial_topdown_decoder_null_mean"])
            ) <= 0.15
        ),
        "expectation_emergence_pre": (
            float(primary["pre_topdown_alignment"]) - initial_topdown >= 0.20
        ),
        "expectation_emergence_post": (
            float(primary["post_topdown_alignment"]) - initial_topdown >= 0.20
        ),
        "longitudinal_chain": all(
            float(primary[key]) >= 0.20
            and float(primary[f"{key}_ci95"][0]) > 0.0
            for key in LONGITUDINAL_KEYS
        ),
        "t_to_smart_specificity": all(
            comparisons[f"primary_minus_blocked_{key}"]["mean"] >= 0.15
            and comparisons[f"primary_minus_blocked_{key}"]["ci95"][0] > 0.0
            for key in LONGITUDINAL_KEYS
        ),
        "topdown_changes_timing": (
            float(primary["topdown_created_spike_fraction"]) > 0.0
            or float(primary["topdown_latency_advance_ms"]) > 0.0
        ),
        "expression_separation": all(
            abs(
                float(primary[key]) - float(expression[key])
            ) <= 0.05
            for key in (
                "pre_remap_evaluation_success",
                "post_remap_evaluation_success",
            )
        ),
        "remap_reorganization": (
            float(primary["post_topdown_alignment"])
            - float(primary["old_topdown_new_alignment"]) >= 0.20
        ),
        "context_opposition": float(primary["context_topdown_opposition"]) >= 0.25,
        "positive_control_valid": (
            float(vector["pre_remap_evaluation_success"]) >= 0.80
            and float(vector["post_remap_evaluation_success"]) >= 0.80
            and all(
                float(vector[key]) >= 0.20
                and float(vector[f"{key}_ci95"][0]) > 0.0
                for key in LONGITUDINAL_KEYS
            )
        ),
    }
    generic_full_chain = (
        float(generic["pre_remap_evaluation_success"]) - max(
            float(frozen["pre_remap_evaluation_success"]),
            float(random["pre_remap_evaluation_success"]),
        ) >= 0.10
        and float(generic["post_remap_evaluation_success"]) - max(
            float(frozen["post_remap_evaluation_success"]),
            float(random["post_remap_evaluation_success"]),
        ) >= 0.10
        and all(float(generic[key]) >= 0.20 for key in LONGITUDINAL_KEYS)
    )
    criteria["generic_full_chain"] = generic_full_chain
    primary_behavior = criteria["behavior_pre"] and criteria["behavior_post"]
    strong = all(
        criteria[key]
        for key in (
            "behavior_pre",
            "behavior_post",
            "no_initial_vector",
            "expectation_emergence_pre",
            "expectation_emergence_post",
            "longitudinal_chain",
            "t_to_smart_specificity",
            "topdown_changes_timing",
            "expression_separation",
            "remap_reorganization",
            "context_opposition",
            "positive_control_valid",
        )
    ) and not generic_full_chain
    if not criteria["positive_control_valid"]:
        outcome = "E_NON_DIAGNOSTIC"
    elif generic_full_chain:
        outcome = "B_GENERIC_LOCAL_FEEDBACK_SUFFICIENT"
    elif strong:
        outcome = "A_STRONG_GROSSBERGIAN_SUPPORT"
    elif primary_behavior and not criteria["longitudinal_chain"]:
        outcome = "C_COMPOSITION_FAILS_LONGITUDINAL_CHAIN"
    else:
        outcome = "E_NON_DISCRIMINATING"
    return {
        "outcome": outcome,
        "criteria": criteria,
        "paired_comparisons": comparisons,
        "notes": {
            "within_hypothesis": True,
            "primary_dendritic_phase_index": 1,
            "positive_control_phase_index": 3,
            "phase_names": [
                "category_selection",
                "pre_action_expectation",
                "action_execution",
                "sensory_feedback",
                "outcome",
                "post_outcome",
            ],
        },
    }
