"""
USO-023: 波動率自適應均值回歸（USO Volatility-Adaptive Mean Reversion）

USO-013 目前最佳（min(A,B) Sharpe 0.26）的主要弱點：
Part A Sharpe 0.26 vs Part B Sharpe 0.82 — Part A 結構性弱勢。
USO-020 已發現「停損/達標交易在 20 日實現波動率、波動率動量、日內範圍擴張上
完全重疊，不存在技術面指標可區分好壞訊號」，暗示 USO-013 RSI(2)<15 框架
已接近技術面天花板。本實驗嘗試三個方向驗證此結論。

Att1（已驗證失敗 min 0.25）：ATR(5)/ATR(20) > 1.05 波動率飆升過濾。ATR 在 USO 無選擇性，
Part B 3 筆 TPs 被錯濾。

Att2（當前設定）：USO-013 框架 + 2日報酬 cap (>= -6%) 過濾「崩盤加速中」訊號。
跨資產移植自 CIBR-012（1.53% vol sector ETF 上 2DD cap -4% 成功），假設 USO Part A
2020 油價崩盤的深 2DD 日（2DD 深於 -6%）為 crash-in-progress 停損結構，cap 可移除。
關閉 ATR 過濾以隔離 2DD cap 效應。
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

    # 波動率自適應過濾器（Att1 參數，Att2 關閉以隔離 2DD cap 效應）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 0.0  # 關閉 ATR 過濾

    # 2DD cap 過濾器（USO-023 Att2 新增）— CIBR-012 方向
    # 過濾「崩盤加速中」訊號（2020-04 WTI 負油價、2022 俄烏衝擊等）
    drop_2d_cap: float = -0.06  # 要求 2日報酬 >= -6%（不可過深）


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
