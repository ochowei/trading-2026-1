"""
URA-012: Volatility-Acceleration-Bounded Mean Reversion (ATR Ratio BAND)

Cross-asset port of FXI-014 / CIBR-014 ATR ratio framework to URA, refined
to BAND structure after Part A/B mirror-image discovery.

URA-004 baseline (Pullback 10-20% + RSI(2)<15 + 2DD<=-3%) min(A,B) 0.39
had been declared global optimum after 11 strategy types tried (URA-005~011),
including BB Squeeze / SMA trend / vol-adaptive (FLOOR only) / RSI hook /
day-after / WVF / volume-confirmed — all failed.

Trade-level analysis discovered URA Part A and Part B SLs have mirror-image
ATR distributions:
  Part A SLs (7 trades): ATR low(<=1.05): 3, med(1.05-1.30): 2, high(>1.30): 3
  Part B SLs (5 trades): ATR low(<=1.05): 4, med(1.05-1.30): 1, high(>1.30): 0

  → CEILING alone (URA-012 Att1, ATR<=1.30) helps Part A but kills Part B
    (filters Part B winners 2024-08-05 / 2025-01-27 at ATR > 1.55)
  → FLOOR alone (URA-007 Att1, ATR>1.05) helps Part B but kills Part A
    (filters Part A winners at low ATR)
  → BAND structure (Att2, 1.00 <= ATR <= 1.50) balances both directions

Iterations:
  Att1 (CEILING <= 1.30, FXI/CIBR cross-asset port direct):
    Part A 0.69 (+68%) / Part B 0.27 (-31%) / min 0.27 — FAIL
  Att2 ★ (BAND 1.00 <= ATR <= 1.50, mirror-image-balanced):
    Part A 0.47 (+15%) / Part B 0.62 (+59%) / min 0.47 — SUCCESS (+21%)
  Att3 (BAND 1.05 <= ATR <= 1.50, FLOOR tighter):
    Part A 0.37 / Part B 0.51 / min 0.37 — FAIL (over-tight FLOOR)
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA012Config(ExperimentConfig):
    """URA-012 ATR ratio BAND mean reversion parameters"""

    # Pullback parameters (same as URA-004)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    # RSI(2) (same as URA-004)
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 2-day decline (same as URA-004)
    two_day_decline: float = -0.03

    # ATR ratio BAND (Att2 ★ — Part A/B mirror-image discovery)
    # Trade-level analysis: Part A SLs cluster high ATR (CEILING helps),
    # Part B SLs cluster low ATR (FLOOR helps) — BAND balances both.
    # Att1 (CEILING 1.30) Part A 0.69 / Part B 0.27 — FAIL (Part B winners filtered)
    # Att2 ★ (BAND [1.00, 1.50]) Part A 0.47 / Part B 0.62 / min 0.47 — SUCCESS
    # Att3 (BAND [1.05, 1.50]) Part A 0.37 / Part B 0.51 / min 0.37 — FAIL (over-tight)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.00
    atr_ratio_ceiling: float = 1.50

    # Cooldown (same as URA-004)
    cooldown_days: int = 10


def create_default_config() -> URA012Config:
    return URA012Config(
        name="ura_012_atr_band_mr",
        experiment_id="URA-012",
        display_name="URA ATR-Band MR",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,
        stop_loss=-0.055,
        holding_days=20,
    )
