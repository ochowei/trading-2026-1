"""
URA-005: BB Squeeze Breakout 配置（3 次嘗試均失敗）
URA BB Squeeze Breakout Configuration (All 3 attempts failed)

URA 首次嘗試突破策略，驗證 BB Squeeze Breakout 在鈾礦 ETF 上的效果。

嘗試記錄：
- Att1: 25th pct, TP+7%/SL-6%, cd 10d → Part A Sharpe -0.13, Part B -0.87
- Att2: 20th pct, TP+6%/SL-7%, cd 15d → Part A Sharpe -0.13, Part B -0.84
- Att3: 15th pct, TP+5%/SL-7%, cd 15d → Part A Sharpe -0.28, Part B -0.37

結論：BB Squeeze Breakout 在 URA 上完全無效。突破訊號頻繁反轉（Part A WR 37-44%，
Part B WR 14-33%），鈾礦 ETF 的波動擠壓突破不具持續性。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URABBSqueezeBreakoutConfig(ExperimentConfig):
    """URA BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.15
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> URABBSqueezeBreakoutConfig:
    """建立預設配置"""
    return URABBSqueezeBreakoutConfig(
        name="ura_005_bb_squeeze_breakout",
        experiment_id="URA-005",
        display_name="URA BB Squeeze Breakout",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.05,
        stop_loss=-0.07,
        holding_days=20,
    )
