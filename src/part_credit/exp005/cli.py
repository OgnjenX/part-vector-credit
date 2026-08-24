"""Run the EXP005 generic diagnostic; no Grossberg-primary run exists."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .experiment import Exp005Config, run_scenario, scenario_suite
from .figures import save_figures
from .statistics import analyze_results

SOURCE_PATHS = (
    "src/part_credit/exp005/__init__.py",
    "src/part_credit/exp005/model.py",
    "src/part_credit/exp005/experiment.py",
    "src/part_credit/exp005/statistics.py",
    "src/part_credit/exp005/figures.py",
    "src/part_credit/exp005/cli.py",
    "tests/test_exp005_generic.py",
    "pyproject.toml",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items() if key != "_raw"}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def save_results(results: dict[str, dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True)
    raw_dir = output / "raw"
    raw_dir.mkdir()
    summary = {}
    for name, result in results.items():
        summary[name] = json_ready(result)
        arrays: dict[str, np.ndarray] = {}
        for row, seed_raw in zip(result["seeds"], result["_raw"], strict=True):
            prefix = f"seed_{int(row['seed'])}__"
            arrays.update({prefix + key: value for key, value in seed_raw.items()})
        np.savez_compressed(raw_dir / f"{name}.npz", **arrays)
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    required = {scenario.name for scenario in scenario_suite(Exp005Config())}
    complete = required.issubset(results)
    statistics = (
        analyze_results(results)
        if complete
        else {"status": "incomplete development subset", "scenario_count": len(results)}
    )
    (output / "statistics.json").write_text(
        json.dumps(json_ready(statistics), indent=2), encoding="utf-8"
    )
    if complete:
        save_figures(results, output / "figures")
    manifest = {
        str(path.relative_to(output)): sha256(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "SHA256SUMS.json"
    }
    (output / "SHA256SUMS.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def validate_confirmation(
    cfg: Exp005Config, names: tuple[str, ...], output: Path
) -> tuple[int, ...]:
    protocol_path = Path("experiments/exp005/FROZEN_PROTOCOL.json")
    if not protocol_path.exists():
        raise SystemExit("diagnostic confirmation blocked: frozen protocol absent")
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("status") != "frozen":
        raise SystemExit("diagnostic confirmation blocked: protocol is not frozen")
    if protocol.get("grossberg_primary_run_permitted") is not False:
        raise SystemExit("source-gate declaration is missing")
    if protocol.get("held_out_touched") is not False:
        raise SystemExit("held-out state is not pristine")
    if str(output) != protocol["confirmation_output"]:
        raise SystemExit("confirmation output differs from frozen protocol")
    if list(cfg.confirmatory_seeds) != protocol["confirmatory_seeds"]:
        raise SystemExit("confirmation seeds differ from frozen protocol")
    if list(names) != protocol["scenario_names"]:
        raise SystemExit("scenario suite differs from frozen protocol")
    for relative, expected in protocol["source_sha256"].items():
        if sha256(Path(relative)) != expected:
            raise SystemExit(f"source hash mismatch: {relative}")
    return cfg.confirmatory_seeds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("development", "confirmatory"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scenarios", nargs="*")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("EXP005 outputs are append-only")
    cfg = Exp005Config()
    available = {scenario.name: scenario for scenario in scenario_suite(cfg)}
    if args.phase == "confirmatory":
        names = tuple(available)
        seeds = validate_confirmation(cfg, names, args.output)
    else:
        names = tuple(args.scenarios) if args.scenarios else tuple(available)
        unknown = sorted(set(names) - set(available))
        if unknown:
            raise SystemExit(f"unknown scenarios: {unknown}")
        seeds = cfg.development_seeds
    results = {}
    for index, name in enumerate(names, start=1):
        print(f"[{index}/{len(names)}] {name}", flush=True)
        results[name] = run_scenario(available[name], cfg, seeds)
    save_results(results, args.output)
    print(json.dumps({
        name: {
            "pre_alignment": float(np.mean([
                row["pre_remap_alignment"] for row in result["seeds"]
            ])),
            "post_alignment": float(np.mean([
                row["post_remap_alignment"] for row in result["seeds"]
            ])),
        }
        for name, result in results.items()
    }, indent=2))


if __name__ == "__main__":
    main()

