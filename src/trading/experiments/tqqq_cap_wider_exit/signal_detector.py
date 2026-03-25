"""
TQQQ 加寬出場訊號偵測模組 (TQQQ Wider Exit Signal Detector)
直接複用 TQQQSignalDetector — 進場條件與原始策略完全相同。
Reuses TQQQSignalDetector directly — entry conditions are identical to baseline.
"""

from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector

__all__ = ["TQQQSignalDetector"]
