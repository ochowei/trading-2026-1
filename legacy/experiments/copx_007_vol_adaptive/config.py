"""
COPX-007: 波動率自適應均值回歸配置
(COPX Volatility-Adaptive Mean Reversion Config)

基於 COPX-003 的 20日回檔 + WR(10) 進場架構，加入 ATR(5)/ATR(20) 波動率飆升過濾。
跨資產驗證：XLU-011 (+272%) 和 IWM-011 (+67.7%) 證明 ATR 過濾有效。

Att1: ATR > 1.1  → Part A 0.42 / Part B 0.42, min 0.42（+20% vs COPX-003）
Att2: ATR > 1.15 → Part A 0.46 / Part B 0.42, min 0.42（Part A 更優但 Part B 不變）
Att3: ATR > 1.05 → Part A 0.45 / Part B 0.57, min 0.45（+28.6% vs COPX-003）★
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX007Config(ExperimentConfig):
    """COPX-007 波動率自適應均值回歸參數"""

    # 進場指標（同 COPX-003）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10  # 回檔 >= 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 12

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05  # ATR(5)/ATR(20) > 1.05


def create_default_config() -> COPX007Config:
    return COPX007Config(
        name="copx_007_vol_adaptive",
        experiment_id="COPX-007",
        display_name="COPX Volatility-Adaptive Mean Reversion",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 COPX-003）
        stop_loss=-0.045,  # -4.5%（同 COPX-003）
        holding_days=20,  # 20 天（同 COPX-003）
    )
