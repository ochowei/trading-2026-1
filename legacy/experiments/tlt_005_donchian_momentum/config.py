"""
TLT-005: Donchian 突破 + 趨勢跟蹤
(TLT Donchian Channel Breakout + Trend Following)

策略類型：趨勢跟蹤 / 突破（非均值回歸）。
TLT 受利率政策驅動，具有明確的趨勢特性。
2022 升息期間均值回歸持續產生假訊號（Part A Sharpe -0.20），
趨勢跟蹤策略在下跌趨勢中自然不會觸發買入訊號，可迴避此風險。

TLT-004 驗證了 BB 擠壓突破，此實驗使用 Donchian Channel 突破
及 ROC 動量兩種不同方法，從不同角度驗證趨勢/動量方向。

結論：Part A Sharpe 0.20（TLT 所有實驗中最佳），但 Part B -0.83（2024-2025
區間震盪環境中突破策略全面失效）。未能超越 TLT-002 的整體表現。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLTBreakoutTrendConfig(ExperimentConfig):
    """TLT Donchian 突破 + ���勢跟蹤參數"""

    # Donchian Channel 突破
    donchian_period: int = 20  # 20 日最高價突破
    # 趨勢確認：SMA 過濾
    sma_period: int = 50  # 收盤 > SMA(50) 確認上升趨勢
    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> TLTBreakoutTrendConfig:
    return TLTBreakoutTrendConfig(
        name="tlt_005_donchian_momentum",
        experiment_id="TLT-005",
        display_name="TLT Donchian Breakout + Trend Following",
        tickers=["TLT"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=20,  # 20 天
    )
