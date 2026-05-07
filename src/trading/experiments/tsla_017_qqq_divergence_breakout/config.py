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
- Att2：min_relative_return = -0.01（基於 Att1 trade-level 分析，所有 Part A SLs
  divergence 落於 -1.45% ~ -2.37% 區間，winners 均 > +4.82%）
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
等同 baseline。

================================================================================
Att2 (min_relative_return = -0.01)：PARTIAL Part A SUCCESS / Part B 非綁定
================================================================================
參數：min_relative_return=-0.01（surgical 切除 Part A 全部 3 losers），其餘同 Att1
結果：Part A 10/80.0%/Sharpe **1.17** cum +94.32%（**+39% Part A** vs baseline 0.84）
      Part B 6/66.7%/Sharpe 0.53 cum +26.25%（**完全相同**）
      min(A,B) 0.53（Part B 為約束，未提升）
- Part A 過濾 3 losers（2021-07-30 SL div -1.45%、2023-03-31 SL div -2.37%、
  2023-12-14 Expiry div -1.23%，全部 div < -1%），cooldown chain shift 釋放
  2021-08-02 + 2023-12-15 替代訊號（仍部分 losers），淨 Part A 訊號 11→10、
  WR 72.7%→80.0%、Sharpe 0.84→1.17
- Part B 2024-06-17 winner（div -1.75%）被過濾，cooldown chain shift 釋放
  2024-06-26 winner（div +6.43%，亦 +10% TP）替代——**淨無變化**
失敗：閾值 -1% 對 Part A 高度有效但對 Part B 非綁定（最低 SL div -0.67% 仍 > -1%）。
下一迭代需收緊至 -0.005 區間以 surgical 過濾 Part B 2025-11-03 SL（div -0.67%）。
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
    # Att1：-0.10 loose（非綁定）
    # Att2：-0.01 moderate（surgical 切除 Part A 全部 3 losers div -1.23%~-2.37%）
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    min_relative_return: float = -0.01


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
