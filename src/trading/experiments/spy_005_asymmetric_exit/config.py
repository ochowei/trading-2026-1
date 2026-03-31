"""
SPY-005: RSI(2) 寬出場均值回歸
(SPY RSI(2) Wider Exit Mean Reversion)

基於 SPY-004 同進場條件，改用寬出場架構：
- TP +3.0%（SPY-004 為 +2.5%，利用 RSI(2) 訊號的反彈空間）
- SL -3.0%（SPY-004 為 -2.5%，避免短暫深跌假停損）
- 持倉 20 天（SPY-004 為 15 天，給予更多回歸時間）

設計理據：DIA-004 在相同波動度等級（~1.0-1.3%）使用同樣進場框架，
寬出場大幅改善 Sharpe。三次嘗試驗證 SL -3.0% 為 SPY 甜蜜點：
- Att1 (SL -3.5%): Part A 0.45/Part B 0.47（SL 過寬壓縮 Part A）
- Att2 (SL -3.0%): Part A 0.53/Part B 0.56（最佳平衡）✓
- Att3 (SL -2.5%): Part A 0.30/Part B 0.66（SL 過緊致 Part A 低）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYAsymmetricExitConfig(ExperimentConfig):
    """SPY RSI(2) 寬出場參數"""

    # RSI(2) 參數（同 SPY-004）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 SPY-004）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 SPY-004）
    close_position_threshold: float = 0.4

    # 冷卻期（同 SPY-004）
    cooldown_days: int = 5


def create_default_config() -> SPYAsymmetricExitConfig:
    return SPYAsymmetricExitConfig(
        name="spy_005_asymmetric_exit",
        experiment_id="SPY-005",
        display_name="SPY RSI(2) Wider Exit Mean Reversion",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（SPY-004 為 +2.5%）
        stop_loss=-0.030,  # -3.0%（SPY-004 為 -2.5%）
        holding_days=20,  # 20 天（SPY-004 為 15 天）
    )
