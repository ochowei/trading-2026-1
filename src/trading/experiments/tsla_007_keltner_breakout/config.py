"""
TSLA-007: Keltner Channel Breakout 配置
TSLA Keltner Channel Breakout Configuration

假說：Keltner Channel 使用 ATR 而非標準差衡量波動，對 TSLA 頻繁的跳空缺口更穩健。
ATR 計算 true range（含缺口），可能提供比 BB 更乾淨的擠壓/突破訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLAKeltnerConfig(ExperimentConfig):
    """TSLA Keltner Channel Breakout 策略專屬參數"""

    ema_period: int = 20
    atr_period: int = 10
    atr_multiplier: float = 2.5
    kc_squeeze_percentile_window: int = 60
    kc_squeeze_percentile: float = 0.25
    kc_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> TSLAKeltnerConfig:
    """建立預設配置"""
    return TSLAKeltnerConfig(
        name="tsla_007_keltner_breakout",
        experiment_id="TSLA-007",
        display_name="TSLA Keltner Channel Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
