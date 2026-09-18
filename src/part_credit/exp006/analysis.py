"""Frozen-threshold classification for EXP006 result summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from .cli import FREEZE_PATH, _sha256


def _interval(values: list[float]) -> dict[str, float | int | None]:
    array = np.asarray(values, dtype=float)
    array = array[np.isfinite(array)]
    if not array.size:
        return {"n": 0, "mean": None, "ci95_low": None, "ci95_high": None}
    mean = float(np.mean(array))
    sem = float(np.std(array, ddof=1) / np.sqrt(array.size)) if array.size > 1 else 0.0
    return {
        "n": int(array.size),
        "mean": mean,
        "ci95_low": mean - 1.96 * sem,
        "ci95_high": mean + 1.96 * sem,
    }


def _metric_means(summary: dict[str, Any]) -> dict[str, dict[str, float]]:
    return {
        scenario: {
            key: float(value)
            for key, value in result["means"].items()
            if value is not None
        }
        for scenario, result in summary.items()
    }


def _passes(means: dict[str, float], floors: dict[str, float]) -> bool:
    return all(means.get(metric, float("-inf")) >= floor for metric, floor in floors.items())


def classify(summary: dict[str, Any], frozen: dict[str, Any]) -> dict[str, Any]:
    means = _metric_means(summary)
    floors = frozen["pass_floors"]
    intervals = {
        scenario: {
            key: _interval([row[key] for row in result["seeds"]])
            for key in result["means"]
        }
        for scenario, result in summary.items()
    }
    classifications: dict[str, dict[str, Any]] = {}
    for scenario in frozen["primary_models"]:
        scenario_means = means[scenario]
        behavior = _passes(scenario_means, floors["behavior"])
        topology = _passes(scenario_means, floors["topology"])
        francioni = _passes(scenario_means, floors["francioni_signature"])
        matched_counts = (
            scenario_means.get("matched_residual_samples_acquisition", 0.0),
            scenario_means.get("matched_residual_samples_remap", 0.0),
        )
        matched_identifiable = all(
            count >= floors["matched_soma"]["minimum_samples"]
            for count in matched_counts
        )
        matched_preserved = matched_identifiable and all(
            scenario_means.get(metric, float("-inf"))
            >= floors["matched_soma"]["minimum_score"]
            for metric in (
                "matched_residual_vectorization_acquisition",
                "matched_residual_vectorization_remap",
            )
        )
        classifications[scenario] = {
            "behavior": behavior,
            "topology": topology,
            "francioni_signature": francioni,
            "matched_soma_identifiable": matched_identifiable,
            "matched_soma_preserved": matched_preserved if matched_identifiable else None,
            "full_bridge": (
                behavior
                and topology
                and francioni
                and (matched_preserved if matched_identifiable else True)
            ),
        }

    control_pairs = frozen["control_comparisons"]
    controls: dict[str, Any] = {}
    for name, specification in control_pairs.items():
        primary = means[specification["primary"]]
        control = means[specification["control"]]
        effects = {
            metric: primary[metric] - control[metric]
            for metric in specification["minimum_effects"]
        }
        controls[name] = {
            "effects": effects,
            "pass": all(
                effects[metric] >= floor
                for metric, floor in specification["minimum_effects"].items()
            ),
        }

    full = [name for name, row in classifications.items() if row["full_bridge"]]
    ordinary_full = [name for name in full if name != "vector_oracle"]
    if ordinary_full:
        interpretation = "one_or_more_ordinary_models_passed_the_full_bridge"
    elif full == ["vector_oracle"]:
        interpretation = "only_the_privileged_vector_oracle_passed_the_full_bridge"
    else:
        interpretation = "even_the_vector_oracle_failed_the_full_bridge_sensitivity_check"
    return {
        "classification_rule": "scenario means compared with prospectively frozen floors",
        "classifications": classifications,
        "controls": controls,
        "interpretation": interpretation,
        "intervals": intervals,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("EXP006 classifications are append-only")
    frozen = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    summary_path = args.input / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    result = classify(summary, frozen)
    result["summary_sha256"] = _sha256(summary_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["classifications"], indent=2))


if __name__ == "__main__":
    main()
