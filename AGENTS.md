# Repository Guidelines

## Project Structure & Module Organization

The installable package is under `src/part_credit`. `task.py` defines the artificial
intermingled P+/P- task; `model.py` contains the pART/SMART-inspired state and trial
dynamics; `experiment.py` owns frozen conditions, metrics, and decision rules; and
`cli.py` writes reproducible artifacts. Scientific claims are split deliberately:
`docs/PROTOCOL.md` fixes hypotheses and falsification criteria, `docs/MODEL_CARD.md`
separates Grossberg-derived mechanisms from engineering abstractions, and
`docs/RESULTS.md` is an append-only narrative of successes and failures. Generated
JSON and figures belong in `results/` and are ignored by Git.

## Build, Test, and Development Commands

Create an environment and install with `python -m pip install -e '.[dev]'`. Run the
full suite with `pytest`; run one test with `pytest tests/test_model.py::test_small_run_is_deterministic`.
Execute the fixed initial experiment using `part-credit --seeds 30 --trials 1200`.
Use `ruff check .` for the configured Python 3.10, 100-column lint policy.

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
and append results or failures without erasing earlier runs.

## Commit & Pull Request Guidelines

This repository begins without prior commit conventions. Use concise imperative
commit subjects. Pull requests should state whether changes affect the task, model,
metric, or analysis; identify any post-result decisions; and include the exact test
and experiment commands run.
