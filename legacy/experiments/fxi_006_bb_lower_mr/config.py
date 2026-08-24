"""
FXI-006: BB Lower Band → Acute Decline Mean Reversion
(FXI 布林帶下軌→急跌均值回歸)

Att1: BB(20,2.0) lower + ATR>1.05 + ClosePos>=40% + TP5%/SL4.5%/18d
  → Part A -0.19 (12訊號, WR41.7%), Part B 0.04 (2訊號)
  → BB 2.0σ 太鬆，慢磨下跌產生大量假訊號

Att2: BB(20,2.5) + PB>=4% + WR<=80 + ATR>1.05 + ClosePos>=40%
  → Part A -0.70 (5訊號, WR20%), Part B 0.00 (1訊號)
  → BB+多重過濾過度嚴格，訊號不足

Att3: 2日急跌≤-3% + ATR>1.05 + ClosePos>=40% + TP5%/SL5.5%/22d
  → 放棄 BB 和 PB+WR，改用直接的 2 日急跌作為主進場訊號
  → 加寬 SL -5.5%（2.75σ）+ 延長持倉 22d 給予更多恢復空間
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI006Config(ExperimentConfig):
    """FXI-006 急跌均值回歸參數"""

    # 2 日急跌門檻
    decline_2d_threshold: float = -0.03

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # 收盤位置過濾
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FXI006Config:
    return FXI006Config(
        name="fxi_006_bb_lower_mr",
        experiment_id="FXI-006",
        display_name="FXI Acute Decline Mean Reversion",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.050,
        stop_loss=-0.055,
        holding_days=22,
    )
