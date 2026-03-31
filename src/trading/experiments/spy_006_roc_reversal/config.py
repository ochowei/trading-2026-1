"""
SPY-006: RSI(2) 寬獲利目標均值回歸
(SPY RSI(2) Wider TP Mean Reversion)

基於 SPY-005 的進場條件，測試提高獲利目標至 +3.5%。

Att1: 純 ROC(5) <= -3% → Sharpe 0.13/0.34（品質過低，失敗）
Att2: RSI(2) + 10日回檔 >= 2% → Sharpe 0.48/0.56（移除 1 個好訊號，失敗）
Att3: RSI(2) 同 SPY-005 進場，TP +3.5% / SL -3.0% / 20d

設計理據：SPY-005 的 TP +3.0% 在部分交易中可能過早出場，
RSI(2) 極端超賣的反彈幅度可能超過 +3.0%。
TP +3.5% 搭配 SL -3.0% 提供更佳的風險報酬比 (1.17:1)。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYROCReversalConfig(ExperimentConfig):
    """SPY RSI(2) 寬獲利目標均值回歸參數"""

    # RSI(2) 參數（同 SPY-005）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 SPY-005）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 SPY-005）
    close_position_threshold: float = 0.4

    # 冷卻期（同 SPY-005）
    cooldown_days: int = 5


def create_default_config() -> SPYROCReversalConfig:
    return SPYROCReversalConfig(
        name="spy_006_roc_reversal",
        experiment_id="SPY-006",
        display_name="SPY RSI(2) Wider TP Mean Reversion",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（SPY-005 為 +3.0%）
        stop_loss=-0.030,  # -3.0%（同 SPY-005）
        holding_days=20,
    )
