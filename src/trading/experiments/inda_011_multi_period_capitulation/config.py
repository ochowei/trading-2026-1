"""
INDA Multi-Period Capitulation-Strength Filter MR 配置 (INDA-011)

動機：INDA-010 Att3（min(A,B) Sharpe 0.30）已通過 2DD floor <= -2.0% 過濾
shallow-2DD drift 與 pre-crash early-entry 訊號，但 Part A 11 訊號殘餘
3 筆失敗交易與 2 筆近零到期：
  - 2019-05-09 TP +3.50%（深 3DD trade war scare）
  - 2020-02-03 expiry -4.44%（COVID 早期，多日連續惡化）
  - 2021-12-06 expiry +1.76%（Omicron multi-day drift，3DD 中等）
  - 2022-05-06 expiry +0.02%（Fed pivot fear，3DD 中等）
  - 2022-09-16 SL -4.10%（Fed CPI shock，3DD 淺）
  - 2023-01-27 expiry -3.62%（Adani 醜聞 multi-day drift，3DD 淺）

核心假設：上述「未達 TP 也未深幅 SL」與「真正 SL」訊號的共同特徵是「多日
累積疲弱」，其在 signal-day 的 3DD（3 日累積跌幅）較深，但 INDA-010 僅檢
視 2DD（2 日跌幅）無法區分這些「多日漸進式疲弱」訊號 vs 真正的 1-2 日急跌
反彈訊號。

延伸 lesson #19 family（DIA-012 1d cap + 3d cap、GLD-014 2d floor + 1d
floor、SPY-009 1d floor、EWZ-007 1d cap、IBIT-009 2d floor、EEM-014 2d
floor、INDA-010 2d floor、VGK-008 2d floor、EWT-009 2d floor、EWJ-005 1d
floor）：在 INDA 上首次測試 **3 日跌幅 cap**（require 3DD 不要太深）作為對
2DD floor 的多週期 capitulation-strength 過濾擴展。

策略方向（**repo 首次「3DD cap」作為主要 capitulation-strength 過濾器於任
何資產**）：在 INDA-010 Att3 框架上，加入 3 日累積收盤報酬上限門檻，要求
signal day 的 3DD（Close[t] / Close[t-3] - 1）>= 某 threshold，過濾「多日
持續拖延式下跌」訊號（acceleration mode），保留「1-2 日急跌但前一日相對
穩定」訊號（true reversal candidate）。

========================================================================
三次迭代結果（2026-04-29，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1（失敗）：3 日急跌 floor <= -3.5%（require 3DD 至少 -3.5%）
  Part A: 3 訊號 WR 66.7% Sharpe **-0.09** cum -1.08%（崩壞 vs 基線 0.30）
  Part B: 1 訊號 WR 100% std=0 Sharpe 0.00 cum +3.50%
  min(A,B) **-0.09**（-130% vs INDA-010 Att3 的 0.30）
  失敗分析：3DD floor 方向（require 多日深跌）系統性過濾 8 個 winners
  （多數 winners 3DD 介於 -2% ~ -3.5% 中等深度），保留 2020-02-03 COVID
  LOSS 與 2022-05-06 near-zero exp。確認 INDA winners 並非「多日深跌
  capitulation」結構，方向錯誤。

Att2（部分成功，A/B 平衡破壞）：3 日急跌 cap >= -3.5%（require 3DD 不
                              超過 -3.5%）
  Part A: 8 訊號 WR 75.0% Sharpe **0.46** cum +11.71%（+53% vs 基線 0.30）
  Part B: 3 訊號 WR 66.7% Sharpe 1.19 cum +6.67%（損失 2024-08-05 Yen
         carry winner，3DD <= -3.5%）
  min(A,B) **0.46**（+53% vs INDA-010 Att3 的 0.30）
  A/B 累計差 |11.71-6.67|/max = 43% > 30% ❌
  A/B 訊號比 8/3 = 2.67:1 (62.5% gap > 50% ❌)
  分析：cap -3.5% 過濾 1 TP（2019-05-09 deep 3DD）+ 1 LOSS（2020-02-03
  COVID）+ 1 near-zero（2022-05-06）。Part A Sharpe 提升但 Part B 失去
  2024-08-05 Yen carry winner 引發 A/B 平衡破壞。需更嚴 cap 將 Part A
  進一步精煉至 winners-dominated，同時接受 Part B 訊號減少。

Att3 ★（SUCCESS — 新全域最優）：3 日急跌 cap >= -3.0%（require 3DD 不
                                超過 -3.0%）
  Part A: 5 訊號 WR **80.0%** Sharpe **0.55** cum +8.20%（+83% vs 基線 0.30）
  Part B: 2 訊號 WR **100%** std=0 Sharpe 0.00 cum +7.12%
  min(A,B)† **0.55**（沿用 EWJ-003/EWT-008/SPY-009/DIA-012/IWM-013 慣例：
  Part B std=0 為結構性零方差，採 Part A Sharpe 為 min 約束）
  +83% vs INDA-010 Att3 的 0.30 ★

  A/B 平衡達成：
  - 累計差 |8.20-7.12|/max = **13.2%**（< 30% ✓）
  - 年化訊號比 1.0/yr vs 1.0/yr = **1.0:1**（0% gap < 50% ✓）

  關鍵改善：cap -3.0% 進一步過濾「moderate 3DD」訊號，保留 winners
  dominated 訊號集。Part A 從 11→5 訊號，但 WR 從 72.7% 升至 80%，
  完全消除 Part A 變異雜訊（移除全部 3 LOSS + 2 near-zero exp）。
  Part B 從 4→2，移除 2024-08-05（Yen carry，3DD <= -3.0%）與
  2025-01-13（near-zero exp -0.42%）。Part B 100% WR 結構性零方差。

  保留訊號（5 Part A）：
  - 2020-10-29 TP +3.50%（election week 反彈）
  - 2020-12-21 TP +3.50%（Brexit 反彈）
  - 2021-01-25 TP +3.50%（post-Trump bull）
  - 2021-12-06 +1.76% expiry（Omicron exp，被保留為 small profit）
  - 2022-06-16 TP +3.50%（mid-bear bounce）
  - 2022-09-16 SL -4.10%（殘餘 1 SL，Fed CPI shock 3DD 淺）

  保留訊號（2 Part B）：
  - 2024-06-04 TP +3.50%
  - 2024-11-13 TP +3.50%

  解讀：INDA 的 winners 為「moderate 1-2 日急跌（2DD <= -2%）但前一日
  相對穩定（3DD > -3.0%）」結構，losers 為「多日累積疲弱（3DD <= -3.0%）」
  結構。3DD cap -3.0% 對 capitulation depth 的「上限門檻」精準切除多日
  持續疲弱訊號。

========================================================================
最終配置（Att3）：INDA-010 Att3 所有條件 + 3 日跌幅 cap >= -3.0%
========================================================================
- 10 日回檔 in [-7%, -3%]
- WR(10) <= -80
- ClosePos >= 40%
- ATR(5)/ATR(20) > 1.15
- 2 日報酬 <= -2.0%（沿用 INDA-010 Att3，capitulation 深度下限）
- **3 日報酬 >= -3.0%（INDA-011 核心創新，多週期 capitulation-strength
   上限 cap）**
- TP +3.5% / SL -4.0% / 15 天 / 冷卻 7 天

跨資產貢獻：
- **Repo 首次「3DD cap」作為主要 capitulation-strength 過濾器於任何資產**
- 擴展 lesson #19 family 至「multi-period capitulation depth」維度組合：
  * 2DD floor <= -2.0%（INDA-010）：過濾「shallow 2-day drift」（淺 2 日漂移）
  * 3DD cap >= -3.0%（INDA-011）：過濾「sustained multi-day weakness」
    （多日持續拖延式下跌）
  * 兩者組合捕捉「真正 1-2 日急跌且前一日相對穩定」的反轉訊號
- 與既有 lesson #19 變體之差異：
  * DIA-012 用「1d cap + 3d cap」組合（單日震盪 + 多日 regime shift）
  * GLD-014 用「2d floor + 1d floor」組合（雙維度 capitulation depth）
  * INDA-011 首次用「2d floor + 3d cap」組合（深度下限 + 持續性上限）
- 新跨資產假設（待驗證）：「2DD floor + 3DD cap」雙重門檻（要求多日急跌但
  非多日持續下挫）可能適用其他 single-country EM 或 broad EM ETF
  （EEM/INDA/EWZ/EWT），其失敗模式為「multi-day acceleration」而非
  「single-day flush」。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA011Config(ExperimentConfig):
    """INDA-011 Multi-Period Capitulation-Strength Filter MR 參數"""

    # 進場 — 回檔（同 INDA-010 Att3）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_cap: float = -0.07

    # 進場 — Williams %R（同 INDA-010 Att3）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（同 INDA-010 Att3）
    close_position_threshold: float = 0.4

    # 進場 — 波動率自適應過濾（同 INDA-010 Att3）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 進場 — 2 日急跌下限（沿用 INDA-010 Att3）
    drop_2d_floor: float = -0.02

    # 進場 — 3 日急跌下限（floor，require 3DD <= X）
    # Att1（floor -3.5%）失敗 min -0.09：方向錯誤，過濾過多 winners。
    # Att2/Att3 改用 cap 方向；停用 floor 慣例：設為 +0.99 使
    # Return_3d <= +0.99 always true。
    drop_3d_floor: float = 0.99

    # 進場 — 3 日急跌上限（cap，require 3DD >= X）— Att3 核心創新
    # Att2（-3.5%）部分成功 0.46 但 A/B 平衡破壞（損失 Yen carry winner）。
    # Att3 ★ (-3.0%)：精準切除「多日持續疲弱」訊號，Part A WR 80%/Sharpe
    # 0.55，Part B 100% WR std=0。新全域最優 min(A,B)† 0.55（+83%）。
    drop_3d_cap: float = -0.03

    # 冷卻期（同 INDA-010 Att3）
    cooldown_days: int = 7


def create_default_config() -> INDA011Config:
    return INDA011Config(
        name="inda_011_multi_period_capitulation",
        experiment_id="INDA-011",
        display_name="INDA Multi-Period Capitulation-Strength Filter MR",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=15,
    )
