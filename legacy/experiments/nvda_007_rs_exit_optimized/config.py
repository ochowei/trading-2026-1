"""
NVDA-007: RS Exit Optimization 配置
NVDA RS Exit Optimization Configuration

基於 NVDA-006 (RS Momentum Pullback) 的成功（Part A 0.47/Part B 0.64），
借鏡 TSM-008 的出場優化方法（延長持倉 20→25天使 min(A,B) 從 0.64→0.79，+23%），
嘗試優化 NVDA-006 的出場參數以提升 min(A,B) > 0.47。

進場條件完全沿用 NVDA-006 Att1（最佳版本）：
- NVDA 20日報酬 - SMH 20日報酬 >= 5%
- 5日高點回撤 3-8%
- Close > SMA(50)
- 冷卻期 10 天

Attempt 1: TP+8%/SL-7%/25d（延長持倉 20→25天）→ Part A 0.44/Part B 0.64, min 0.44（失敗）
Attempt 2: TP+8%/SL-8%/20d（放寬 SL）→ Part A 0.40/Part B 0.57, min 0.40（失敗，虧損放大）
Attempt 3: TP+8%/SL-7%/15d（縮短持倉）→ Part A 0.46/Part B 0.70, min 0.46（最佳嘗試但仍未超越）

結論：三次嘗試均失敗，NVDA-006 的 TP+8%/SL-7%/20d 已是 RS 策略最佳出場配置。
Part A 的 11 筆停損（主要集中在 2021 泡沫期）為結構性虧損，無法透過出場優化改善。
保留 Att3（15d 持倉）作為最終配置，因其 Part B Sharpe 最高（0.70）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDARSExitOptimizedConfig(ExperimentConfig):
    """NVDA RS Exit Optimization 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.08
    cooldown_days: int = 10


def create_default_config() -> NVDARSExitOptimizedConfig:
    return NVDARSExitOptimizedConfig(
        name="nvda_007_rs_exit_optimized",
        experiment_id="NVDA-007",
        display_name="NVDA RS Exit Optimization",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=15,
    )
