"""
IWM-010: 回檔範圍 + RSI(2) 混合均值回歸
(IWM Pullback Range + RSI(2) Hybrid Mean Reversion)

結合 IWM-005 的 RSI(2) 進場架構與回檔範圍結構性過濾：
- 10 日回檔範圍 3-10%：過濾淺回檔噪音 (<3%) 和深度熊市假訊號 (>10%)
- RSI(2) < 10 + 2 日跌幅 ≥ 2.5% + ClosePos ≥ 40%：保留 IWM-005 核心進場邏輯
- 出場參數同 IWM-005：TP +4.0% / SL -4.25% / 20 天

3 次嘗試結果：
- Att1（PB 5-12% + RSI2）：Part A 0.31 / Part B 0.31，過濾過嚴 Part B 僅 3 訊號
- Att2（PB 3-10% + RSI2）：Part A 0.40 / Part B 0.31，Part A +5.3%，A/B 比 2.0:1
- Att3（PB 3-10% + WR10）：Part A 0.08 / Part B 0.20，WR(10) 在 IWM 訊號品質遠低於 RSI(2)
最終版本使用 Att2 參數（最佳 Part A 改善）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM010Config(ExperimentConfig):
    """IWM-010 回檔範圍 + RSI(2) 混合參數"""

    # 回檔範圍過濾
    pullback_lookback: int = 10  # 回檔計算回看天數
    pullback_min: float = 0.03  # 最小回檔 3%
    pullback_max: float = 0.10  # 最大回檔 10%

    # RSI(2) 參數（同 IWM-005）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 IWM-005）
    decline_lookback: int = 2
    decline_threshold: float = -0.025  # 2 日跌幅 >= 2.5%

    # 收盤位置過濾（同 IWM-005）
    close_position_threshold: float = 0.4  # >= 40%

    # 冷卻期（同 IWM-005）
    cooldown_days: int = 5


def create_default_config() -> IWM010Config:
    return IWM010Config(
        name="iwm_010_pullback_rsi2_hybrid",
        experiment_id="IWM-010",
        display_name="IWM Pullback Range + RSI(2) Hybrid",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（同 IWM-005）
        stop_loss=-0.0425,  # -4.25%（同 IWM-005）
        holding_days=20,  # 20 天（同 IWM-005）
    )
