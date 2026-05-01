"""
URA-012: Volatility-Acceleration-Bounded Mean Reversion (ATR Ratio CEILING)

Cross-asset port of FXI-014 / CIBR-014 ATR ratio CEILING success to URA.
URA-004 baseline (Pullback 10-20% + RSI(2)<15 + 2DD<=-3%) min(A,B) 0.39
has been declared global optimum after 11 strategy types tried (URA-005~011),
including BB Squeeze / SMA trend / vol-adaptive (FLOOR only) / RSI hook /
day-after / WVF / volume-confirmed — all failed.

Hypothesis: URA's Part A losers may cluster at high ATR(5)/ATR(20) ratios
(in-crash acceleration phase) similar to FXI-014's pre-improvement Part A
SLs at ATR ratio 1.38-1.54. URA-007 Att1 (FLOOR ATR>1.05) failed because
URA's panic confirmation is already provided by 2DD<=-3%; the missing
filter is the CEILING that excludes accelerating crashes.

URA vol 2.34% > FXI 2.00% (CEILING 1.35) > CIBR 1.53% (CEILING 1.40),
suggests a tighter URA ceiling around 1.30 by vol scaling extrapolation.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA012Config(ExperimentConfig):
    """URA-012 ATR ratio CEILING mean reversion parameters"""

    # Pullback parameters (same as URA-004)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    # RSI(2) (same as URA-004)
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 2-day decline (same as URA-004)
    two_day_decline: float = -0.03

    # ATR ratio CEILING (new — cross-asset port from FXI-014)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_ceiling: float = 1.30

    # Cooldown (same as URA-004)
    cooldown_days: int = 10


def create_default_config() -> URA012Config:
    return URA012Config(
        name="ura_012_atr_band_mr",
        experiment_id="URA-012",
        display_name="URA ATR-Ceiling MR",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,
        stop_loss=-0.055,
        holding_days=20,
    )
