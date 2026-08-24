"""
XLU-003: Tight Pullback + Williams %R + Reversal Candle
(XLU 緊縮回檔門檻 + Williams %R + 反轉K線)

基於 XLU-002 框架，提高回檔下限從 3% → 3.5%，過濾淺回檔假訊號。
XLU 日波動 1.08%，3% 回檔僅 ~2.8σ 可能不夠深以確保均值回歸。
3.5% 下限（~3.2σ）移除淺回檔假訊號，Part A WR 58.3%→61.9%。

Att1 失敗：20日回看 Part A Sharpe 0.00→-0.17（捕捉更多壞訊號）。
Att2 失敗：回檔上限 7%→6%，Part A Sharpe 0.00→-0.07（移除 2 個好訊號）。
Att3 成功：回檔下限 3%→3.5%，Part A Sharpe 0.00→0.06，Part B 0.32→0.35。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLUTightPullbackConfig(ExperimentConfig):
    """XLU 緊縮回檔門檻 + WR 參數"""

    # 回檔參數（核心變更：下限 3% → 3.5%）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035  # 回檔 >= 3.5%
    pullback_cap: float = -0.07  # 回檔 <= 7% (上限過濾)

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉K線確認）
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> XLUTightPullbackConfig:
    return XLUTightPullbackConfig(
        name="xlu_003_tight_pullback_wr",
        experiment_id="XLU-003",
        display_name="XLU Tight Pullback + Williams %R + Reversal Candle",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
