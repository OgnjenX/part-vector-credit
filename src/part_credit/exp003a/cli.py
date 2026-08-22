"""Run and save the EXP003a mechanism-validation checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from .experiment import run_suite, save_figures


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _json_ready(value.tolist())
    if isinstance(value, np.generic):
        return _json_ready(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items() if key != "_raw"}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("EXP003a output path already exists; failures/results are append-only")
    suite = run_suite()
    args.output.mkdir(parents=True)
    raw_dir = args.output / "raw"
    raw_dir.mkdir()
    for condition, result in suite["_raw"].items():
        arrays = {
            key: value
            for key, value in result.items()
            if isinstance(value, np.ndarray)
        }
        np.savez_compressed(raw_dir / f"{condition}.npz", **arrays)
        for probe_name in ("before_probe", "after_probe"):
            np.savez_compressed(
                raw_dir / f"{condition}_{probe_name}.npz",
                **result[probe_name],
            )
    with (args.output / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(_json_ready(suite), handle, indent=2)
    save_figures(suite, args.output / "figures")
    print(json.dumps(_json_ready(suite["classification"]), indent=2))


if __name__ == "__main__":
    main()
