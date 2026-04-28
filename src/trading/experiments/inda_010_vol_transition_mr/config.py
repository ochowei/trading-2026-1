"""
INDA Post-Capitulation Vol-Transition 均值回歸配置 (INDA-010)

動機：INDA-005 Att3（全域最佳 min(A,B) Sharpe 0.23）為 repo 整體倒數第三低
（僅次於 TLT/USO），Part A 13 訊號中 2 筆停損（2019-07-31、2022-09-16 皆 -4.1%）
以及 1 筆到期重虧（2020-02-03 COVID -4.44%）均發生在「崩盤加速中」或「pre-crash
早期進場」時點。

核心假設：CIBR-012 Att3（2026-04-21）與 EEM-014 Att2（2026-04-21）分別驗證
2DD cap（深 2DD 過濾）與 2DD floor（淺 2DD 過濾）兩個相反方向。INDA 0.97%
vol 符合 CIBR-012 跨資產假設描述範圍（low-mid vol ETF with Part A crash-day
SL failures），應測試兩方向以找出 INDA 的失敗結構。

INDA-005 Att3 殘餘失敗訊號：
- Part A 虧損：
  - 2019-07-31 SL -4.10%（中美貿易戰第一波）
  - 2020-02-03 到期 -4.44%（COVID 前夕，2DD 中等約 -2.5%）
  - 2022-09-16 SL -4.10%（Fed 鷹派衝擊）
  - 2023-01-27 到期 -3.62%（Adani 醜聞期）
- Part B 虧損：
  - 2024-10-04 到期 -2.63%（外資流出）
  - 2025-02-18 SL -4.10%（印度後峰下跌 regime）

========================================================================
三次迭代結果（2026-04-21，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1（失敗）：INDA-005 Att3 框架 + 2DD cap >= -3.0%（CIBR-012 方向移植）
  Part A: 10 訊號 WR 60.0% Sharpe **0.08** cum +2.37%（崩壞 vs 基線 0.23）
  Part B: 5 訊號 WR 60.0% Sharpe 0.21 cum +3.29%
  min(A,B) **0.08**（-65% vs INDA-005 Att3 的 0.23）
  失敗分析：CIBR 方向（深 2DD = 崩盤加速）在 INDA 上與 EEM-014 Att1 同樣失敗。
  -3.0% cap 過濾了 2020-12-21 TP、2021-02-26 TP、2022-05-06 近零到期（共 3 個
  Part A），以及 2024-08-05 TP（Part B），但保留所有 Part A SL 與 COVID 到期。
  INDA 的 TP 集中於中等 2DD (-2% ~ -3%)，非深 2DD，cap 方向系統性移除贏家。

Att2（失敗）：放寬 2DD cap 至 -4.0%
  Part A: 11 訊號 WR 63.6% Sharpe **0.17** cum +5.95%（仍弱於基線 0.23）
  Part B: 7 訊號 WR 57.1% Sharpe 0.31 cum +6.46%（同基線）
  min(A,B) **0.17**（-26% vs 基線 0.23）
  失敗分析：-4.0% cap 僅過濾 2021-02-26 TP 與 2022-05-06 近零到期。關鍵發現：
  2020-02-03 COVID（到期 -4.44%）實際 signal-day 2DD 僅 -2.5% ~ -3.0%（pre-crash
  早期進場），2DD cap 無法捕捉，因為真正的 -4.4% 下跌發生在進場後的後續幾日。
  Part B 完全不變（INDA 2024-2025 無 2DD ≤ -4% 訊號），cap 方向不具選擇力。

Att3 ★（當前最佳）：改用 2DD floor 加深至 <= -2.0%，停用 cap
  Part A: 11 訊號 WR 72.7% Sharpe **0.30** cum +10.51%（+30% vs 基線 0.23）
  Part B: 4 訊號 WR 75.0% Sharpe **1.48** cum +10.41%（+377% vs 基線 0.31）
  min(A,B) **0.30**（+30% vs INDA-005 Att3 的 0.23）★
  A/B 累計差 0.10pp（vs 基線 3.22pp，幾乎消除）
  A/B 年化訊號比 1.1:1（Part A 2.2/yr, Part B 2.0/yr，優秀平衡）

  關鍵改善：
  - 過濾 Part A 2019-07-31 SL（貿易戰，淺 2DD 早期進場）
  - 過濾 Part B 2024-01-23 近 TP 到期（非真正 capitulation）
  - 過濾 Part B 2024-10-04 到期損失（淺 2DD）
  - 過濾 Part B 2025-02-18 SL（淺 2DD，非真正恐慌）
  - 代價：Part A 2023-03-15 TP 被過濾（淺 2DD 但後續 bounce 成功）

  解讀：INDA 的失敗模式為「shallow 2DD = early-in-decline 或 policy-driven slow
  drift」，非「deep 2DD = in-crash acceleration」。加深 2DD floor 同時過濾這兩種
  失敗類型，並保留「真正 capitulation 後的中等 2DD 反彈」訊號。與 EEM-014 Att2
  方向一致但門檻更深（EEM: -0.5%, INDA: -2.0%）— 因 INDA-005 基線已要求 -1.0%
  floor，需進一步加深才具選擇力。

========================================================================
最終配置（Att3）：INDA-005 Att3 所有條件 + 2DD floor 加深至 <= -2.0%
========================================================================
- 10 日回檔 in [-7%, -3%]
- WR(10) <= -80
- ClosePos >= 40%
- ATR(5)/ATR(20) > 1.15
- **2 日收盤報酬 <= -2.0%（Att3 核心創新，加深原基線 -1.0%）**
- TP +3.5% / SL -4.0% / 15 天 / 冷卻 7 天

跨資產貢獻：
- Repo 第 3 次「2DD floor 加深方向」成功驗證（繼 USO-013、EEM-014 後）
- 擴展 lesson #19：2DD floor 方向在 single-country EM（INDA policy/外資驅動）
  與 broad EM（EEM）上皆成功，顯示 EM ETF 失敗模式結構相似
- 擴展 lesson #20b：突破 INDA 0.23 天花板，證明 2DD 深度濾波可繞過 oscillator
  hook 失敗家族在 post-peak slow-melt regime 的限制
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA010Config(ExperimentConfig):
    """INDA-010 Post-Capitulation Vol-Transition MR 參數"""

    # 進場 — 回檔（同 INDA-005 Att3）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_cap: float = -0.07  # 回檔 <= 7%（崩盤隔離）

    # 進場 — Williams %R（同 INDA-005 Att3）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（同 INDA-005 Att3）
    close_position_threshold: float = 0.4

    # 進場 — 波動率自適應過濾（同 INDA-005 Att3）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 進場 — 2 日急跌下限（Att3 核心創新，加深自 INDA-005 Att3 的 -1.0%）
    # Att3：收緊至 -2.0% 測試 EEM-014 Att2 方向（require 更深 capitulation）
    # 直覺：INDA shallow-2DD 訊號常為 (a) pre-crash early entry（後續更大下跌）
    # 或 (b) post-peak slow-melt drift。加深 floor 同時過濾兩類失敗。
    drop_2d_floor: float = -0.02  # 2日報酬 <= -2.0%

    # 進場 — 2 日急跌上限（Att3 停用）
    # Att1 (-3.0%) / Att2 (-4.0%) 皆失敗：CIBR 方向移除 INDA TPs 多於 SLs
    # Att3 結論：INDA 失敗模式與 CIBR 結構相反，停用 cap，轉用 floor 方向
    drop_2d_cap: float = -0.99  # 非綁定（停用 cap）

    # 冷卻期（同 INDA-005 Att3）
    cooldown_days: int = 7


def create_default_config() -> INDA010Config:
    return INDA010Config(
        name="inda_010_vol_transition_mr",
        experiment_id="INDA-010",
        display_name="INDA Post-Capitulation Vol-Transition MR",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=15,
    )
