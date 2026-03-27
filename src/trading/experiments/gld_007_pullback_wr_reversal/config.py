"""
GLD 回檔 + Williams %R + 反轉K線確認配置
(GLD Pullback + Williams %R + Reversal Candle Confirmation Config)

在 GLD-006 基礎上新增「收盤位置過濾」作為第三個進場條件。
要求收盤價位於當日振幅上方 40% 以上，過濾仍在下跌的訊號日（收盤接近最低價），
保留有日內反轉跡象的訊號（收盤從低點反彈）。

Adds Close Position filter on top of GLD-006 entry conditions.
Requires close in upper 60% of day's range, filtering out still-falling signals
and keeping those showing intraday reversal evidence.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLDPullbackWRReversalConfig(ExperimentConfig):
    """GLD 回檔 + Williams %R + 反轉K線確認參數"""

    # 進場指標（同 GLD-006）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥3% 觸發
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 7

    # 新增：收盤位置過濾
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4

    # 追蹤停損
    trail_activation_pct: float = 0.02  # 獲利 +2% 啟動
    trail_distance_pct: float = 0.015  # 追蹤距離 1.5%


def create_default_config() -> GLDPullbackWRReversalConfig:
    return GLDPullbackWRReversalConfig(
        name="gld_007_pullback_wr_reversal",
        experiment_id="GLD-007",
        display_name="GLD Pullback + Williams %R + Reversal Candle",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（因進場品質提升，放寬止盈）
        stop_loss=-0.04,  # -4.0%
        holding_days=20,  # 20 天
    )
