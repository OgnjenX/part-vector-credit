"""Post hoc EXP000 audit: verify that aligned frozen templates solve the task."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from part_credit.model import ModelConfig, PARTModel
from part_credit.task import sample_trial


def main() -> None:
    rows = []
    for seed in range(30):
        rng = np.random.default_rng(seed)
        model = PARTModel(ModelConfig(category_lr=0.0, value_lr=0.0), rng)
        rewards = []
        for trial in range(1200):
            soma, target = sample_trial(rng, 10)
            result = model.trial(soma, target)
            if trial >= 900:
                rewards.append(float(result["reward"]))
        rows.append({"seed": seed, "late_accuracy": float(np.mean(rewards))})
    result = {
        "label": "EXP000 post hoc frozen-template reanalysis",
        "plasticity": {"category_lr": 0.0, "value_lr": 0.0},
        "mean_late_accuracy": float(np.mean([row["late_accuracy"] for row in rows])),
        "seeds": rows,
    }
    output = Path("results/exp000_frozen_reanalysis.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

