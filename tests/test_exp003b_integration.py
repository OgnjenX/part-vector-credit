from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

import numpy as np

from part_credit.exp003a.plasticity import equation5_update
from part_credit.exp003b import (
    EXP003A_MOTIF_SHA256,
    EXP003A_PLASTICITY_SHA256,
)
from part_credit.exp003b.experiment import CONDITIONS
from part_credit.exp003b.model import Condition, Exp003bController, LearnerConfig
from part_credit.exp003b.spiking_cache import (
    CacheGrid,
    SmartResponseCache,
    build_cache,
    save_cache,
)

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exp003a_component_hashes_are_locked() -> None:
    assert _sha256(ROOT / "src/part_credit/exp003a/motif.py") == EXP003A_MOTIF_SHA256
    assert (
        _sha256(ROOT / "src/part_credit/exp003a/plasticity.py")
        == EXP003A_PLASTICITY_SHA256
    )


def test_local_update_has_no_global_or_teaching_input() -> None:
    parameters = set(inspect.signature(equation5_update).parameters)
    forbidden = {
        "reward", "error", "topdown", "causal", "role", "target", "condition",
    }
    assert parameters.isdisjoint(forbidden)


def test_all_named_conditions_are_computationally_distinct() -> None:
    configurations = [tuple(vars(condition).items()) for condition in CONDITIONS.values()]
    assert len(configurations) == len(set(configurations))


def test_context_expectancy_is_category_hypothesis_specific() -> None:
    controller = Exp003bController(
        LearnerConfig(), Condition(), np.random.default_rng(1)
    )
    assert controller.topdown.ndim == 3
    assert controller.topdown.shape[:2] == (
        controller.cfg.max_categories,
        controller.cfg.n_hypotheses,
    )
    assert not np.shares_memory(controller.topdown[0, 0], controller.motor_basis[0])


def test_small_brian_cache_preserves_match_ablation_and_mismatch(tmp_path: Path) -> None:
    grid = CacheGrid(
        motor=(1.0,),
        weight=(0.6,),
        topdown=(0.0, 1.0),
        global_topdown=(0.0, 1.0),
        reset=(0.0, 1.0),
    )
    path = tmp_path / "cache.npz"
    save_cache(build_cache(grid), path)
    cache = SmartResponseCache(path)
    matched = cache.frame(
        motor=np.asarray([1.0]),
        weight=np.asarray([0.6]),
        topdown=np.asarray([1.0]),
        reset=False,
        plastic=True,
    )
    ablated = cache.frame(
        motor=np.asarray([1.0]),
        weight=np.asarray([0.6]),
        topdown=np.asarray([0.0]),
        reset=False,
        plastic=True,
    )
    mismatch = cache.frame(
        motor=np.asarray([1.0]),
        weight=np.asarray([0.6]),
        topdown=np.asarray([1.0]),
        reset=True,
        plastic=True,
    )
    assert matched["delta_weight"][0] > 0.0
    assert abs(ablated["delta_weight"][0]) < 0.25 * matched["delta_weight"][0]
    assert abs(mismatch["delta_weight"][0]) < 0.25 * matched["delta_weight"][0]


def test_replay_update_is_invariant_to_offline_hidden_roles(tmp_path: Path) -> None:
    grid = CacheGrid(
        motor=(1.0,),
        weight=(0.6,),
        topdown=(1.0,),
        global_topdown=(1.0,),
        reset=(0.0,),
    )
    path = tmp_path / "cache.npz"
    save_cache(build_cache(grid), path)
    cache = SmartResponseCache(path)
    visible = {
        "motor": np.asarray([1.0, 1.0]),
        "weight": np.asarray([0.6, 0.6]),
        "topdown": np.asarray([1.0, 1.0]),
        "reset": False,
        "plastic": True,
    }
    first = cache.frame(**visible)
    offline_causal = np.asarray([1.0, -1.0])
    offline_causal[:] = offline_causal[::-1]
    second = cache.frame(**visible)
    np.testing.assert_array_equal(first["weight_after"], second["weight_after"])
