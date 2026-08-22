"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .experiment import ExperimentConfig, run_suite


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--trials", type=int, default=1200)
    parser.add_argument("--output", type=Path, default=Path("results/initial_experiment.json"))
    args = parser.parse_args()
    result = run_suite(ExperimentConfig(seeds=args.seeds, trials=args.trials))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")

    names = list(result["conditions"])
    summaries = [result["conditions"][n]["summary"] for n in names]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].bar(names, [x["accuracy"] for x in summaries])
    axes[0].axhline(0.7, color="black", linestyle="--", linewidth=1)
    axes[0].set_ylabel("late-task accuracy")
    axes[1].bar(names, [x["p_plus_modulation"] for x in summaries], label="P+")
    axes[1].bar(names, [x["p_minus_modulation"] for x in summaries], alpha=0.75, label="P-")
    axes[1].axhline(0, color="black", linewidth=1)
    axes[1].set_ylabel("target 0 - target 1 apical modulation")
    axes[1].legend()
    for ax in axes:
        ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(args.output.with_suffix(".png"), dpi=180)
    print(json.dumps({n: result["conditions"][n]["summary"] for n in names}, indent=2))


if __name__ == "__main__":
    main()
