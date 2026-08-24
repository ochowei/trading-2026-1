"""
TLT-004: Bollinger Band Squeeze Breakout / SMA Golden Cross 配置
TLT Trend Following Configuration

假說：TLT 受利率政策驅動，均值回歸在升息期失效（TLT-001~003 驗證）。
嘗試趨勢跟蹤/突破方向：BB 擠壓突破（Att1/2）和 SMA 黃金交叉（Att3）。
三次嘗試均未能同時達成 Part A 和 Part B 的均衡績效。
最終保留 Att1 BB 擠壓突破（訊號數最均衡 14:13）作為代表版本。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLTBBSqueezeConfig(ExperimentConfig):
    """TLT BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> TLTBBSqueezeConfig:
    """建立預設配置"""
    return TLTBBSqueezeConfig(
        name="tlt_004_bb_squeeze_breakout",
        experiment_id="TLT-004",
        display_name="TLT BB Squeeze Breakout",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.03,
        stop_loss=-0.03,
        holding_days=20,
    )
