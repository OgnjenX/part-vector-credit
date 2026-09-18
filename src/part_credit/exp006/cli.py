"""Run EXP006 development simulations; confirmation remains protocol-gated."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .experiment import Exp006Config, run_scenario, scenario_suite


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("development", "confirmatory"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scenarios", nargs="*")
    args = parser.parse_args()
    if args.phase == "confirmatory":
        raise SystemExit(
            "EXP006 confirmation is forbidden until FROZEN_PROTOCOL.json exists"
        )
    if args.output.exists():
        raise SystemExit("EXP006 outputs are append-only")
    cfg = Exp006Config()
    available = {scenario.name: scenario for scenario in scenario_suite()}
    names = tuple(args.scenarios) if args.scenarios else tuple(available)
    unknown = sorted(set(names) - set(available))
    if unknown:
        raise SystemExit(f"unknown scenarios: {unknown}")
    results = {}
    for index, name in enumerate(names, start=1):
        print(f"[{index}/{len(names)}] {name}", flush=True)
        results[name] = run_scenario(available[name], cfg, cfg.development_seeds)
    _save(results, args.output)
    print(json.dumps({name: result["means"] for name, result in results.items()}, indent=2))


if __name__ == "__main__":
    main()
