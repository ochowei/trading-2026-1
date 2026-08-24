"""
VGK-004: Crash-Isolated Pullback + WR + ATR Mean Reversion

在 VGK-003 Att2 基礎上加入回檔上限隔離極端崩盤。

Att1★: 回檔上限 7% + TP+3.5%/SL-4.0%/20天 → Part A 0.45, Part B 1.07, min 0.45
  - Sharpe 0.42→0.45（+7.1%），但 A/B 累積差距 37.5%（COVID 訊號僅在 Part A）
Att2: 回檔上限 10% + 持倉 15天 → Part A 0.14（15天轉贏為輸，VGK 需 20天）
Att3: 回檔上限 8% + 持倉 20天 → Part A 0.29（8% 放入 COVID/2022 壞訊號）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK004Config(ExperimentConfig):
    """VGK-004 崩盤隔離回檔+WR+ATR 均值回歸參數"""

    # 回檔參數
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 10日高點回檔 >= 3%
    pullback_cap: float = -0.07  # 回檔上限 7%（~6σ for 1.12% vol, lesson #13）

    # Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # >= 40%

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15  # XLU-011/VGK-003 甜蜜點

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> VGK004Config:
    return VGK004Config(
        name="vgk_004_crash_isolated_mr",
        experiment_id="VGK-004",
        display_name="VGK Crash-Isolated Pullback + WR + ATR MR",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
