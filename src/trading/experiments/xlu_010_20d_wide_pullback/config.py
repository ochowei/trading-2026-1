"""
XLU-010: 20-Day Wide Pullback + Williams %R + Reversal Candle
(XLU 20日寬回檔 + Williams %R + 反轉K線)

COPX-003 證實 20 日回看 + 加寬回檔範圍可大幅改善 Part A Sharpe（0.08→0.39）。
XLU-003 Att1 的 20 日回看失敗是因為沿用 3.5-7% 窄範圍，
20 日窗口讓 2022 漸進式升息下跌也累積至 3.5%，產生大量壞訊號。

本實驗將回檔範圍加寬至 5-10%，使 20 日窗口只在顯著回檔時觸發。
XLU 日波動 1.08% vs COPX ~2.5%，等比例縮放 COPX 的 10-20% → XLU 的 5-10%。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU20dWidePullbackConfig(ExperimentConfig):
    """XLU 20日寬回檔 + WR 參數"""

    # 回檔參數（核心變更：20日回看 + 5-10% 寬範圍）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.05  # 回檔 >= 5%
    pullback_cap: float = -0.10  # 回檔 <= 10%

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉K線確認）
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> XLU20dWidePullbackConfig:
    return XLU20dWidePullbackConfig(
        name="xlu_010_20d_wide_pullback",
        experiment_id="XLU-010",
        display_name="XLU 20-Day Wide Pullback + Williams %R + Reversal Candle",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（XLU 均值回歸甜蜜點）
        stop_loss=-0.040,  # -4.0%（XLU 全域甜蜜點）
        holding_days=20,
    )
