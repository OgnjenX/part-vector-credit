"""Offline hidden-role repertoire oracles; never imported by learner code."""

from __future__ import annotations

import numpy as np

from .environment import TopologyTaskConfig


def safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    if x.size != y.size or x.size < 2 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def causal_score(
    pattern: np.ndarray,
    role: np.ndarray,
    mask: np.ndarray | None = None,
) -> float:
    values = np.asarray(pattern, dtype=float)
    causal = np.asarray(role, dtype=float)
    if mask is not None:
        values = values[mask]
        causal = causal[mask]
    return float(values[causal > 0].mean() - values[causal < 0].mean())


def coverage_metrics(patterns: np.ndarray, role: np.ndarray) -> dict[str, object]:
    correlations = np.asarray([safe_corr(pattern, role) for pattern in patterns])
    scores = np.asarray([causal_score(pattern, role) for pattern in patterns])
    order = np.argsort(correlations)[::-1]
    best_corr = int(order[0])
    best_q = int(np.argmax(scores))
    top_k = min(5, patterns.shape[0])
    return {
        "correlations": correlations,
        "causal_scores": scores,
        "A_single": float(correlations[best_corr]),
        "Q_single": float(scores[best_q]),
        "mean_alignment": float(np.mean(correlations)),
        "mean_absolute_alignment": float(np.mean(np.abs(correlations))),
        "top_k_alignment": float(np.mean(correlations[order[:top_k]])),
        "best_alignment_h": best_corr,
        "best_q_h": best_q,
    }


def repertoire_oracles(
    patterns: np.ndarray,
    role: np.ndarray,
    cfg: TopologyTaskConfig,
    phase_masks: np.ndarray | None,
) -> dict[str, object]:
    frames = cfg.action_frames
    hypotheses = patterns.shape[0]
    scores = np.empty((frames, hypotheses), dtype=float)
    for frame in range(frames):
        mask = None if phase_masks is None else phase_masks[frame]
        scores[frame] = [causal_score(pattern, role, mask) for pattern in patterns]

    repeated_totals = scores.sum(axis=0)
    best_single_h = int(np.argmax(repeated_totals))
    best_single_sequence = [best_single_h] * frames
    best_sequence = np.argmax(scores, axis=1).astype(int)

    def evaluate(sequence: list[int] | np.ndarray) -> dict[str, object]:
        state = 0.0
        trajectory = []
        for frame, hypothesis in enumerate(sequence):
            state = float(np.clip(
                state + cfg.causal_strength * scores[frame, int(hypothesis)],
                0.0,
                cfg.target,
            ))
            trajectory.append(state)
        return {
            "sequence": [int(value) for value in sequence],
            "final_state": state,
            "normalized_state": float(state / cfg.target),
            "success": float(cfg.target - state <= cfg.success_tolerance),
            "trajectory": trajectory,
        }

    return {
        "frame_hypothesis_scores": scores,
        "best_single": evaluate(best_single_sequence),
        "best_allowed_sequence": evaluate(best_sequence),
        "allowed_sequence_advantage": (
            evaluate(best_sequence)["normalized_state"]
            - evaluate(best_single_sequence)["normalized_state"]
        ),
    }
