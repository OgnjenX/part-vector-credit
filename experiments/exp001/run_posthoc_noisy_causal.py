"""Post-confirmatory exploratory probe for heterogeneous hidden causal weights."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from part_credit.exp001.experiment import Exp001Config, run_condition


def main() -> None:
    cfg = Exp001Config()
    cfg = replace(
        cfg,
        environment=replace(cfg.environment, causal_weight_noise=0.35),
    )
    result = run_condition(
        "grossberg_inspired_full",
        cfg,
        cfg.development_seeds,
        detailed_raw=True,
    )
    raw = result.pop("_raw")
    neural = result.pop("_raw_neural")
    output = Path("results/exp001/posthoc_noisy_causal_development")
    output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    np.savez_compressed(
        output.with_name(output.name + "_raw.npz"),
        scalar=raw,
        neural=neural,
    )
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

