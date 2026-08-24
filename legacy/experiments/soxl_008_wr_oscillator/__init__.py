"""SOXL Williams %R(10) 振盪器測試 + 成交模型 (SOXL WR Oscillator Test + Execution Model) — SOXL-008"""

from trading.experiments import register
from trading.experiments.soxl_008_wr_oscillator.strategy import (
    SOXLWROscillatorStrategy,
)

register("soxl_008_wr_oscillator")(SOXLWROscillatorStrategy)
