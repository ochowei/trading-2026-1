"""
SIVR 極端超賣均值回歸配置 (SIVR Deep Oversold Mean Reversion Configuration)
雙條件進場：RSI 超賣 + SMA 乖離，搭配冷卻期控制訊號頻率。
Entry requires 2 conditions: RSI oversold + SMA deviation, with cooldown for frequency control.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRMeanReversionConfig(ExperimentConfig):
    """SIVR 均值回歸特定參數（白銀波動較黃金大，閾值較寬）"""

    # RSI 參數
    rsi_period: int = 10
    rsi_threshold: float = 28.0  # 比 GLD 的 30 稍嚴格

    # SMA 乖離參數
    sma_period: int = 20
    sma_deviation_threshold: float = -0.025  # -2.5%（白銀波動較大）

    # 冷卻期
    cooldown_days: int = 15  # 較長冷卻期控制頻率至 3-5 次/年


def create_default_config() -> SIVRMeanReversionConfig:
    return SIVRMeanReversionConfig(
        name="sivr_001_mean_reversion",
        experiment_id="SIVR-001",
        display_name="SIVR Deep Oversold Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.03,  # +3.0%（較低目標提高達標率）
        stop_loss=-0.045,  # -4.5%（較寬停損避免被洗出）
        holding_days=15,  # 15 天給予更多回歸時間
    )
