"""Run EXP006 development simulations; confirmation remains protocol-gated."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import numpy as np

from .experiment import Exp006Config, run_scenario, scenario_suite

FREEZE_PATH = Path("experiments/exp006/FROZEN_PROTOCOL.json")


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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _save(results: dict[str, dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True)
    raw_dir = output / "raw"
    raw_dir.mkdir()
    summary = {}
    for name, result in results.items():
        summary[name] = _json_ready(result)
        arrays: dict[str, np.ndarray] = {}
        for row, seed_raw in zip(result["seeds"], result["_raw"], strict=True):
            prefix = f"seed_{int(row['seed'])}__"
            arrays.update({prefix + key: value for key, value in seed_raw.items()})
        np.savez_compressed(raw_dir / f"{name}.npz", **arrays)
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    manifest = {
        str(path.relative_to(output)): _sha256(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "SHA256SUMS.json"
    }
    (output / "SHA256SUMS.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def _load_and_validate_freeze(cfg: Exp006Config, population: str) -> dict[str, Any]:
    if not FREEZE_PATH.exists():
        raise SystemExit("EXP006 confirmation is forbidden until FROZEN_PROTOCOL.json exists")
    frozen = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    expected_config = _json_ready(asdict(cfg))
    frozen_config = dict(frozen["config"])
    if population == "secondary":
        frozen_config["task"]["n_neurons"] = cfg.task.n_neurons
    if frozen_config != expected_config:
        raise SystemExit("current EXP006 configuration differs from the frozen protocol")
    for relative, expected in frozen["source_sha256"].items():
        path = Path(relative)
        if not path.exists() or _sha256(path) != expected:
            raise SystemExit(f"source hash differs from frozen protocol: {relative}")
    if population == "secondary":
        primary = Path("results/exp006/frozen_v1_primary/classification.json")
        if not primary.exists():
            raise SystemExit("secondary confirmation requires the frozen primary classification")
    return frozen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("development", "confirmatory"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scenarios", nargs="*")
    parser.add_argument(
        "--population",
        choices=("primary", "secondary"),
        default="primary",
    )
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("EXP006 outputs are append-only")
    cfg = Exp006Config()
    if args.population == "secondary":
        cfg = replace(cfg, task=replace(cfg.task, n_neurons=8))
    available = {scenario.name: scenario for scenario in scenario_suite()}
    if args.phase == "confirmatory":
        if args.scenarios:
            raise SystemExit("confirmatory scenarios are fixed by FROZEN_PROTOCOL.json")
        frozen = _load_and_validate_freeze(cfg, args.population)
        names = tuple(frozen["scenario_order"])
        seeds = cfg.confirmatory_seeds
    else:
        names = tuple(args.scenarios) if args.scenarios else tuple(available)
        seeds = cfg.development_seeds
    unknown = sorted(set(names) - set(available))
    if unknown:
        raise SystemExit(f"unknown scenarios: {unknown}")
    results = {}
    for index, name in enumerate(names, start=1):
        print(f"[{index}/{len(names)}] {name}", flush=True)
        results[name] = run_scenario(available[name], cfg, seeds)
    _save(results, args.output)
    print(json.dumps({name: result["means"] for name, result in results.items()}, indent=2))


if __name__ == "__main__":
    main()
