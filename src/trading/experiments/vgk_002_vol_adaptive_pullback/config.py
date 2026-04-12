"""
VGK-002: Volatility-Adaptive Pullback + WR Mean Reversion
(VGK 波動率自適應回檔均值回歸)

RSI(2) 框架對 VGK 無效（Att1/Att2 均 Part A Sharpe < 0，ATR 過濾無助益，
因 RSI(2) 訊號本身已處於高波動期，ATR 無額外區分力）。

改用 Pullback + WR 框架（GLD-007 模板）+ ATR 波動率飆升過濾（XLU-011）：
- VGK 日波動 1.12% ≈ GLD 1.12%，直接採用 GLD-007 進場參數
- EWJ（日波動 1.15%）使用相同框架 Part A Sharpe 0.16、Part B 0.24
- ATR > 1.15 選擇急跌恐慌進場（XLU 1.0% vol 甜蜜點）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK002Config(ExperimentConfig):
    """VGK-002 波動率自適應回檔均值回歸參數"""

    # 回檔參數（同 GLD-007，VGK vol 1.12% ≈ GLD 1.12%）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 10日高點回檔 >= 3%

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（XLU-011 甜蜜點）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> VGK002Config:
    return VGK002Config(
        name="vgk_002_vol_adaptive_pullback",
        experiment_id="VGK-002",
        display_name="VGK Volatility-Adaptive Pullback MR",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 GLD-007）
        stop_loss=-0.040,  # -4.0%（同 GLD-007）
        holding_days=20,
    )
