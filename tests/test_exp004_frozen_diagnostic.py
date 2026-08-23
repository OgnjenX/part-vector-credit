from __future__ import annotations

import numpy as np

from part_credit.exp004.frozen_diagnostic import causal_score, safe_corr


def test_causal_score_uses_only_offline_role_partition() -> None:
    pattern = np.asarray([0.8, 0.2, 0.6, 0.4])
    role = np.asarray([1.0, -1.0, 1.0, -1.0])
    assert np.isclose(causal_score(pattern, role), 0.4)
    assert np.isclose(causal_score(pattern, -role), -0.4)


def test_safe_corr_has_defined_constant_convention() -> None:
    assert safe_corr(np.ones(4), np.arange(4)) == 0.0
    assert np.isclose(safe_corr(np.arange(4), np.arange(4)), 1.0)
