"""EXP003a: independently validated SMART-derived spiking plasticity motif."""

from .motif import MotifConfig, run_condition
from .plasticity import equation5_update, equation6_post_signal

__all__ = ["MotifConfig", "equation5_update", "equation6_post_signal", "run_condition"]
