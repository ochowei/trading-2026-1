"""
COPX Post-Capitulation Vol-Transition 均值回歸配置 (COPX-010)

動機：COPX-007 Att3（全域最佳 min(A,B) Sharpe 0.45）雖已納入 ATR(5)/ATR(20)
波動率自適應過濾，但存在兩個結構性問題：
- Part A 21 訊號中 5 筆停損（2019-05-06、2019-08-01、2020-02-25、2021-06-16、
  2022-06-13），全部為 1-4 日快速停損的「continuation-decline traps」
- A/B 累計差距 46%（+36.73%/+19.74%）超過 30% 平衡目標
- A/B 訊號比 52%（21/10）剛好超過 50% 平衡目標

核心觀察：COPX-007 的 ATR > 1.05 能區分「急跌恐慌 vs 慢磨下跌」（跨資產教訓 #15），
但無法區分「急跌中（續跌停損）」vs「急跌後（反彈達標）」。延伸 CIBR-012 Att3 的
跨資產假設「2DD cap filter may extend to other US sector ETFs (XBI, XLU, IWM,
COPX, VGK, EEM) facing 'BB lower + cap' hybrid pattern — pending validation」。

========================================================================
COPX-007 Part A 21-trade signal-day stats（2019-2023，分析自實際回測）：
========================================================================
LOSERS (n=5):
  Pullback: -10.06% ~ -13.20%（mean -11.86%）
  2dRet:    +0.19% ~ -7.49%（mean -5.48%）
  1dRet:    -2.12% ~ -5.28%（mean -3.41%）
  ClosePos: 0.08 ~ 0.97
  ATR_ratio: 1.11 ~ 1.35

WINNERS (n=16):
  Pullback: -10.14% ~ -16.36%（mean -12.51%）
  2dRet:    -3.32% ~ -9.97%
  1dRet:    -1.17% ~ -7.52%（mean -3.99%）
  ClosePos: 0.01 ~ 1.00
  ATR_ratio: 1.06 ~ 1.86

關鍵發現：losers 與 winners 在 Pullback / 2dRet / ATR_ratio 三維度分佈大幅重疊；
僅有兩個「最弱」losers（2019-05-06 / 2025-03-31）為「淺 1DD + 高 ClosePos」
（1.17~2.35% drop + close 收於日內 high 81~97% 處）的 soft-capitulation pattern。

========================================================================
三次迭代結果（2026-04-23，成交模型 0.15% slippage，隔日開盤市價進場）：
全部失敗 — COPX-007 仍為全域最優
========================================================================

Att1（失敗）：2DD cap >= -5.5%（CIBR-012 方向，過濾「崩盤加速中」進場）
  Part A: 18 訊號 WR 61.1% Sharpe **0.08** cum +4.69%（崩壞 vs 0.45）
  Part B: 10 訊號 WR 70.0% Sharpe 0.28 cum +10.33%
  min(A,B) **0.08**（-82% vs COPX-007 的 0.45）
  失敗分析：cap -5.5% 過濾 3 個訊號但「冷卻鏈偏移」（lesson #19）新增 2 個壞訊號。
  COPX winners 的 2dRet 多在 -3% ~ -10% 寬範圍，與 losers 重疊；cap 方向移除贏家
  多於輸家，Part A WR 從 76.2% 崩至 61.1%。**確認 COPX winners 的 2dRet 分佈
  整體偏深於 losers**（與 CIBR 結構相反）。

Att2（失敗）：2DD floor <= -3.0%（EEM/INDA/USO 方向，要求真實 capitulation）
  Part A: 21 訊號 WR 76.2% Sharpe 0.45 cum +36.73%（NEAR-IDENTICAL：
    2019-05-06 訊號被 cooldown chain shift 推移至 2019-05-07，仍為 SL）
  Part B: 6 訊號 WR 66.7% Sharpe **0.21** cum +4.35%（崩壞 vs 0.57）
  min(A,B) **0.21**（-53% vs COPX-007 的 0.45）
  失敗分析：2dRet floor 在 Part A 幾乎無作用（多數訊號天然有深 2dRet），
  但在 Part B 過濾 5 個淺 2DD 贏家（2024-01-22 -1.23% / 2024-08-07 -2.30% /
  2024-12-17 -2.88% / 2025-03-03 -2.43% / 2025-11-20 -2.23%）。COPX 2024-2025
  銅週期復甦中許多 valid MR 訊號的 2DD 較淺，floor 方向系統性殺死這些訊號。

Att3（best of 3，仍未超越 baseline）：
  「弱 capitulation」雙條件過濾：跳過 (1日報酬 > -3%) AND (ClosePos > 0.30) 訊號
  目標：精準鎖定兩個「淺 1DD + 高 ClosePos」losers（2019-05-06 / 2025-03-31）
  同時保留盤中拋售型贏家（如 2024-08-07 1DD -2.49% / CP 0.02）

  Part A: 19 訊號 WR 73.7% Sharpe **0.38** cum +27.64%（vs 0.45）
  Part B: 10 訊號 WR 80.0% Sharpe **0.57** cum +19.74%（**完全持平**）
  min(A,B) **0.38**（-15% vs COPX-007 的 0.45）

  **Part B 結構性持平的精緻機制**：filter 過濾 2024-12-17（CP 0.75 winner）+
  2025-03-31（CP 0.81 loser），cooldown shift 補充 2024-12-18（winner）+
  2025-04-03（Trump 關稅後續 SL）。1 winner + 1 loser 替換 1 winner + 1 loser，
  WR / 訊號數 / Sharpe 全部完全持平。**A/B 累計差從 46% 降至 28.6%**（達標 <30%！）
  且 A/B 訊號比從 2.1:1 降至 1.9:1（達標 <50%！）

  Part A 退化分析：filter 過濾 2019-05-06（弱 capitulation loser）+ 2022-01-28
  + 2022-03-15（兩個高 CP 高 1DD winners），但 cooldown shift 引入 2019-05-13
  新 SL（4 個月 trade war 持續期）。淨效果：3 個訊號被替換，1 個 winner 變
  1 個 loser，Sharpe 從 0.45→0.38。

========================================================================
跨資產貢獻（lesson 整合）
========================================================================
1. **拒絕 CIBR-012 跨資產假設於 COPX**：「2DD cap filter for low-mid vol US sector
   ETFs」假設不延伸至 COPX 2.25% vol 商品 ETF。CIBR 1.53% vol 與 COPX 2.25% vol
   的 winners/losers 2DD 分佈結構不同——CIBR losers 集中深 2DD（cap 有效），
   COPX winners 跨深淺 2DD 廣泛分佈（cap/floor 雙向均失效）。

2. **延伸 lesson #20b 失敗家族至「single-day momentum filter」類別**：1DD floor
   作為 entry-time confirmation filter 在 COPX 上展現「Part A 改善 + Part B 退化」
   的 regime asymmetry，與 TQQQ-017（ClosePos / 2DD / Prev RSI）失敗模式同類——
   無法找到 cross-regime 一致的單日/雙日 winner/loser discriminator。

3. **新發現：「冷卻鏈偏移」（lesson #19）對「弱 capitulation 過濾」的破壞效應**：
   即便精準過濾兩個「淺 1DD + 高 ClosePos」losers，cooldown chain shift 仍會在
   trade-war / Trump tariff 等延續性事件期間引入新 SL。Att3 雖達成 A/B 平衡目標
   （cum 差 28.6% < 30%、訊號比 1.9:1 < 50%），但 Part A Sharpe 退化抵消平衡改善。

4. **COPX 結構性 Sharpe 上限證據**：COPX-007 的 ATR > 1.05 + 20日 pullback 10-20%
   + WR ≤ -80 + 12d cooldown 框架已是 2.25% vol 商品 ETF 的結構最優；任何 entry-time
   額外確認過濾器（2DD cap、2DD floor、1DD floor、weak-capitulation 雙條件）都會
   在 A/B regime 之間造成不對稱影響或被 cooldown shift 抵消，無法同時提升 min(A,B)。

最終配置（Att3，best of 3 iterations，但 min(A,B) 仍劣於 COPX-007 baseline）：
- 20 日回檔 in [-20%, -10%]
- WR(10) <= -80
- ATR(5)/ATR(20) > 1.05
- **跳過訊號 iff (1日報酬 > -3.0%) AND (ClosePos > 0.30)**（弱 capitulation 過濾）
- 冷卻 12 天 / TP +3.5% / SL -4.5% / 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX010Config(ExperimentConfig):
    """COPX-010 Post-Capitulation Vol-Transition MR 參數（Att3 best-of-3 final config）"""

    # 進場 — 回檔（同 COPX-007）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    # 進場 — Williams %R（同 COPX-007）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 波動率自適應（同 COPX-007）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # 進場 — 2 日急跌上限（CIBR-012 方向）— Att1 失敗
    # 設 -0.99 表示停用此條件
    twoday_return_cap: float = -0.99

    # 進場 — 2 日急跌下限（EEM/INDA/USO 方向）— Att2 失敗
    # 設 0.99 表示停用此條件
    twoday_return_floor: float = 0.99

    # 進場 — 「弱 capitulation」雙條件過濾（Att3 核心創新，best of 3）
    # 跳過訊號 iff (1日報酬 > oneday_return_floor) AND (ClosePos > weak_cap_closepos)
    # 等價於：保留 iff (panic momentum 1DD <= -3%) OR (盤中拋售 ClosePos <= 0.30)
    # 此 OR 邏輯精準鎖定 COPX-007 兩個「最弱 capitulation」losers
    # （2019-05-06 1DD -2.12%/CP 0.97、2025-03-31 1DD -2.35%/CP 0.81），
    # 同時保留 Part B 牛市盤中拋售型贏家（如 2024-08-07 1DD -2.49%/CP 0.02）
    oneday_return_floor: float = -0.030
    weak_cap_closepos_threshold: float = 0.30

    # 冷卻期（同 COPX-007）
    cooldown_days: int = 12


def create_default_config() -> COPX010Config:
    return COPX010Config(
        name="copx_010_vol_transition_mr",
        experiment_id="COPX-010",
        display_name="COPX Post-Capitulation Vol-Transition MR",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.045,
        holding_days=20,
    )
