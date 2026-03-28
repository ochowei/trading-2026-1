"""
SPY-005: RSI(2) 極端超賣均值回歸（放寬收盤位置）
(SPY RSI(2) Extreme Oversold Mean Reversion with Relaxed Close Position)

基於 SPY-004 改進：將收盤位置門檻從 ≥ 40% 放寬至 ≥ 25%。
ClosePos 25% 允許在更強賣壓的日子進場——這些在牛市修正中反而提供
更好的均值回歸機會，同時 RSI(2) < 10 + 2日跌幅 ≥ 1.5% 已足夠精確
過濾品質不佳的訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYRsi2RelaxedConfig(ExperimentConfig):
    """SPY RSI(2) 放寬收盤位置參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10（與 SPY-004 相同）

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（放寬反轉確認）
    close_position_threshold: float = 0.25  # ClosePos >= 25%（SPY-004 為 40%）

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> SPYRsi2RelaxedConfig:
    return SPYRsi2RelaxedConfig(
        name="spy_005_rsi2_relaxed_cp",
        experiment_id="SPY-005",
        display_name="SPY RSI(2) Relaxed Close Position",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.025,  # -2.5%（與 TP 對稱）
        holding_days=15,  # 15 天
    )
