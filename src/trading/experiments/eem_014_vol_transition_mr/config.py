"""
EEM Post-Capitulation Vol-Transition 均值回歸配置 (EEM-014)

動機：CIBR-012 Att3（2026-04-21）首次驗證「2 日急跌上限（2DD cap）」方向，
於 BB 下軌+回檔上限混合進場框架上使 min(A,B) 0.39→0.49（+26%）。
CIBR-012 跨資產假設明確列舉 EEM 為候選對象：

  "2DD cap filter may extend to other US sector ETFs / low-mid vol ETFs
  (XBI, XLU, IWM, COPX, VGK, **EEM**) using BB lower + cap hybrid pattern —
  especially those with Part A crash-day SL failures."

EEM-012 Att3（基線 min 0.34）的 Part A 殘餘停損（signal-day 2DD）：
  - 2021-07-08: SL, 2DD -2.19%（DiDi ADR 監管衝擊第一日）
  - 2021-11-30: SL, 2DD +0.29%（Omicron 恐慌淺幅震盪）
  Part B: 2025-11-19 SL, 2DD -0.85%（美中貿易摩擦升溫）

TPs signal-day 2DD 分布：-1.47%, -3.36%, -1.79%, -3.10%, -3.88%, -1.95%, -2.37%
（最淺 -1.47%，中位 -2.37%）

關鍵跨資產發現（EEM vs CIBR 2DD 分布方向相反）：
- CIBR 失敗 SL：深 2DD（-4% 以下，崩盤加速中）
- EEM 失敗 SL：**淺** 2DD（中位 -0.85%，非真正 capitulation，慢漂移）
- EEM 正確方向：2DD **floor**（要求下跌深度），非 2DD **cap**（排除深跌）

========================================================================
三次迭代記錄（2026-04-21，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1：直接移植 CIBR-012 方向（2DD cap >= -3.0%，= 2.6σ for 1.17% vol）
  Part A: 4 訊號 50.0% WR Sharpe **-0.02** cum -0.39%（崩壞 vs 基線 0.34）
  Part B: 3 訊號 66.7% WR Sharpe 0.34 cum +2.80%
  min(A,B) -0.02（-106% vs EEM-012 Att3 的 0.34）
  失敗分析：CIBR 2DD cap 方向移除 EEM 的 TP（2021-07-26 2DD -3.36%、
  2021-09-20 2DD -3.10%、2024-01-17 2DD -3.88%、2024-04-16 2DD -1.95%）
  而保留 SL（2021-07-08 -2.19%、2021-11-30 +0.29%、2025-11-19 -0.85%）。
  EEM 的 TP 集中於深 2DD 反彈，SL 集中於淺 2DD 漂移 — 方向必須反轉。

Att2 ★（全域最佳）：改用 2DD floor -0.5%（要求 2 日至少下跌 0.5%）
  Part A: 5 訊號 80.0% WR Sharpe **0.73** cum +9.06%（+115% vs 基線）
  Part B: 4 訊號 75.0% WR Sharpe 0.56 cum +5.89%（同基線）
  min(A,B) **0.56**（+65% vs EEM-012 Att3 的 0.34）
  A/B cum 差 3.17pp（遠優於 <30% 要求）
  A/B 訊號比 1.25:1（遠優於 <50% 要求）
  過濾動態：
  - 僅過濾 1 筆訊號：2021-11-30 SL（2DD +0.29% > -0.5% → 過濾）
  - 保留 2021-07-08 SL（-2.19% < -0.5%）與 2025-11-19 SL（-0.85% < -0.5%）
  - 全部 7 筆 TP 保留（皆 < -1.4%，遠於門檻）
  解讀：EEM 的「淺 2DD」訊號缺乏 capitulation 動能，-0.5% floor 精準過濾
  弱 MR 訊號而不影響真實 capitulation 反彈。

Att3 ablation：Att2 - ATR 過濾（atr_ratio_threshold = 0.0 停用）
  Part A: 8 訊號 50.0% WR Sharpe **-0.02** cum -0.77%（崩壞）
  Part B: 4 訊號 75.0% WR Sharpe 0.56 cum +5.89%（Part B 不受影響）
  min(A,B) -0.02
  證明：移除 ATR 後 Part A 新增 3 筆 SL（8-5=3），ATR > 1.10 與 2DD floor
  為**互補雙過濾**而非冗餘 — ATR 捕捉 signal-day panic，2DD floor 排除
  淺幅漂移。兩者疊加對 EEM 必要，Att2 為最優配置。

========================================================================
最終配置（Att2）：EEM-012 Att3 所有條件 + 2DD floor <= -0.5%
========================================================================
- BB(20, 2.0) 下軌
- 10 日回檔上限 -7%
- WR(10) <= -85
- ClosePos >= 40%
- ATR(5)/ATR(20) > 1.10
- **2 日收盤報酬 <= -0.5%（Att2 核心創新）**
- TP +3.0% / SL -3.0% / 20 天 / 冷卻 10 天

跨資產貢獻：
- Repo 第 2 次「2DD floor 方向」正式成功驗證（繼 USO-013 後，broad EM ETF 首次）
- 擴展 lesson #19：2DD floor/cap 方向取決於失敗 SL 的 2DD 結構，非通用規則
  - CIBR: 深 2DD SL → cap 方向
  - EEM: 淺 2DD SL → floor 方向
- 擴展 lesson #52（混合進場模式）：EEM 進一步受益於 2DD floor 精煉

EEM 特有限制（lesson #49 / EEM-012，已遵守）：
- SL -3.0%（未超 -3.5% 上限）
- TP +3.0%（符合上限）
- 回檔上限 -7%（符合 -8% 內）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM014Config(ExperimentConfig):
    """EEM-014 Post-Capitulation Vol-Transition MR 參數"""

    # BB 參數（同 EEM-012 Att3）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（同 EEM-012 Att3）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    # 品質過濾（同 EEM-012 Att3）
    wr_period: int = 10
    wr_threshold: float = -85.0
    close_position_threshold: float = 0.40

    # ATR 當日過濾（Att2 最終配置，Att3 ablation 驗證此門檻必要）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # 2 日急跌過濾（Att2 改用 2DD floor 方向，對 EEM 為正確方向）
    #
    # Att1 失敗驗證（2026-04-21）：直接移植 CIBR-012 2DD cap 方向（require 2DD >= -3.0%）
    # 在 EEM 上 Part A Sharpe 0.34→-0.02（崩壞），因 EEM SL 訊號結構與 CIBR 相反。
    # CIBR 的失敗 SL 集中於深 2DD（≤-4%，崩盤加速中）；EEM 的失敗 SL 卻集中於
    # 淺 2DD（2021-11-30 +0.29% / 2025-11-19 -0.85% / 2021-07-08 -2.19%，中位 -0.85%）,
    # 代表 EEM 的失敗模式為「淺幅慢漂移，未真正 capitulation」而非「崩盤加速中」。
    # TPs 集中於 2DD -1.47% ~ -3.88%（真正急跌後反彈），故應加 floor 而非 cap。
    #
    # Att2 新方向：require 2DD <= -0.5%（2DD floor，排除「淺幅慢漂移」的弱 MR 訊號）
    # 此為 CIBR-004 方向（2DD floor）的跨資產驗證，非 CIBR-012 方向（2DD cap）。
    # 標準解讀：EEM 的 MR 需要先有真正的 2 日急跌作為「capitulation confirmation」，
    # 信號日若 2DD 太淺則不具備 MR 能量。
    twoday_return_floor: float = -0.005

    # 冷卻期（同 EEM-012 Att3）
    cooldown_days: int = 10


def create_default_config() -> EEM014Config:
    return EEM014Config(
        name="eem_014_vol_transition_mr",
        experiment_id="EEM-014",
        display_name="EEM Post-Capitulation Vol-Transition MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
