"""
SPY-007: Trend Pullback to SMA(50)
(SPY Trend Following Strategy)

假說：SPY 在確認上升趨勢（黃金交叉）中回測 SMA(50) 後反彈，
提供順勢進場機會。SPY 比 DIA 有更強的科技股趨勢驅動力。

參考 DIA-007 Att3（Part B Sharpe 1.07，Part A 0.29），
嘗試在 SPY 上復現此策略並改善 Part A。

Attempt 1: 直接移植 DIA-007 Att3 架構 → Part A 0.11 / Part B 0.15（失敗）
- 7 個 Part A 停損，SMA(50) 回測在熊市/轉折市產生大量假訊號

Attempt 2: Momentum Pullback to SMA(20) → Part A 0.17 / Part B 0.45（改善但 Part A 仍弱）
- 10 個 Part A 停損，2021 Q4~2022 Q1 轉折期產生 3 連停損

Attempt 3: 加 ClosePos >= 40% 反彈確認 + 冷卻 15d
- ClosePos 在 SPY 上有效（SPY-005 驗證），日波動 ~1.2% 在有效邊界內
- 冷卻 15d 打散 2021 Q4 連續壞訊號群
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPY007TrendPullbackConfig(ExperimentConfig):
    """SPY-007 Trend Pullback 策略專屬參數"""

    # SMA 參數
    sma_short_period: int = 20
    sma_mid_period: int = 50
    sma_long_period: int = 200

    # 收盤位置過濾
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> SPY007TrendPullbackConfig:
    return SPY007TrendPullbackConfig(
        name="spy_007_trend_pullback",
        experiment_id="SPY-007",
        display_name="SPY Momentum Pullback to SMA(20)",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0% (SPY sweet spot from SPY-005)
        holding_days=20,
    )
