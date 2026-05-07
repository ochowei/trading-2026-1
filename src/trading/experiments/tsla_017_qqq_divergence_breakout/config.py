"""
TSLA TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout (TSLA-017)

實驗動機 (Motivation)：
- TSLA-015 Att3 為當前全域最優（min(A,B) 0.53，Part A Sharpe 0.84 / Part B 0.53），
  但 Part A vs Part B Sharpe 落差 37%（0.84 vs 0.53），結構性失衡來自 Part A
  2 筆 SL（2021-07-30、2023-03-31）+ 1 筆到期（2023-12-14）共拖累 -7.2%、
  Part B 2 筆 SL（2024-09-23、2025-11-03）共拖累 -14.3%。
- TSLA-013 / TSLA-016 已驗證 single-day signal-day filter（T-1 cap、3d/5d ceiling）
  系統性失敗於 TSLA 高波動 multi-regime AI 個股 BB Squeeze 框架。
- TSLA AI_CONTEXT 明確指出未來突破方向需「跨維度」過濾：
  ^VXN forward-looking implied vol、TSLA-QQQ cross-asset divergence、^VIX BANDS。

嘗試方向（repo 首次：cross-asset divergence regime gate 應用於高波動 AI 個股 +
BB Squeeze Breakout 框架，cross-strategy port from TLT-014）：
**TSLA vs QQQ 多週期報酬差過濾**。

核心思想：
- TSLA 2019 trade war / 2021 Q3 chip shortage / 2023 Q1 demand worry 等事件驅動
  sell-off regime 下，TSLA 20 日報酬常輕微落後 QQQ。此 regime 中 BB Squeeze 觸發
  的突破多為「relative weakness 假突破」，被 single-day filter 無法捕捉但被
  multi-week cross-asset divergence 精準分離。
- 健康的 TSLA breakout 通常發生於：(a) 與 QQQ 同步 melt-up、(b) TSLA 主升段
  leadership、或 (c) calm regime 共識行情。

與 TSLA-008（已失敗 RS Momentum 進場）的明確區分：
- TSLA-008：RS >= +5%/+8% 作為「**進場觸發條件**」（要求 TSLA 必須積極跑贏 QQQ），
  Part B -0.96 / -0.01 災難性失敗
- TSLA-017：divergence >= -X% 作為「**regime 過濾器**」（僅排除 TSLA 嚴重落後
  QQQ 的 bear regime，不要求 TSLA 主動領先），與 BB Squeeze 進場結構正交

與 TSLA-015 Att3 的疊加：
- TSLA-015 Att3：BB(20,2) 擠壓 30th pct + Close>Upper BB + Close>SMA(50) +
  buffered SMA(20)≥0.99×SMA(60)（同資產 multi-week trend regime）
- TSLA-017 新增：TSLA 20d return - QQQ 20d return >= min_relative_return
  （跨資產 multi-week relative strength regime gate）

迭代計畫 (Iteration Plan)：
- Att1：min_relative_return = -0.10（loose，TLT-014 -0.04 vol-scaled to TSLA 3.72% vol）
- Att2：根據 Att1 結果調整閾值
- Att3：根據 Att1/Att2 結果挑選甜蜜點

================================================================================
Att1 (min_relative_return = -0.10)：FAILED non-binding
================================================================================
參數：min_relative_return=-0.10, divergence_lookback=20, benchmark=QQQ
結果：Part A 11/72.7%/Sharpe 0.84 cum +82.29%（與 TSLA-015 Att3 baseline 完全相同）
      Part B 6/66.7%/Sharpe 0.53 cum +26.25%（與 baseline 完全相同）
      min(A,B) 0.53（與 baseline 相同，無改善）
失敗：全部 17 baseline 訊號 divergence 皆 >= -10%（最低 -2.37%），閾值非綁定。
策略方向（lesson #19 family v14 cross-asset divergence regime gate）正確但閾值過鬆，
等同 baseline。下一迭代需大幅收緊閾值至 ~-0.01 區間。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA017Config(ExperimentConfig):
    """TSLA-017 TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 TSLA-015 Att3）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === Same-Asset Multi-Week Trend Regime（同 TSLA-015 Att3 buffered SMA）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.99

    # === Cross-Asset Divergence Regime Gate（TSLA-017 核心新增）===
    # benchmark：QQQ（NASDAQ-100，TSLA 主要市場 context）
    # divergence_lookback：20 日（與 TLT-014 一致）
    # min_relative_return：TSLA N 日報酬 - QQQ N 日報酬 必須 >= 此值
    # Att1：-0.10 loose（TLT-014 -0.04 vol-scaled to TSLA 3.72% vol ≈ 0.04*3.7≈0.15→取 -0.10
    # 為起始，留收緊空間）
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    min_relative_return: float = -0.10


def create_default_config() -> TSLA017Config:
    return TSLA017Config(
        name="tsla_017_qqq_divergence_breakout",
        experiment_id="TSLA-017",
        display_name="TSLA TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
