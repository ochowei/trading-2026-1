"""
VGK-006: Trend Pullback Momentum (FAILED — did not surpass VGK-003 Att2)

A momentum/trend strategy testing whether buying VGK in confirmed
uptrends after a mild pullback outperforms mean reversion.

Att1: SMA(20)>SMA(50)+PB 2-5%, TP+3.0%/SL-2.5%/15d
  → Part A 0.17 / Part B 0.02, min 0.02 (SL too tight, 15d too short)
Att2: SMA(20)>SMA(50)+PB 2.5-6%, TP+3.5%/SL-3.5%/20d
  → Part A -0.21 / Part B 0.18, min -0.21 (SMA false positives at tops)
Att3: ROC(10)>3% + 2d decline ≥1%, TP+3.5%/SL-3.5%/20d
  → Part A 0.02 (5 signals) / Part B 0.00 (0 signals) (too restrictive)

Conclusion: Trend/momentum pullback not viable for VGK. Extends
cross-asset lesson #26 to European broad equity ETFs.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK006Config(ExperimentConfig):
    """VGK-006 trend pullback momentum parameters (Att1 — representative)"""

    # Trend filters (SMA alignment)
    sma_short_period: int = 20
    sma_long_period: int = 50

    # Pullback parameters (shallower than mean reversion)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.02  # 10d high pullback >= 2%
    pullback_cap: float = -0.05  # pullback <= 5%

    # Reversal confirmation
    close_position_threshold: float = 0.4  # >= 40% of day range

    # Cooldown
    cooldown_days: int = 7


def create_default_config() -> VGK006Config:
    return VGK006Config(
        name="vgk_006_trend_pullback_momentum",
        experiment_id="VGK-006",
        display_name="VGK Trend Pullback Momentum",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.025,  # -2.5%
        holding_days=15,
    )
