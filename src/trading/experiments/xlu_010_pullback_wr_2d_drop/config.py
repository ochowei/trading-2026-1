"""
XLU-010: Pullback + Williams %R + 2-Day Sharp Decline
(XLU 回檔 + Williams %R + 2日急跌過濾)

基於 XLU-003 框架，探索不同進場過濾條件以改善 Part A Sharpe。

Att1 失敗：2日跌幅 ≤ -1.0%，Part A Sharpe -0.02（vs XLU-003 0.06）。
  2日跌幅過濾移除好訊號多於壞訊號（Part B 10→6，WR 70%→50%）。

Att2 失敗：回檔下限 4.0%（vs 3.5%），Part A Sharpe -0.02，Part B 0.11。
  Part B 訊號 10→5，移除 3.5-4% 回檔中的好訊號。

Att3: WR(10) ≤ -85（vs -80），回檔恢復 3.5-7%，停用 2日跌幅。
  邏輯：更嚴格超賣門檻，只接受真正極端超賣條件。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLUPullbackWR2dDropConfig(ExperimentConfig):
    """XLU 回檔 + WR + 2日急跌參數"""

    # 回檔參數（Att3: 恢復 XLU-003 的 3.5-7%）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035  # 回檔 >= 3.5%
    pullback_cap: float = -0.07  # 回檔 <= 7%

    # Williams %R 參數（Att3: 收緊至 -85）
    wr_period: int = 10
    wr_threshold: float = -85.0  # WR(10) <= -85

    # 收盤位置過濾（同 XLU-003）
    close_position_threshold: float = 0.4

    # 2日跌幅過濾（Att2: 停用）
    drop_2d_threshold: float = 0.0  # 0 = 停用

    # 冷卻期（同 XLU-003）
    cooldown_days: int = 7


def create_default_config() -> XLUPullbackWR2dDropConfig:
    return XLUPullbackWR2dDropConfig(
        name="xlu_010_pullback_wr_2d_drop",
        experiment_id="XLU-010",
        display_name="XLU Pullback + Williams %R + 2-Day Drop",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
