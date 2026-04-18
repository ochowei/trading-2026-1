"""
VGK-005: Deep Pullback Mean Reversion

在 VGK-003 Att2 基礎上嘗試更深回檔門檻改善訊號品質。

Att1: 2日急跌 ≤ -1.0% + pullback≥3% → Part A 0.36（2日急跌過濾太溫和，反效果）
Att2: pullback≥3.5% + TP+4.0% → Part A 0.28（TP+4.0% 轉達標為停損，確認禁忌）
Att3★: pullback≥3.5% + TP+3.5%/SL-4.0%（隔離 TP 效果，僅測深回檔）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK005Config(ExperimentConfig):
    """VGK-005 深回檔+WR+ATR 均值回歸參數"""

    # 回檔參數
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035  # 10日高點回檔 >= 3.5%（3.13σ）

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


def create_default_config() -> VGK005Config:
    return VGK005Config(
        name="vgk_005_decline_enhanced_mr",
        experiment_id="VGK-005",
        display_name="VGK 2-Day Decline Enhanced Pullback + WR + ATR MR",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
