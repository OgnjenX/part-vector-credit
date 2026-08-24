"""Fixed motor-bank construction and offline geometry audits for EXP004."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

COVERAGE_TARGETS = {"low": 0.375, "medium": 0.625, "high": 0.875}


@dataclass(frozen=True)
class BankResult:
    patterns: np.ndarray
    directions: np.ndarray
    family: str
    coverage_label: str
    phase_masks: np.ndarray | None = None


def balanced_role(rng: np.random.Generator, n_neurons: int) -> np.ndarray:
    if n_neurons % 2:
        raise ValueError("EXP004 requires an even neuron count")
    role = np.r_[np.ones(n_neurons // 2), -np.ones(n_neurons // 2)]
    return rng.permutation(role).astype(float)


def _balanced_direction(rng: np.random.Generator, n_neurons: int) -> np.ndarray:
    direction = np.r_[np.ones(n_neurons // 2), -np.ones(n_neurons // 2)]
    return rng.permutation(direction).astype(float)


def direction_alignment(direction: np.ndarray, role: np.ndarray) -> float:
    return float(np.mean(np.asarray(direction) * np.asarray(role)))


def _patterns(directions: np.ndarray, amplitude: float) -> np.ndarray:
    return 0.5 + amplitude * np.asarray(directions, dtype=float)


def random_nested_bank(
    rng: np.random.Generator,
    *,
    n_neurons: int,
    max_hypotheses: int,
    n_hypotheses: int,
    amplitude: float,
) -> BankResult:
    """Generate an interleaved antithetic maximum bank and return its prefix."""
    if n_hypotheses % 2 or max_hypotheses % 2:
        raise ValueError("nested antithetic banks require even sizes")
    pairs = []
    seen: set[bytes] = set()
    while len(pairs) < max_hypotheses // 2:
        direction = _balanced_direction(rng, n_neurons)
        canonical = min(direction.tobytes(), (-direction).tobytes())
        if canonical in seen:
            continue
        seen.add(canonical)
        pairs.append(direction)
    interleaved = np.stack([
        signed
        for direction in pairs
        for signed in (direction, -direction)
    ])
    selected = interleaved[:n_hypotheses]
    return BankResult(
        patterns=_patterns(selected, amplitude),
        directions=selected,
        family="random_nested",
        coverage_label="uncontrolled",
    )


def _draw_with_alignment(
    rng: np.random.Generator,
    role: np.ndarray,
    *,
    exact_abs: float | None = None,
    maximum_abs: float | None = None,
    forbidden: set[bytes],
) -> np.ndarray:
    for _ in range(200_000):
        direction = _balanced_direction(rng, role.size)
        alignment = abs(direction_alignment(direction, role))
        if exact_abs is not None and not np.isclose(alignment, exact_abs):
            continue
        if maximum_abs is not None and alignment > maximum_abs + 1e-12:
            continue
        canonical = min(direction.tobytes(), (-direction).tobytes())
        if canonical in forbidden:
            continue
        forbidden.add(canonical)
        return direction
    raise RuntimeError("unable to construct requested coverage-controlled bank")


def _construct_exact_alignment(
    rng: np.random.Generator,
    role: np.ndarray,
    target_abs: float,
    forbidden: set[bytes],
) -> np.ndarray:
    """Construct a balanced sign direction at an attainable exact correlation."""
    mismatch_count = round((1.0 - target_abs) * role.size / 2.0)
    if mismatch_count % 2:
        raise ValueError("requested alignment is incompatible with balanced signs")
    direction = np.asarray(role, dtype=float).copy()
    per_sign = mismatch_count // 2
    positive = rng.choice(np.flatnonzero(role > 0), per_sign, replace=False)
    negative = rng.choice(np.flatnonzero(role < 0), per_sign, replace=False)
    direction[np.r_[positive, negative]] *= -1.0
    if rng.random() < 0.5:
        direction *= -1.0
    if not np.isclose(abs(direction_alignment(direction, role)), target_abs):
        raise AssertionError("exact alignment construction failed")
    canonical = min(direction.tobytes(), (-direction).tobytes())
    if canonical in forbidden:
        return _construct_exact_alignment(rng, role, target_abs, forbidden)
    forbidden.add(canonical)
    return direction


def controlled_coverage_bank(
    rng: np.random.Generator,
    role: np.ndarray,
    *,
    n_hypotheses: int,
    coverage: str,
    amplitude: float,
) -> BankResult:
    if coverage not in COVERAGE_TARGETS:
        raise ValueError(f"unknown coverage band: {coverage}")
    if n_hypotheses % 2:
        raise ValueError("controlled banks require antithetic pairs")
    target = COVERAGE_TARGETS[coverage]
    forbidden: set[bytes] = set()
    pair_directions = [
        _construct_exact_alignment(rng, role, target, forbidden)
    ]
    while len(pair_directions) < n_hypotheses // 2:
        pair_directions.append(_draw_with_alignment(
            rng,
            role,
            maximum_abs=target,
            forbidden=forbidden,
        ))
    rows = np.stack([
        signed
        for direction in pair_directions
        for signed in (direction, -direction)
    ])
    rows = rows[rng.permutation(rows.shape[0])]
    return BankResult(
        patterns=_patterns(rows, amplitude),
        directions=rows,
        family="controlled_coverage",
        coverage_label=coverage,
    )


def _balanced_phase_masks(
    rng: np.random.Generator, role: np.ndarray, action_frames: int
) -> np.ndarray:
    plus = rng.permutation(np.flatnonzero(role > 0))
    minus = rng.permutation(np.flatnonzero(role < 0))
    cells_per_sign = min(3, len(plus) // action_frames, len(minus) // action_frames)
    masks = np.zeros((action_frames, role.size), dtype=bool)
    for frame in range(action_frames):
        masks[frame, plus[frame * cells_per_sign:(frame + 1) * cells_per_sign]] = True
        masks[frame, minus[frame * cells_per_sign:(frame + 1) * cells_per_sign]] = True
    return masks


def composition_bank(
    rng: np.random.Generator,
    role: np.ndarray,
    *,
    n_hypotheses: int,
    action_frames: int,
    amplitude: float,
    maximum_single_alignment: float = 0.25,
) -> BankResult:
    """Create low-global-coverage directions with phase-specific useful components."""
    if n_hypotheses < 2 * action_frames or n_hypotheses % 2:
        raise ValueError("composition bank needs one antithetic pair per phase")
    masks = _balanced_phase_masks(rng, role, action_frames)
    forbidden: set[bytes] = set()
    pair_directions: list[np.ndarray] = []
    for frame in range(action_frames):
        for _ in range(200_000):
            direction = _balanced_direction(rng, role.size)
            direction[masks[frame]] = role[masks[frame]]
            # Restore the fixed number of positive and negative coordinates outside the mask.
            outside = np.flatnonzero(~masks[frame])
            required_positive = role.size // 2 - int(np.sum(direction[masks[frame]] > 0))
            shuffled = rng.permutation(outside)
            direction[outside] = -1.0
            direction[shuffled[:required_positive]] = 1.0
            if abs(direction_alignment(direction, role)) > maximum_single_alignment + 1e-12:
                continue
            canonical = min(direction.tobytes(), (-direction).tobytes())
            if canonical in forbidden:
                continue
            forbidden.add(canonical)
            pair_directions.append(direction)
            break
        else:
            raise RuntimeError("unable to construct phase-composition direction")
    while len(pair_directions) < n_hypotheses // 2:
        pair_directions.append(_draw_with_alignment(
            rng,
            role,
            maximum_abs=maximum_single_alignment,
            forbidden=forbidden,
        ))
    rows = np.stack([
        signed
        for direction in pair_directions
        for signed in (direction, -direction)
    ])
    rows = rows[rng.permutation(rows.shape[0])]
    return BankResult(
        patterns=_patterns(rows, amplitude),
        directions=rows,
        family="phase_composition",
        coverage_label="low_single_solvable",
        phase_masks=masks,
    )


def bank_geometry(patterns: np.ndarray) -> dict[str, np.ndarray | float]:
    centered = patterns - patterns.mean(axis=1, keepdims=True)
    normalized = centered / (np.linalg.norm(centered, axis=1, keepdims=True) + 1e-12)
    pairwise = normalized @ normalized.T
    off_diagonal = pairwise[~np.eye(pairwise.shape[0], dtype=bool)]
    return {
        "pairwise_similarity": pairwise,
        "row_norms": np.linalg.norm(patterns, axis=1),
        "row_means": patterns.mean(axis=1),
        "row_variances": patterns.var(axis=1),
        "mean_abs_pairwise_similarity": float(np.mean(np.abs(off_diagonal))),
    }
