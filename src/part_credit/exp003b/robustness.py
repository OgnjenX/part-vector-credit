"""Independent local-neighborhood check of the fixed EXP003a motif."""

from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

import numpy as np

from part_credit.exp003a.motif import MotifConfig, run_condition


def _case_summary(name: str, cfg: MotifConfig) -> dict[str, Any]:
    results = {
        condition: run_condition(condition, cfg)
        for condition in ("matched", "topdown_ablated", "mismatch")
    }
    matched = results["matched"]
    center = int(matched["center"])
    competitor = int(matched["competitor"])
    matched_delta = float(matched["weight_change"][center])
    competitor_delta = float(matched["weight_change"][competitor])
    ablated_delta = float(np.max(np.abs(results["topdown_ablated"]["weight_change"])))
    mismatch_delta = float(np.max(np.abs(results["mismatch"]["weight_change"])))
    advantage = matched_delta - competitor_delta
    return {
        "name": name,
        "config": asdict(cfg),
        "matched_delta_weight": matched_delta,
        "competitor_delta_weight": competitor_delta,
        "topdown_ablated_max_abs_delta_weight": ablated_delta,
        "mismatch_max_abs_delta_weight": mismatch_delta,
        "matched_minus_competitor": advantage,
        "matched_spikes": int(np.sum(matched["lower_spike_indices"] == center)),
        "competitor_spikes": int(np.sum(matched["lower_spike_indices"] == competitor)),
        "passes_qualitative_check": bool(
            matched_delta > competitor_delta
            and matched_delta > ablated_delta
            and matched_delta > mismatch_delta
        ),
    }


def run_robustness_check() -> dict[str, Any]:
    """Run one-factor-at-a-time ±10% checks, not a BCI parameter search."""

    base = MotifConfig()
    cases: list[tuple[str, MotifConfig]] = [("canonical", base)]
    for label, factor in (("low", 0.9), ("high", 1.1)):
        cases.append((f"feedforward_gain_{label}", replace(
            base, feedforward_gain=base.feedforward_gain * factor
        )))
        cases.append((f"topdown_gain_{label}", replace(
            base, topdown_gain=base.topdown_gain * factor
        )))
        cases.append((f"surround_gain_{label}", replace(
            base, surround_gain=base.surround_gain * factor
        )))
    cases.extend([
        ("topdown_lead_3.5ms", replace(base, topdown_at_ms=16.5)),
        ("topdown_lead_4.5ms", replace(base, topdown_at_ms=15.5)),
    ])
    rows = [_case_summary(name, cfg) for name, cfg in cases]
    return {
        "design": "one-factor-at-a-time canonical and modest +/-10% neighborhood",
        "selection_rule": "not used to optimize EXP003b; canonical parameters remain fixed",
        "cases": rows,
        "passed": sum(row["passes_qualitative_check"] for row in rows),
        "total": len(rows),
    }
