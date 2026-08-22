# Repository Guidelines

## Project Structure & Module Organization

The original EXP000 package remains directly under `src/part_credit`; do not rewrite
its run history. EXP001 is isolated in `src/part_credit/exp001`, with environment,
learner, analysis, experiment, and CLI modules. Its frozen protocol, theory mapping,
parameter decisions, failures, results, and conclusion are in
`experiments/exp001/`. Seed metrics, trial-level NPZ files, and figures under
`results/` are committed evidence, not disposable build artifacts.

## Build, Test, and Development Commands

Resolve the locked environment with `uv sync --extra dev`. Run the full suite with
`uv run pytest`; run one test with `uv run pytest tests/test_model.py::test_small_run_is_deterministic`.
Execute EXP000 with `uv run part-credit --seeds 30 --trials 1200` and EXP001 with
`uv run part-credit-exp001 --phase development`. Use `uv run ruff check .` for the
configured Python 3.10, 100-column lint policy. Do not use ad hoc pip environments;
commit dependency changes together with `uv.lock`.

## Coding Style & Naming Conventions

Use typed Python and keep stochasticity explicit through a passed
`numpy.random.Generator`; never introduce an unseeded global RNG. Keep theoretical
names in the model only when their computational mapping is documented in the model
card. Condition names and serialized metric keys use `snake_case` because they are
part of the machine-readable result format.

## Testing Guidelines

Pytest tests live in `tests/`. Tests must remain deterministic and should distinguish
mechanism checks from claims about biological fidelity. When changing a scientific
mechanism, update the protocol or model card before running new confirmatory seeds,
and append results or failures without erasing earlier runs. Never rerun or overwrite
the held-out EXP001 `frozen_v1` result as if it were a fresh confirmation.

## Commit & Pull Request Guidelines

This repository begins without prior commit conventions. Use concise imperative
commit subjects. Pull requests should state whether changes affect the task, model,
metric, or analysis; identify any post-result decisions; and include the exact test
and experiment commands run.
