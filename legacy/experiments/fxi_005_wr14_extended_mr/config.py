"""
FXI-005: Exit-Optimized Mean Reversion

Same proven entry framework as FXI-002 Att3, with exit optimization
to capture larger policy-driven moves in China's policy-driven market.

Att1: WR(14) + cooldown 15d, same exit as FXI-002 (TP5%/SL4.5%/18d)
  Part A 0.23 (WORSE), Part B 0.50 (same). WR(14) no added value,
  cooldown 15d removed 3 winning Part A signals. Reverted.

Att2: WR(10)/cooldown 10d, wider exits TP5.5%/SL-5.5%/22d
  Part A 0.33 (same), Part B 1.40 (+180%). Wider SL saved 2025-04-04
  Part B trade (SL->TP, +10.1pp swing). But TP/SL scale equally -> same Sharpe.

Att3*: TP5.5%/SL-5.0%/20d (sweet spot)
  Part A 0.38 (+15%!), Part B 1.61 (+222%). SL -5.0% still saves key trade
  while reducing per-SL-trade loss by 0.49pp vs -5.5%. Both higher mean AND
  lower std -> min(A,B) 0.38 beats FXI-002's 0.33.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI005Config(ExperimentConfig):
    """FXI-005 exit-optimized mean reversion parameters"""

    # Pullback parameters (same as FXI-002 Att3)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # 10d high pullback >= 5%
    pullback_cap: float = -0.12  # Cap at 12% (crash isolation)

    # Williams %R (reverted to WR(10) after Att1 showed WR(14) no value)
    wr_period: int = 10
    wr_threshold: float = -80.0

    # Close position filter (reversal confirmation)
    close_position_threshold: float = 0.4

    # ATR volatility filter (same as FXI-002)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # Cooldown (reverted to 10d after Att1 showed 15d removed winners)
    cooldown_days: int = 10


def create_default_config() -> FXI005Config:
    return FXI005Config(
        name="fxi_005_wr14_extended_mr",
        experiment_id="FXI-005",
        display_name="FXI Exit-Optimized MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,  # +5.5% (wider TP for larger policy-driven moves)
        stop_loss=-0.050,  # -5.0% (intermediate SL, tighter than Att2's -5.5%)
        holding_days=20,  # Moderate extension from FXI-002's 18d
    )
