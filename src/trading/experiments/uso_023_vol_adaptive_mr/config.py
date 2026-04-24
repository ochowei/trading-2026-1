"""
USO-023: 波動率自適應均值回歸（USO Volatility-Adaptive Mean Reversion）

USO-013 目前最佳（min(A,B) Sharpe 0.26）的主要弱點：
Part A Sharpe 0.26 vs Part B Sharpe 0.82 — Part A 結構性弱勢。
USO-020 已發現「停損/達標交易在 20 日實現波動率、波動率動量、日內範圍擴張上
完全重疊，不存在技術面指標可區分好壞訊號」，暗示 USO-013 RSI(2)<15 框架
已接近技術面天花板。本實驗嘗試三個方向驗證此結論。

Att1（當前設定）：USO-013 框架 + ATR(5)/ATR(20) > 1.05 波動率飆升過濾。
跨資產移植自 COPX-007 / XLU-011 / IWM-011 / EWZ-002（lesson #15）——在中低波動
（≤ 2.25% vol）資產上，ATR 比率過濾可選擇急跌恐慌型訊號、排除慢磨下跌型假訊號。
USO 日波動 2.2%，與 COPX 2.25% 接近，採用 COPX-007 的 1.05 門檻作為 Att1 起點。

假設：USO Part A 的 2020 油價崩盤期與 2023-2024 慢磨下跌期訊號拖累 Sharpe；
ATR(5)/ATR(20) > 1.05 可選擇 capitulation-type 訊號，提升 Part A Sharpe。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO023Config(ExperimentConfig):
    """USO-023 波動率自適應均值回歸參數"""

    # 進場條件（同 USO-013）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 >= 7%
    pullback_max: float = -0.12  # 回檔上限 12%
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    drop_2d_threshold: float = -0.025  # 2日報酬 ≤ -2.5%
    cooldown_days: int = 10

    # 波動率自適應過濾器（USO-023 Att1 新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05  # ATR(5)/ATR(20) > 1.05（COPX-007 門檻）

    # Att2 / Att3 保留欄位（Att1 不啟用）
    drop_2d_cap: float = -1.0  # 關閉 2DD cap（-100% 等同於不過濾）


def create_default_config() -> USO023Config:
    return USO023Config(
        name="uso_023_vol_adaptive_mr",
        experiment_id="USO-023",
        display_name="USO Volatility-Adaptive RSI(2) Mean Reversion",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,  # +3.0%（USO-013 甜蜜點）
        stop_loss=-0.0325,  # -3.25%（USO-013 甜蜜點）
        holding_days=10,
    )
