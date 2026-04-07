"""
IWM-007: 趨勢回檔恢復策略 (Trend Pullback Recovery)

Attempt 3: 改用 SMA(50) 作為回檔目標，SMA(50) 提供比 SMA(20) 更強的支撐。
當 SMA(50) 正在上升、價格從高處拉回接近 SMA(50) 然後反彈恢復，
代表中期趨勢延續的進場機會。

策略類型：趨勢跟蹤 (Trend Following)
日波動 ~1.5-2%，出場參數適度放寬以捕捉趨勢延續。

Attempt 1: SMA(20) crossback, TP+5%/SL-4%, cooldown 10 → Sharpe -0.17/-0.04
Attempt 2: SMA(20) crossback + slope + 2日確認, TP+4%/SL-4%, cooldown 15 → -0.36/-0.19
Attempt 3: SMA(50) 回檔, 接近 SMA(50) 後反彈, TP+5%/SL-4.5%, cooldown 15
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM007Config(ExperimentConfig):
    """IWM-007 Trend Pullback Recovery 策略專屬參數"""

    # 均線參數
    sma_period: int = 50  # 中期均線（回檔支撐）
    sma_long_period: int = 200  # 長期均線（主趨勢）

    # 回檔條件
    proximity_pct: float = 0.02  # 接近 SMA(50) 的距離（2%以內）
    recent_high_lookback: int = 10  # 回看 N 日內的高點
    min_pullback_pct: float = 0.03  # 從近期高點至少拉回 3%

    # 反彈確認
    close_position_threshold: float = 0.5  # 收盤位置 >= 50%（日內反彈）

    cooldown_days: int = 15  # 冷卻期


def create_default_config() -> IWM007Config:
    return IWM007Config(
        name="iwm_007_trend_pullback",
        experiment_id="IWM-007",
        display_name="IWM Trend Pullback Recovery",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.05,  # +5.0%（SMA50 回檔反彈空間更大）
        stop_loss=-0.045,  # -4.5%（若跌破 SMA50 太多則趨勢轉弱）
        holding_days=20,  # 20 天
    )
