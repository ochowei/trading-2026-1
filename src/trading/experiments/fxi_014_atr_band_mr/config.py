"""
FXI-014: Volatility-Acceleration-Bounded Mean Reversion (ATR Ratio BAND)

Cross-asset port of CIBR-014's ATR ratio CEILING hypothesis to FXI.
FXI-005 uses ATR(5)/ATR(20) > 1.05 as a FLOOR (panic confirmation).
Trade-level analysis of FXI-005 Part A SLs reveals that "in-crash
acceleration" signals (ATR ratio > 1.40) systematically fail:
  Part A SL ATR ratios: 1.38, 1.41, 1.48, 1.52, 1.54 (5 of 8 SLs)
  Part A SL ATR ratios: 1.10, 1.10, 1.18, 1.38 (3 lower, 1 still high)
  Part A TP/expiry max ATR ratio (winners): 1.32 (excluding 2 expiry days
                                                with 1.71/2.00 that were
                                                non-clean exits)
  Part B (all winners): max ATR ratio 1.25 — well below ceiling

The CEILING dimension targets the symmetric failure mode discovered by
CIBR-014: lesson #15 "ATR>1.15 separates panic from slow-grind" was
FLOOR-only; "ATR > 1.40 marks in-crash acceleration phase" is the
inverse failure.

Att1: ATR ratio CEILING <= 1.40 (CIBR-014 cross-asset reference threshold)
Att2: ATR ratio CEILING <= 1.30 (tighter, repo first sub-CIBR threshold)
Att3: ATR ratio CEILING <= 1.35 (sensitivity boundary check)
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI014Config(ExperimentConfig):
    """FXI-014 ATR ratio BAND mean reversion parameters"""

    # Pullback parameters (same as FXI-005)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05
    pullback_cap: float = -0.12

    # Williams %R (same as FXI-005)
    wr_period: int = 10
    wr_threshold: float = -80.0

    # Close position filter (same as FXI-005)
    close_position_threshold: float = 0.4

    # ATR ratio BAND (new — adds CEILING)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.05
    atr_ratio_ceiling: float = 1.40

    # Cooldown (same as FXI-005)
    cooldown_days: int = 10


def create_default_config() -> FXI014Config:
    return FXI014Config(
        name="fxi_014_atr_band_mr",
        experiment_id="FXI-014",
        display_name="FXI ATR-Band MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,
        stop_loss=-0.050,
        holding_days=20,
    )
