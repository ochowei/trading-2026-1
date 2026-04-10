"""
SIVR Donchian 通道突破策略配置 (SIVR-014)

突破策略：當 SIVR 突破 20 日最高價且價格在 SMA(50) 之上，
且近期曾有 ≥5% 的回檔（確保非磨頂突破），進場做多。

與 SIVR-008 BB Squeeze 的差異：
- Donchian 使用固定回看期高點（價格層級）
- BB Squeeze 使用波動率壓縮（統計層級）
- 回檔要求確保突破來自恢復而非持續上漲
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRDonchianBreakoutConfig(ExperimentConfig):
    """SIVR Donchian 通道突破參數"""

    donchian_period: int = 20
    sma_period: int = 50
    pullback_threshold: float = 0.05  # 突破前需有 ≥5% 回檔
    pullback_lookback: int = 10  # 回檔發生在最近 10 日內
    cooldown_days: int = 10


def create_default_config() -> SIVRDonchianBreakoutConfig:
    return SIVRDonchianBreakoutConfig(
        name="sivr_014_donchian_breakout",
        experiment_id="SIVR-014",
        display_name="SIVR Donchian Channel Breakout",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.05,
        stop_loss=-0.05,
        holding_days=20,
    )
