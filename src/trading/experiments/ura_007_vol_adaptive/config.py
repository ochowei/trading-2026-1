"""
URA-007: 波動率自適應均值回歸配置
(URA Volatility-Adaptive Mean Reversion Config)

基於 URA-004 的回檔 + RSI(2) + 2日急跌進場架構，加入 ATR(5)/ATR(20) 波動率飆升過濾。
跨資產驗證：COPX-007 (+28.6%, 日波動 2.25%), IWM-011 (+67.7%), XLU-011 (+272%)。
URA 日波動 2.34%，接近 COPX，但 ATR 過濾在 URA 上無效。

Att1: ATR > 1.05 + SL -5.5% → Part A 0.27 / Part B 0.71, min 0.27（Part B +82% 但 Part A -34%）
Att2: ATR > 1.1  + SL -5.5% → Part A 0.21 / Part B 1.18, min 0.21（更嚴格 ATR 移除 Part A 好訊號）
Att3: ATR > 1.05 + SL -6.0% → Part A 0.22 / Part B 0.65, min 0.22（寬 SL 未挽救任何停損）
結論：URA 熊市訊號在高波動環境，ATR 無法區分好壞訊號，確認 ATR 有效邊界 ≤ 2.25%
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA007Config(ExperimentConfig):
    """URA-007 波動率自適應均值回歸參數"""

    # 進場指標（同 URA-004）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 >= 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    two_day_decline: float = -0.03  # 2日跌幅 ≤ -3%
    cooldown_days: int = 10

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05  # ATR(5)/ATR(20) > 1.05


def create_default_config() -> URA007Config:
    return URA007Config(
        name="ura_007_vol_adaptive",
        experiment_id="URA-007",
        display_name="URA Volatility-Adaptive Mean Reversion",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,  # +6.0%（同 URA-004）
        stop_loss=-0.055,  # -5.5%（同 URA-004，Att1 最佳嘗試）
        holding_days=20,  # 20 天（同 URA-004）
    )
