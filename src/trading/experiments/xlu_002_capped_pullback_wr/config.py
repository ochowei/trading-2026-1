"""
XLU-002: Capped Pullback + Williams %R + Reversal Candle
(XLU 回檔範圍 + Williams %R + 反轉K線)

基於 XLU-001 框架，加入回檔上限 7% 過濾 2022 利率上升期的深度跌幅。
回檔範圍 3-7% 限制只在「適度修正」時進場，避免持續下跌趨勢。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLUCappedPullbackConfig(ExperimentConfig):
    """XLU 回檔範圍 + WR 參數"""

    # 回檔參數
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_cap: float = -0.07  # 回檔 <= 7% (上限過濾)

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉K線確認）
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> XLUCappedPullbackConfig:
    return XLUCappedPullbackConfig(
        name="xlu_002_capped_pullback_wr",
        experiment_id="XLU-002",
        display_name="XLU Capped Pullback + Williams %R + Reversal Candle",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.040,  # -4.0% (同 XLU-001)
        holding_days=20,
    )
