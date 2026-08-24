"""
EWJ-002: Volatility-Adaptive Pullback + WR Mean Reversion

EWJ-001 使用追蹤停損（啟動 +2.0% / TP +3.5% = 57%，低於 lesson #2 的 80% 門檻），
壓縮獲利空間。改用 ATR(5)/ATR(20) 波動率飆升過濾（VGK-002/XLU-011 模板），
選擇急跌恐慌時機進場，移除追蹤停損。

EWJ 日波動 1.15% ≈ VGK 1.12% ≈ GLD 1.12%，直接採用 VGK-002 Att3 的成功參數。
VGK-002 Att3 以相同框架達到 min(A,B) Sharpe 0.42。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWJ002Config(ExperimentConfig):
    """EWJ-002 波動率自適應回檔均值回歸參數"""

    # 回檔參數（同 GLD-007/VGK-002，EWJ vol 1.15% ≈ GLD/VGK）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 10日高點回檔 >= 3%
    pullback_cap: float = -0.07  # 回檔上限 7%，隔離極端崩盤（lesson #13, ~6σ）

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（XLU-011/VGK-002 甜蜜點）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> EWJ002Config:
    return EWJ002Config(
        name="ewj_002_vol_adaptive_pullback",
        experiment_id="EWJ-002",
        display_name="EWJ Volatility-Adaptive Pullback MR",
        tickers=["EWJ"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 VGK-002/GLD-007）
        stop_loss=-0.040,  # -4.0%（同 VGK-002/GLD-007）
        holding_days=20,
    )
