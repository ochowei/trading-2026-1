"""
FCX 回檔 + Williams %R + 反轉K線均值回歸策略配置
FCX Pullback + Williams %R + Reversal Candle Mean Reversion Configuration

跨資產驗證模式：改編自 GLD-007 / SIVR-003 已驗證的回檔 + WR 策略，
參數依 FCX 2-4% 日均波動做縮放。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXPullbackWRConfig(ExperimentConfig):
    """FCX 回檔 + WR + 反轉K線策略專屬參數"""

    # 回檔條件：收盤價低於 N 日高點的幅度
    pullback_lookback: int = 10
    pullback_threshold: float = -0.09  # 低於 10 日高點 9%

    # Williams %R 條件
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 反轉K線條件：收盤位置（0=最低, 1=最高）
    close_position_threshold: float = 0.4  # 收盤位於當日振幅上方 60%

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FCXPullbackWRConfig:
    """建立預設配置"""
    return FCXPullbackWRConfig(
        name="fcx_002_pullback_wr",
        experiment_id="FCX-002",
        display_name="FCX Pullback + Williams %R + Reversal Candle",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,  # +8% 獲利目標
        stop_loss=-0.10,  # -10% 停損
        holding_days=20,  # 20 天持倉
    )
