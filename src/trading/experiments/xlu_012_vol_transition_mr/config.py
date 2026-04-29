"""
XLU Post-Capitulation Vol-Transition MR Configuration (XLU-012)

動機：XLU-011（當前最佳，min(A,B) Sharpe 0.67）的 Part A 殘留 1 筆 SL（2021-09-20
-4.10%，FOMC 鷹派衝擊）與 Part B 殘留 1 筆近零到期（2024-01-18 -0.20%）。本實驗
測試是否可透過 2DD 過濾移除這些失敗訊號（CIBR-012 / INDA-010 的 2DD 區間方向
跨資產移植）。

跨資產背景：
- CIBR-012 Att3（2026-04-21）：2DD cap >= -4.0% 在 1.53% vol US 板塊 ETF 成功
- INDA-010 Att3（2026-04-21）：2DD floor <= -2.0% 在 0.97% vol single-country EM ETF 成功
- XLU 1.08% vol 介於兩者，且為利率敏感公用事業（不同失敗結構）

XLU-011 訊號 2DD 分布實測（auto_adjust=True data）：
  Part A TP（6 筆）：-0.67%, -1.16%, -1.31%, -1.48%, -1.77%, -2.09%
  Part A SL（1 筆）：-1.72%（2021-09-20 FOMC 鷹派）
  Part B TP（3 筆）：-0.01%, -2.32%, -3.39%
  Part B Expiry（1 筆）：-2.51%（2024-01-18 近零到期）

關鍵觀察：失敗訊號 2DD 落於 -1.72% / -2.51%（中等深度），與 TP 訊號 2DD 寬廣分布
重疊。「2DD 維度」對 XLU 的 winners/losers 不具區分力。

========================================================================
三次迭代結果（2026-04-27，成交模型 0.1% slippage，隔日開盤市價進場）
========================================================================

Att1（失敗）：XLU-011 框架 + 2DD cap >= -2.5%（CIBR-012 方向移植）+ TP +2.5%
  Part A: 7 訊號（同 XLU-011 baseline），WR 85.7%，Sharpe 0.67，cum +11.21%
  Part B: 3 訊號（過濾 2024-01-18 expiry、2024-11-04 deep TP，cooldown 移入
          2024-11-06）WR 100%，Sharpe **0.00（zero-var, 3 TPs 皆 +2.50%）**
  min(A,B) **0.00**（vs XLU-011 0.67，崩壞）
  失敗分析：(a) Part A 訊號 2DD 全部 >= -2.5%（cap 結構非綁定），無過濾效果；
  (b) Part B 移除 1 expiry + 2 TPs（淨 -1 TP, -1 expiry）後僅留 3 純 TPs，
  zero-variance 使 Sharpe 計算崩潰至 0。**核心發現**：CIBR 方向（過濾深 2DD）
  在 XLU 上同時移除 Part B winner（2024-11-04 TP -3.39%）與 expiry（2024-01-18
  -2.51%），無選擇力。

Att2（失敗）：Att1 + TP 加寬至 +3.0%（嘗試打破 Part B zero-var）
  Part A: 7 訊號 WR 85.7%，Sharpe **0.75**（+12% vs baseline，因 TP 擴張），
          cum +13.26%
  Part B: 3 訊號 WR 100%，Sharpe **0.00（仍 zero-var, 3 TPs 皆 +3.00%）**
          cum +9.27%
  min(A,B) **0.00**（仍崩壞）
  失敗分析：TP +3.0% 提升 Part A（5 TPs 從 +2.5% → +3.0%），但 Part B 3 個
  剩餘訊號仍乾淨達標，TP 加寬未引入到期變異。**確認 2DD cap 對 XLU Part B
  結構性退化**。

Att3 ★（當前最佳）：移除 2DD 過濾，僅保留 TP 加寬（XLU-011 框架 + TP +3.0%）
  Part A: 7 訊號 WR 85.7%，Sharpe **0.75**（+12% vs XLU-011 0.67），
          cum +13.26%（5 TP +3.00%、1 SL -4.10%、1 Expiry +1.88%）
  Part B: 4 訊號 WR 75.0%，Sharpe **1.59**（+2% vs XLU-011 1.56），
          cum +9.05%（3 TP +3.00%、1 Expiry -0.20%）
  min(A,B) **0.75**（+12% vs XLU-011 0.67）★

  目標達成度：
    - Sharpe > XLU-011 最佳: ✓ 0.75 > 0.67
    - A/B cum 差距 < 30%: ✗（31.7%）— 略高於目標，但 vs baseline 33.4% 改善
    - A/B 訊號比 < 1.5:1: ✗（1.75:1）— XLU-011 訊號流結構性 7:4

  關鍵改善：
    - 2019-11-08 訊號從原 TP +2.50%（5 日）變為 Expiry +1.88%（20 日）
    - 2024-06-14 / 2024-11-04 / 2025-03-05 三筆 TP 從 +2.50% 升級至 +3.00%
    - 2021-09-20 SL 維持 -4.10%（無新增 SL/cooldown shift）
    - 2024-01-18 Expiry 維持 -0.20%（保留 Part B 變異源，避免 zero-var）

  解讀：XLU-011 的 ATR(5)/ATR(20) > 1.15 過濾使訊號天然帶有強動能，原 TP +2.5%
  截斷部分仍在反彈中的交易。加寬至 +3.0% 捕捉更深反彈（同時保留 SL -4.0%
  風險邊界）。**這驗證 cross_asset 規則**：MR 框架疊加 ATR 動能過濾後，
  TP 應採突破型 +3.0% 而非 MR 標準 +2.5%。

  失敗 → 成功路徑（負面知識）：Att1/Att2 證實 2DD 過濾在 XLU 上無區分力，
  將 Part B 退化為 zero-var。Att3 移除 2DD 過濾後，「TP +3.0% / ATR>1.15
  過濾」單獨組合即達成 Sharpe 改善。

========================================================================
最終配置（Att3）：
- 進場：同 XLU-011（pullback 3.5-7% + WR(10)<=-80 + ClosePos>=0.4 + ATR>1.15）
- 出場：TP **+3.0%**（核心創新，加寬自 XLU-011 的 +2.5%）/ SL -4.0% / 20 天
- 冷卻：7 天
- 2DD 過濾：停用（Att1/Att2 驗證 CIBR 方向在 XLU 失敗）

跨資產貢獻：
- 擴展 lesson #6（確認指標邊際效益遞減）：2DD cap/floor 在 1.08% vol 利率敏感
  ETF 上對 winners/losers 無區分力（2DD 維度分布重疊）
- 擴展 lesson #20b 失敗家族：2DD 區間過濾加入 oscillator-hook / day-after /
  signal-day secondary filter 失敗類別，確認在「規範閘門已捕捉 panic 動能（ATR）
  的低-中波動 ETF」上 2DD secondary filter 結構性失效
- **新發現**：MR 框架 + ATR(5)/ATR(20) > 1.15 動能濾波後，TP 應採突破型 +3.0%
  甜蜜點而非標準 MR +2.5%。挑戰原 cross_asset 規則「TP +2.5% 為 MR 甜蜜點」
  的普適性——當 MR 框架疊加動能濾波，TP 上限可隨之擴張
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU012Config(ExperimentConfig):
    """XLU-012 Post-Capitulation Vol-Transition MR 參數 (Att3 final)"""

    # 進場 — 回檔（同 XLU-011）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035
    pullback_cap: float = -0.07

    # 進場 — Williams %R（同 XLU-011）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（同 XLU-011）
    close_position_threshold: float = 0.4

    # 進場 — 波動率自適應過濾（同 XLU-011）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 進場 — 2DD 區間過濾（Att3 結論：停用）
    # Att1/Att2 證實 CIBR 方向 2DD cap 在 XLU 上無區分力且使 Part B zero-var
    # Sentinel for disabled:
    #   drop_2d_floor = +1.0 → cond `Return_2d <= +1.0` 永真
    #   drop_2d_cap   = -1.0 → cond `Return_2d >= -1.0` 永真
    drop_2d_floor: float = 1.0
    drop_2d_cap: float = -1.0

    # 冷卻期（同 XLU-011）
    cooldown_days: int = 7


def create_default_config() -> XLU012Config:
    return XLU012Config(
        name="xlu_012_vol_transition_mr",
        experiment_id="XLU-012",
        display_name="XLU Post-Capitulation Vol-Transition MR",
        tickers=["XLU"],
        data_start="2010-01-01",
        # Att3 最終配置：TP +3.0%（核心創新，加寬自 XLU-011 +2.5%）
        profit_target=0.030,
        stop_loss=-0.040,
        holding_days=20,
        drop_2d_floor=1.0,
        drop_2d_cap=-1.0,
    )
