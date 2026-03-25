"""
TQQQ 溫和放寬進場訊號偵測模組 (TQQQ Gentle Entry Signal Detector)
直接複用 TQQQSignalDetector — 偵測邏輯已參數化，由 config 控制閾值。
Reuses TQQQSignalDetector directly — detection logic is parameterized by config thresholds.
"""

from trading.experiments.tqqq_capitulation.signal_detector import TQQQSignalDetector

__all__ = ["TQQQSignalDetector"]
