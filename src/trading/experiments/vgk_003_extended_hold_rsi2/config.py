"""
VGK-003: RSI(2) Extended Hold Mean Reversion
(VGK RSI(2) 延長持倉均值回歸)

基於 VGK-001 進場條件，採用 DIA-005 出場優化：
- SL -3.5%（VGK 日波動 1.12% ≈ DIA 1.0%，參考 DIA-005 SL -3.5% 甜蜜點）
- 持倉 25 天（從 20 天延長，讓邊際到期交易達標）
- 冷卻期 10 天（避免歐洲危機期間連續停損）
- 不使用 ATR 過濾（VGK-002/DIA-011 驗證：日波動 ~1% 資產 ATR 無法區分好壞訊號）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK003Config(ExperimentConfig):
    """VGK-003 RSI(2) 延長持倉均值回歸參數"""

    # RSI(2) 參數（同 VGK-001）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 VGK-001）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 VGK-001）
    close_position_threshold: float = 0.4

    # 冷卻期（延長：5 → 10 天）
    cooldown_days: int = 10


def create_default_config() -> VGK003Config:
    return VGK003Config(
        name="vgk_003_extended_hold_rsi2",
        experiment_id="VGK-003",
        display_name="VGK RSI(2) Extended Hold",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 VGK-001）
        stop_loss=-0.035,  # -3.5%（加寬，參考 DIA-005）
        holding_days=25,  # 25 天（延長，參考 DIA-005）
    )
