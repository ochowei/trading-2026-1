"""
DIA-007: Trend Pullback to SMA(50)
(DIA Trend Pullback Strategy)

假說：DIA 在確認上升趨勢（黃金交叉）中回測 SMA(50) 支撐後反彈，
提供順勢進場機會。這是純趨勢跟蹤策略，非均值回歸。

DIA 日波動 ~1.0-1.2%，趨勢回檔進場應有天然支撐（SMA50），
SL 可設得相對緊湊。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA007TrendPullbackConfig(ExperimentConfig):
    """DIA-007 Trend Pullback 策略專屬參數"""

    # SMA 參數
    sma_fast_period: int = 50
    sma_slow_period: int = 200

    # 回測 SMA(50) 門檻：Low <= SMA(50)（必須實際觸及）
    proximity_pct: float = 0.0  # 0% — Low must touch or break SMA(50)

    # SMA(50) 斜率確認：SMA(50) 必須在近 N 日內上升
    sma_slope_lookback: int = 10  # 比較 SMA(50) 與 10 日前

    # 反彈確認：Close > SMA(50)
    # (implicit in signal logic)

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> DIA007TrendPullbackConfig:
    return DIA007TrendPullbackConfig(
        name="dia_007_trend_pullback",
        experiment_id="DIA-007",
        display_name="DIA Trend Pullback to SMA(50)",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.035,  # -3.5% (DIA sweet spot from DIA-005)
        holding_days=25,  # Extended holding (DIA-005 validated)
    )
