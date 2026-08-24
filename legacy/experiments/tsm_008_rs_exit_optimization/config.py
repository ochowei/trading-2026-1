"""
TSM-008: RS Exit Optimization 配置
TSM Relative Strength Exit Optimization Configuration

沿用 TSM-007 的進場條件（已驗證最佳），優化出場參數：
- 進場：TSM-SMH 20日報酬差 >= 5% + 5日回撤 3-7% + Close > SMA(50) + 冷卻 10天
- 出場：針對 RS 動量回調進場特性優化 TP/SL/持倉天數

TSM-007 出場（TP+7%/SL-7%/20天）直接沿用 TSM-006 動量回調的參數，
未針對 RS 進場特性獨立優化。RS 進場品質更高（min(A,B) 0.64 vs 0.46），
可能適合不同的出場組合。

三次嘗試結果：
- Att1: TP+7%/SL-7%/25天 → Part A 0.72/Part B 1.32, min(A,B) 0.72（延長持倉改善 Part A）
- Att2: TP+8%/SL-7%/25天 → Part A 0.79/Part B 0.83, min(A,B) 0.79（最佳，A/B 完美平衡）
- Att3: TP+7.5%/SL-7%/25天 → Part A 0.76/Part B 0.79, min(A,B) 0.76（2024-10-31 交易仍翻轉）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMRSExitOptConfig(ExperimentConfig):
    """TSM RS Exit Optimization 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10


def create_default_config() -> TSMRSExitOptConfig:
    return TSMRSExitOptConfig(
        name="tsm_008_rs_exit_optimization",
        experiment_id="TSM-008",
        display_name="TSM RS Exit Optimization",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
