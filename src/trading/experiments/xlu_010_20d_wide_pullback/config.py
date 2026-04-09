"""
XLU-010: Volatility-Spike Mean Reversion
(XLU 波動率飆升均值回歸)

Att1 失敗：20日寬回檔（5-10%）Part A -0.22 / Part B -0.10，
20日窗口仍捕捉 2022 漸進式升息下跌。

Att2 結果：ATR(5)/ATR(20) > 1.2 完美移除所有假訊號，Part A 5/5 全勝 (+13.14%)，
Part B Sharpe 1.26。但訊號數太少（5+3=8），Part A Sharpe=0.00（std=0 異常）。

Att3 結果：ATR > 1.1 增加訊號（9+5=14），Part A Sharpe 0.10 / Part B 0.38，
但重新引入 3 個 2021-2022 停損訊號。ATR > 1.2 品質更佳。

最終選擇 ATR > 1.2：Part A 100% WR（5/5 全勝，Sharpe 0.00 因 std=0），
Part B Sharpe 1.26（3 訊號）。波動率飆升過濾成功消除漸進式下跌假訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLUVolSpikeMRConfig(ExperimentConfig):
    """XLU 波動率飆升均值回歸參數"""

    # 回檔參數（同 XLU-003）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035  # 回檔 >= 3.5%
    pullback_cap: float = -0.07  # 回檔 <= 7%

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉K線確認）
    close_position_threshold: float = 0.4

    # 波動率飆升過濾器（核心創新）
    atr_short_period: int = 5  # 短期 ATR 週期
    atr_long_period: int = 20  # 長期 ATR 週期
    atr_ratio_threshold: float = 1.2  # 短期/長期 ATR > 1.2 才進場

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> XLUVolSpikeMRConfig:
    return XLUVolSpikeMRConfig(
        name="xlu_010_20d_wide_pullback",
        experiment_id="XLU-010",
        display_name="XLU Volatility-Spike Mean Reversion",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（XLU 均值回歸甜蜜點）
        stop_loss=-0.040,  # -4.0%（XLU 全域甜蜜點）
        holding_days=20,
    )
