"""
VOO-003: RSI(2) 寬獲利目標均值回歸
(VOO RSI(2) Wider TP Mean Reversion)

基於 VOO-002 同進場條件與 SL -3.0% / 20d，提升 TP 至 +2.85%。
三次嘗試驗證 TP +2.85% 為 VOO 甜蜜點：
- Att1 (TP +3.0%): Part A Sharpe 0.43（2022-05-12 交易翻為停損）
- Att2 (TP +2.75%): Part A 0.59 / Part B 0.51（改善但非最優）
- Att3 (TP +2.85%): Part A 0.61 / Part B 0.53（最佳，+2.9% 翻轉交易）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VOOWiderTPConfig(ExperimentConfig):
    """VOO RSI(2) 寬獲利目標參數"""

    # RSI(2) 參數（同 VOO-001/002）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10（極端超賣）

    # 2 日累計跌幅過濾（同 VOO-001/002）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 VOO-001/002）
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) >= 40%

    # 冷卻期（同 VOO-001/002）
    cooldown_days: int = 5


def create_default_config() -> VOOWiderTPConfig:
    return VOOWiderTPConfig(
        name="voo_003_wider_tp",
        experiment_id="VOO-003",
        display_name="VOO RSI(2) Wider TP Mean Reversion",
        tickers=["VOO"],
        data_start="2010-10-01",
        profit_target=0.0285,  # +2.85%（VOO-002 為 +2.5%，+2.9% 翻轉交易）
        stop_loss=-0.030,  # -3.0%（同 VOO-002）
        holding_days=20,  # 20 天（同 VOO-002）
    )
