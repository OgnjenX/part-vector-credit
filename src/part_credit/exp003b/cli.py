"""Build cache, run robustness, or execute EXP003b development/confirmation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .experiment import CONDITIONS, Exp003bConfig, run_suite
from .figures import save_figures
from .robustness import run_robustness_check
from .spiking_cache import build_cache, save_cache
from .statistics import analyze_suite


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _json_ready(value.tolist())
    if isinstance(value, np.generic):
        return _json_ready(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {
            key: _json_ready(item)
            for key, item in value.items()
            if key != "_raw"
        }
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _save_suite(suite: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True)
    raw_dir = output / "raw"
    raw_dir.mkdir()
    for name, result in suite["conditions"].items():
        np.savez_compressed(raw_dir / f"{name}.npz", **result["_raw"])
    with (output / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(_json_ready(suite), handle, indent=2)
    statistics = analyze_suite(suite)
    with (output / "statistics.json").open("w", encoding="utf-8") as handle:
        json.dump(_json_ready(statistics), handle, indent=2)
    save_figures(suite, output / "figures")
    manifest = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.json":
            manifest[str(path.relative_to(output))] = _sha256(path)
    with (output / "SHA256SUMS.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "phase",
        choices=("build-cache", "robustness", "development", "confirmatory"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--cache", type=Path, default=Path("results/exp003b/smart_response_cache.npz")
    )
    parser.add_argument(
        "--conditions",
        nargs="*",
        choices=tuple(CONDITIONS),
        help="Development-only condition subset; confirmation always runs the frozen suite.",
    )
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("EXP003b outputs are append-only; output path already exists")

    if args.phase == "build-cache":
        cache = build_cache()
        save_cache(cache, args.output)
        print(f"saved Brian2 SMART response cache to {args.output}")
        return
    if args.phase == "robustness":
        result = run_robustness_check()
        args.output.mkdir(parents=True)
        with (args.output / "summary.json").open("w", encoding="utf-8") as handle:
            json.dump(_json_ready(result), handle, indent=2)
        print(json.dumps({"passed": result["passed"], "total": result["total"]}))
        return
    if not args.cache.exists():
        raise SystemExit(f"missing response cache: {args.cache}")

    cfg = Exp003bConfig()
    if args.phase == "confirmatory":
        frozen = Path("experiments/exp003b/FROZEN_PROTOCOL.json")
        if not frozen.exists():
            raise SystemExit("confirmation blocked until FROZEN_PROTOCOL.json is committed")
        protocol = json.loads(frozen.read_text(encoding="utf-8"))
        if protocol.get("status") != "frozen":
            raise SystemExit("confirmation blocked: protocol status is not frozen")
        if str(args.output) != protocol["confirmation_output"]:
            raise SystemExit("confirmation output does not match the frozen protocol")
        if list(cfg.confirmatory_seeds) != protocol["confirmatory_seeds"]:
            raise SystemExit("confirmatory seeds differ from the frozen protocol")
        for relative, expected in protocol["source_sha256"].items():
            if _sha256(Path(relative)) != expected:
                raise SystemExit(f"source hash mismatch: {relative}")
        if _sha256(args.cache) != protocol["smart_cache_sha256"]:
            raise SystemExit("SMART response-cache hash mismatch")
        seeds = cfg.confirmatory_seeds
        names = tuple(CONDITIONS)
    else:
        seeds = cfg.development_seeds
        names = tuple(args.conditions) if args.conditions else tuple(CONDITIONS)
    suite = run_suite(cfg, seeds, args.cache, names)
    _save_suite(suite, args.output)
    print(json.dumps({
        name: result["summary"] for name, result in suite["conditions"].items()
    }, indent=2))


if __name__ == "__main__":
    main()
