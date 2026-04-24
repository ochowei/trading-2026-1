"""
USO-023: 波動率自適應均值回歸（USO Volatility-Adaptive Mean Reversion）

USO-013 目前最佳（min(A,B) Sharpe 0.26）的主要弱點：
Part A Sharpe 0.26 vs Part B Sharpe 0.82 — Part A 結構性弱勢。
USO-020 已發現「停損/達標交易在 20 日實現波動率、波動率動量、日內範圍擴張上
完全重疊，不存在技術面指標可區分好壞訊號」，暗示 USO-013 RSI(2)<15 框架
已接近技術面天花板。本實驗嘗試三個方向驗證此結論。

Att1（已驗證失敗 min 0.25）：ATR(5)/ATR(20) > 1.05 波動率飆升過濾。
Att2（已驗證失敗 min 0.08）：2日報酬 cap >= -6%（反向錯誤：移除 7 贏家 0 輸家）。

Att3（當前設定）：將 USO-013 的 10 日回看窗口改為 20 日（回檔 10-18% 區間），
檢驗 lesson #38「回檔回看窗口不可跨資產移植」在 USO 上的方向——20 日在 GLD/COPX 有效，
在 SIVR/URA/IBIT/INDA 失敗。關閉 Att1 的 ATR、Att2 的 2DD cap 以隔離回看窗口效應。

本檔案最終保留 Att3 配置供後續可重現驗證。三次迭代均失敗於 USO-013 min(A,B) 0.26，
詳見 EXPERIMENTS_USO.md 的 USO-023 章節。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO023Config(ExperimentConfig):
    """USO-023 波動率自適應均值回歸參數"""

    # 進場條件（USO-023 Att3：20 日回看窗口，取代 USO-013 的 10 日）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10  # 回檔 >= 10%（20d 窗口較深）
    pullback_max: float = -0.18  # 回檔上限 18%
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15（保留）
    drop_2d_threshold: float = -0.025  # 2日報酬 ≤ -2.5%（保留）
    cooldown_days: int = 10

    # 以下為 Att1/Att2 遺留參數（Att3 全部關閉以隔離回看窗口效應）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 0.0  # 關閉 ATR 過濾
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
