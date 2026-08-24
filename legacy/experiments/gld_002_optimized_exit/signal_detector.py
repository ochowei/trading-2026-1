"""GLD-002 detector source boundary for the reused GLD-001 entry logic."""

from trading.experiments.gld_001_mean_reversion.signal_detector import GLDSignalDetector


class GLDOptimizedExitSignalDetector(GLDSignalDetector):
    """Reuse GLD-001 indicators/signals with GLD-002 configuration semantics."""
