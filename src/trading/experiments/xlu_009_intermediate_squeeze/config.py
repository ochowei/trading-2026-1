"""
XLU-009: Intermediate BB Squeeze Breakout 配置
XLU Intermediate BB Squeeze Breakout Configuration

假說：BB(20,2.25) 提供 BB(20,2) 和 BB(20,2.5) 之間的折衷。
BB(20,2) Part A Sharpe 0.18 / Part B 0.26 — 訊號充足但品質一般。
BB(20,2.5) Part A Sharpe 0.40 / Part B 2.26 — 品質極佳但 Part B 僅 2 訊號。
BB(20,2.25) 預期在品質和訊號數量之間取得更好平衡。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU009Config(ExperimentConfig):
    """XLU-009 Intermediate BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.25
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> XLU009Config:
    """建立預設配置"""
    return XLU009Config(
        name="xlu_009_intermediate_squeeze",
        experiment_id="XLU-009",
        display_name="XLU Intermediate BB Squeeze Breakout",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.04,
        holding_days=25,
    )
