"""
SIVR-010: Trend Following (SMA Crossover + Pullback Entry)
SIVR 趨勢跟蹤策略配置

Attempt 3: 改用趨勢跟蹤策略（SMA 金叉 + 回調進場）。
前兩次嘗試使用 Silver/Gold RS Momentum 均失敗（A/B 嚴重失衡）。

策略邏輯：
- SMA(20) > SMA(50)（金叉確認，趨勢向上）
- 5日高點回撤 3-8%（在上升趨勢中回調進場）
- Close > SMA(50)（確保在趨勢之上）
- SMA(20) 5日斜率 > 0（趨勢仍在加速）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRRSMomentumConfig(ExperimentConfig):
    """SIVR 趨勢跟蹤策略參數"""

    sma_fast_period: int = 20
    sma_slow_period: int = 50
    pullback_lookback: int = 5
    pullback_min: float = 0.03  # 5日高點回撤 >= 3%
    pullback_max: float = 0.08  # 5日高點回撤 <= 8%
    cooldown_days: int = 15


def create_default_config() -> SIVRRSMomentumConfig:
    return SIVRRSMomentumConfig(
        name="sivr_010_rs_momentum",
        experiment_id="SIVR-010",
        display_name="SIVR Trend Following (SMA Crossover + Pullback)",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.05,  # +5.0%
        stop_loss=-0.05,  # -5.0% (對稱)
        holding_days=20,
    )
