"""Post-hoc repertoire diagnostic using only frozen EXP003b arrays."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from part_credit.exp003b.experiment import Exp003bConfig, _seed_rngs
from part_credit.exp003b.model import Condition, Exp003bController
from part_credit.exp003b.spiking_cache import SmartResponseCache


def safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    """Pearson correlation with an explicit zero-variance convention."""
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    if x.size != y.size or x.size < 2 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def causal_score(pattern: np.ndarray, role: np.ndarray) -> float:
    """Exact balanced-population BCI control score for one soma pattern."""
    values = np.asarray(pattern, dtype=float)
    causal = np.asarray(role, dtype=float)
    return float(values[causal > 0].mean() - values[causal < 0].mean())


def _bootstrap_corr(
    rows: list[dict[str, Any]], x_key: str, y_key: str, rng_seed: int
) -> dict[str, Any]:
    x = np.asarray([row[x_key] for row in rows], dtype=float)
    y = np.asarray([row[y_key] for row in rows], dtype=float)
    observed = safe_corr(x, y)
    rng = np.random.default_rng(rng_seed)
    estimates = np.empty(5000, dtype=float)
    for index in range(estimates.size):
        sample = rng.integers(0, x.size, x.size)
        estimates[index] = safe_corr(x[sample], y[sample])
    return {
        "x": x_key,
        "y": y_key,
        "n_seeds": int(x.size),
        "correlation": observed,
        "bootstrap_ci95": np.quantile(estimates, [0.025, 0.975]).tolist(),
    }


def _initial_state(
    seed: int, cfg: Exp003bConfig, cache: SmartResponseCache
) -> tuple[Exp003bController, np.ndarray]:
    learner_rng = _seed_rngs(seed)[1]
    controller = Exp003bController(cfg.learner, Condition(), learner_rng)
    zero_topdown = np.zeros(cfg.learner.n_neurons)
    probe = []
    for hypothesis in range(cfg.learner.n_hypotheses):
        response = cache.frame(
            motor=controller.initial_motor_basis[hypothesis],
            weight=controller.initial_lower_weights[hypothesis],
            topdown=zero_topdown,
            reset=False,
            plastic=False,
        )
        probe.append(response["soma"])
    return controller, np.asarray(probe, dtype=float)


def _coverage(patterns: np.ndarray, role: np.ndarray) -> dict[str, Any]:
    correlations = np.asarray([safe_corr(row, role) for row in patterns])
    scores = np.asarray([causal_score(row, role) for row in patterns])
    best_corr_h = int(np.argmax(correlations))
    best_q_h = int(np.argmax(scores))
    pairs = patterns.shape[0] // 2
    return {
        "correlations": correlations,
        "causal_scores": scores,
        "A_single": float(correlations[best_corr_h]),
        "Q_single": float(scores[best_q_h]),
        "best_corr_h": best_corr_h,
        "best_q_h": best_q_h,
        "best_corr_pair": int(best_corr_h % max(1, pairs)),
        "best_corr_orientation": int(best_corr_h >= pairs),
    }


def _reconstruct_learning(
    raw: dict[str, np.ndarray],
    initial: Exp003bController,
    seed_index: int,
    cfg: Exp003bConfig,
) -> tuple[dict[str, dict[str, np.ndarray]], list[dict[str, Any]]]:
    """Replay frozen value/outstar algebra from archived selected samples."""
    values = np.zeros_like(initial.values)
    topdown = initial.initial_topdown.copy()
    snapshots: dict[str, dict[str, np.ndarray]] = {}
    events: list[dict[str, Any]] = []
    episode_scalar = raw["episode_scalar"][seed_index]
    for episode in range(cfg.total_episodes):
        evaluating = bool(episode_scalar[episode, 2])
        if not evaluating:
            reward = float(episode_scalar[episode, 3])
            improvement = float(episode_scalar[episode, 4])
            wm_strength = float(episode_scalar[episode, 6])
            outcome = 0.80 * improvement + 0.20 * reward
            eligibility = 1.0
            for frame in reversed(range(cfg.environment.action_frames)):
                category = int(raw["category"][seed_index, episode, frame])
                hypothesis = int(raw["hypothesis"][seed_index, episode, frame])
                resonant = bool(raw["resonant"][seed_index, episode, frame])
                strength = wm_strength * eligibility
                eligibility *= cfg.learner.eligibility_decay
                old_value = float(values[category, hypothesis])
                values[category, hypothesis] += (
                    cfg.learner.reinforcement_lr
                    * strength
                    * (outcome - values[category, hypothesis])
                )
                if resonant:
                    gain = 1.0 + max(0.0, float(values[category, hypothesis]))
                    eta = cfg.learner.outstar_lr * gain * strength
                    soma = np.asarray(raw["soma"][seed_index, episode, frame], dtype=float)
                    target = soma - float(np.mean(soma))
                    before = topdown[category, hypothesis].copy()
                    topdown[category, hypothesis] += eta * (
                        target - topdown[category, hypothesis]
                    )
                    events.append({
                        "seed_index": seed_index,
                        "episode": episode,
                        "frame": frame,
                        "category": category,
                        "hypothesis": hypothesis,
                        "outcome": outcome,
                        "value_before": old_value,
                        "value_after": float(values[category, hypothesis]),
                        "strength": strength,
                        "eta_eff": eta,
                        "target": target,
                        "topdown_before": before,
                        "topdown_after": topdown[category, hypothesis].copy(),
                    })
        if episode == cfg.acquisition_episodes - 1:
            snapshots["pre"] = {"values": values.copy(), "topdown": topdown.copy()}
        if episode == cfg.remap_at + cfg.reacquisition_episodes - 1:
            snapshots["post"] = {"values": values.copy(), "topdown": topdown.copy()}
    return snapshots, events


def _phase_episode_bounds(phase: str, cfg: Exp003bConfig) -> tuple[range, range]:
    if phase == "pre":
        return range(cfg.acquisition_episodes), range(
            cfg.acquisition_episodes, cfg.remap_at
        )
    return range(cfg.remap_at, cfg.remap_at + cfg.reacquisition_episodes), range(
        cfg.remap_at + cfg.reacquisition_episodes, cfg.total_episodes
    )


def _selected_pair_diagnostics(
    *,
    raw: dict[str, np.ndarray],
    seed_index: int,
    phase: str,
    context: int,
    role: np.ndarray,
    initial_motor: np.ndarray,
    initial_probe: np.ndarray,
    snapshot: dict[str, np.ndarray],
    events: list[dict[str, Any]],
    cfg: Exp003bConfig,
) -> dict[str, Any]:
    train_range, eval_range = _phase_episode_bounds(phase, cfg)
    eval_episodes = [
        episode for episode in eval_range
        if int(raw["episode_scalar"][seed_index, episode, 1]) == context
    ]
    pairs = [
        (
            int(raw["category"][seed_index, episode, frame]),
            int(raw["hypothesis"][seed_index, episode, frame]),
        )
        for episode in eval_episodes
        for frame in range(cfg.environment.action_frames)
    ]
    unique, counts = np.unique(np.asarray(pairs), axis=0, return_counts=True)
    selected_index = int(np.argmax(counts))
    selected_k, selected_h = (int(value) for value in unique[selected_index])
    selected_fraction = float(counts[selected_index] / np.sum(counts))
    learned_t = snapshot["topdown"][selected_k, selected_h]
    learned_value = float(snapshot["values"][selected_k, selected_h])
    emitted = np.stack([
        raw["topdown"][seed_index, episode, frame]
        for episode in eval_episodes
        for frame in range(cfg.environment.action_frames)
        if int(raw["category"][seed_index, episode, frame]) == selected_k
        and int(raw["hypothesis"][seed_index, episode, frame]) == selected_h
    ]).mean(axis=0)
    predicted_emitted = (1.0 + cfg.learner.motivated_gain * max(0.0, learned_value)) * learned_t
    selected_events = [
        event for event in events
        if event["episode"] in train_range
        and event["category"] == selected_k
        and event["hypothesis"] == selected_h
    ]
    targets = np.stack([event["target"] for event in selected_events])
    etas = np.asarray([event["eta_eff"] for event in selected_events])
    simple_average = targets.mean(axis=0)
    target_alignments = np.asarray([safe_corr(target, role) for target in targets])
    best_motor = _coverage(initial_motor, role)
    best_probe = _coverage(initial_probe, role)
    return {
        "context": context,
        "selected_category": selected_k,
        "selected_hypothesis": selected_h,
        "selected_fraction": selected_fraction,
        "selected_initial_motor_alignment": safe_corr(initial_motor[selected_h], role),
        "selected_initial_soma_alignment": safe_corr(initial_probe[selected_h], role),
        "selected_initial_q": causal_score(initial_probe[selected_h], role),
        "learned_t_alignment": safe_corr(learned_t, role),
        "emitted_t_alignment": safe_corr(emitted, role),
        "t_to_best_motor": safe_corr(learned_t, initial_motor[best_motor["best_corr_h"]]),
        "t_to_best_initial_soma": safe_corr(
            learned_t, initial_probe[best_probe["best_corr_h"]]
        ),
        "t_to_selected_initial_soma": safe_corr(learned_t, initial_probe[selected_h]),
        "t_to_simple_target_average": safe_corr(learned_t, simple_average),
        "t_to_best_sampled_target": float(np.max([
            safe_corr(learned_t, target) for target in targets
        ])),
        "best_sampled_target_role_alignment": float(np.max(target_alignments)),
        "simple_average_role_alignment": safe_corr(simple_average, role),
        "t_improvement_over_best_target": (
            safe_corr(learned_t, role) - float(np.max(target_alignments))
        ),
        "target_count": len(selected_events),
        "eta_min": float(np.min(etas)),
        "eta_max": float(np.max(etas)),
        "eta_mean": float(np.mean(etas)),
        "emitted_replay_rmse": float(np.sqrt(np.mean((emitted - predicted_emitted) ** 2))),
    }


def run_frozen_diagnostic(
    *, raw_path: Path, summary_path: Path, cache_path: Path
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    cfg = Exp003bConfig()
    loaded = np.load(raw_path)
    raw = {key: loaded[key] for key in loaded.files}
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    seed_summaries = summary["conditions"]["primary_part_t_smart"]["seeds"]
    cache = SmartResponseCache(cache_path)
    phase_rows: list[dict[str, Any]] = []
    context_rows: list[dict[str, Any]] = []
    all_events: list[dict[str, Any]] = []
    initial_banks = []
    initial_probes = []
    hidden_roles = []

    for seed_index, seed_row in enumerate(seed_summaries):
        seed = int(seed_row["seed"])
        controller, initial_probe = _initial_state(seed, cfg, cache)
        snapshots, events = _reconstruct_learning(raw, controller, seed_index, cfg)
        initial_motor = controller.initial_motor_basis.copy()
        initial_banks.append(initial_motor)
        initial_probes.append(initial_probe)
        hidden_roles.append(np.stack([
            raw["causal"][seed_index, 0],
            raw["causal"][seed_index, cfg.remap_at],
        ]))
        all_events.extend(events)

        for phase_index, phase in enumerate(("pre", "post")):
            base_role = np.asarray(hidden_roles[-1][phase_index], dtype=float)
            motor_context = []
            soma_context = []
            selected_context = []
            for context in (0, 1):
                role = base_role if context == 0 else -base_role
                motor_coverage = _coverage(initial_motor, role)
                soma_coverage = _coverage(initial_probe, role)
                selected = _selected_pair_diagnostics(
                    raw=raw,
                    seed_index=seed_index,
                    phase=phase,
                    context=context,
                    role=role,
                    initial_motor=initial_motor,
                    initial_probe=initial_probe,
                    snapshot=snapshots[phase],
                    events=events,
                    cfg=cfg,
                )
                context_rows.append({
                    "seed": seed,
                    "phase": phase,
                    "A_B": motor_coverage["A_single"],
                    "Q_B": motor_coverage["Q_single"],
                    "A_S": soma_coverage["A_single"],
                    "Q_S": soma_coverage["Q_single"],
                    **selected,
                })
                motor_context.append(motor_coverage)
                soma_context.append(soma_coverage)
                selected_context.append(selected)
            success_key = (
                "pre_remap_evaluation_success"
                if phase == "pre" else "post_remap_evaluation_success"
            )
            phase_rows.append({
                "seed": seed,
                "phase": phase,
                "A_B": float(np.mean([row["A_single"] for row in motor_context])),
                "Q_B": float(np.mean([row["Q_single"] for row in motor_context])),
                "A_S": float(np.mean([row["A_single"] for row in soma_context])),
                "Q_S": float(np.mean([row["Q_single"] for row in soma_context])),
                "final_success": float(seed_row[success_key]),
                "final_t_alignment": float(np.mean([
                    row["emitted_t_alignment"] for row in selected_context
                ])),
                "selected_initial_alignment": float(np.mean([
                    row["selected_initial_soma_alignment"] for row in selected_context
                ])),
                "selected_initial_q": float(np.mean([
                    row["selected_initial_q"] for row in selected_context
                ])),
                "t_to_best_initial_soma": float(np.mean([
                    row["t_to_best_initial_soma"] for row in selected_context
                ])),
                "t_to_selected_initial_soma": float(np.mean([
                    row["t_to_selected_initial_soma"] for row in selected_context
                ])),
                "t_to_simple_target_average": float(np.mean([
                    row["t_to_simple_target_average"] for row in selected_context
                ])),
                "t_improvement_over_best_target": float(np.mean([
                    row["t_improvement_over_best_target"] for row in selected_context
                ])),
                "selected_fraction": float(np.mean([
                    row["selected_fraction"] for row in selected_context
                ])),
                "emitted_replay_rmse": float(np.mean([
                    row["emitted_replay_rmse"] for row in selected_context
                ])),
            })

    correlations: dict[str, list[dict[str, Any]]] = {}
    relationships = (
        ("A_B", "final_success"),
        ("A_B", "final_t_alignment"),
        ("A_S", "final_success"),
        ("A_S", "final_t_alignment"),
        ("Q_S", "final_success"),
        ("Q_S", "final_t_alignment"),
        ("selected_initial_alignment", "final_t_alignment"),
        ("selected_initial_q", "final_success"),
    )
    for phase_offset, phase in enumerate(("pre", "post")):
        selected = [row for row in phase_rows if row["phase"] == phase]
        correlations[phase] = [
            _bootstrap_corr(selected, x, y, 4004 + phase_offset * 100 + index)
            for index, (x, y) in enumerate(relationships)
        ]

    event_arrays = {
        "seed_index": np.asarray([row["seed_index"] for row in all_events], dtype=np.int16),
        "episode": np.asarray([row["episode"] for row in all_events], dtype=np.int16),
        "frame": np.asarray([row["frame"] for row in all_events], dtype=np.int8),
        "category": np.asarray([row["category"] for row in all_events], dtype=np.int16),
        "hypothesis": np.asarray([row["hypothesis"] for row in all_events], dtype=np.int16),
        "outcome": np.asarray([row["outcome"] for row in all_events], dtype=np.float32),
        "value_before": np.asarray([row["value_before"] for row in all_events], dtype=np.float32),
        "value_after": np.asarray([row["value_after"] for row in all_events], dtype=np.float32),
        "strength": np.asarray([row["strength"] for row in all_events], dtype=np.float32),
        "eta_eff": np.asarray([row["eta_eff"] for row in all_events], dtype=np.float32),
        "target": np.stack([row["target"] for row in all_events]).astype(np.float32),
        "topdown_before": np.stack([
            row["topdown_before"] for row in all_events
        ]).astype(np.float32),
        "topdown_after": np.stack([
            row["topdown_after"] for row in all_events
        ]).astype(np.float32),
        "initial_motor_bank": np.stack(initial_banks).astype(np.float32),
        "initial_soma_probe": np.stack(initial_probes).astype(np.float32),
        "hidden_role_pre_post": np.stack(hidden_roles).astype(np.int8),
    }
    report = {
        "label": "POST HOC EXP003b REPERTOIRE DIAGNOSTIC — NOT CONFIRMATORY",
        "frozen_outcome_unchanged": "Outcome C",
        "source_checkpoint": "0e68fedbd7f35d223234b07d9e96f958d7b2896c",
        "config": asdict(cfg),
        "phase_rows": phase_rows,
        "context_rows": context_rows,
        "correlations": correlations,
        "aggregate": {
            key: float(np.mean([row[key] for row in phase_rows]))
            for key in (
                "A_B", "A_S", "Q_S", "final_success", "final_t_alignment",
                "selected_initial_alignment", "selected_initial_q",
                "t_to_best_initial_soma", "t_to_selected_initial_soma",
                "t_to_simple_target_average", "t_improvement_over_best_target",
                "selected_fraction", "emitted_replay_rmse",
            )
        },
        "limitations": [
            "Initial B and no-top-down soma probes are deterministically reconstructed from the frozen seed and locked response cache.",
            "Values and T are exactly replayed from frozen category/hypothesis/soma/outcome arrays; the BCI is not rerun.",
            "Final T is cross-checked against archived motivated-gain-scaled emitted top-down during evaluation.",
            "Only 12 mapping seeds are available, so coverage correlations have wide bootstrap intervals.",
        ],
    }
    return report, event_arrays


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("results/exp003b/frozen_v1/raw/primary_part_t_smart.npz"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/exp003b/frozen_v1/summary.json"),
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path("results/exp003b/smart_response_cache.npz"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("diagnostic output is append-only")
    report, arrays = run_frozen_diagnostic(
        raw_path=args.raw, summary_path=args.summary, cache_path=args.cache
    )
    args.output.mkdir(parents=True)
    (args.output / "diagnostic.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    np.savez_compressed(args.output / "reconstruction_arrays.npz", **arrays)
    print(json.dumps(report["aggregate"], indent=2))


if __name__ == "__main__":
    main()
