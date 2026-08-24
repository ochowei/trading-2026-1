"""
TSLA DXY 5d Direction Filter on TSLA-QQQ Cross-Asset Divergence BB Squeeze Breakout (TSLA-018)

實驗動機 (Motivation)：
- TSLA-017 Att3 為當前全域最優（min(A,B) 0.96，Part A 1.17 / Part B 0.96，
  Part B 5/4W/1EX 結構），TSLA-QQQ 20d divergence -0.5% 已乾淨切除 Part A 全部
  losers + Part B 2025-11-03 SL，**剩餘 Part B binding 為 1 筆 expiry trade**
  （未到 TP 也未碰 SL，Sharpe 提升靠進一步刪除非優質 EX 訊號或降低 winners 變異）。
- TSLA AI_CONTEXT 列出未來突破方向：「^VXN forward-looking IV、^VIX BANDS、
  TSLA-QQQ vs SPY benchmark 對比測試」。本實驗測試 **DXY (US Dollar Index)
  direction filter** 為新方向（lesson #24 family v7 候選 spot FX direction 變體）。
- TSLA 國際營收 occupy ~50%（2024Q4：中國 ~30%，歐洲 ~15-20%，其他 ~5%）；
  USD 強勢期外幣營收折換損失 + 利率敏感成長股估值壓縮使 TSLA 在 DXY 急升期
  系統性受壓——hypothesis：DXY 5d 急升環境下 BB Squeeze 突破多為「macro stress
  driven false breakouts」，與 TSLA 自身基本面動能脫鉤。

嘗試方向（**repo 首次 DXY direction filter 應用於高波動 AI 個股 + BB Squeeze
Breakout 框架**，cross-asset port from GLD-016 / COPX-016）：
**TSLA - QQQ divergence 已過濾「相對弱勢 regime」, DXY 直接過濾「macro USD-strength
shock regime」**——二者正交（前者為 cross-asset relative performance, 後者為 spot FX
maximally-different macro factor）。

設計理念（trade-level analysis hypothesis on TSLA-017 Att3）：
  - Part A 殘餘 weakness 集中於 USD-surge 期：
    * 2022 bear（Fed hike cycle）→ DXY 從 95 急升至 110+, 5d change >2%
    * 2021 Q3 chip shortage 對 EV 供應鏈打擊 + USD 反彈
    * 2024 Q4 election + 寬幅 Fed re-pricing → DXY 11月急升
  - Part B 殘餘 1 筆 expiry：可能落於 USD 中性或弱勢期（未必受 DXY filter 影響）
  - Hypothesis：DXY 5d cap <= +2.0% 過濾 USD-surge 訊號，保留 calm/weak USD 訊號

與 TSLA-017 的明確區分（lesson #20 v3 family + lesson #24 family 邊界擴展）：
- TSLA-017：跨資產**相對表現**（cross-asset divergence regime classifier）
- TSLA-018：跨資產**絕對 macro factor**（spot FX direction filter）
- 二者捕捉不同 regime 維度，疊加為 dual-regime gate（前者排除「TSLA 嚴重落後 QQQ」，
  後者排除「USD 急升 macro stress」）

與 lesson #5「趨勢濾波器+均值回歸=災難」明確區分：
- lesson #5 boundary：same-asset 自身方向過濾於 MR 框架失效
- 本實驗：(a) 進場為 breakout 而非 MR、(b) DXY 為跨資產 macro classifier 而非
  TSLA 自身方向過濾、(c) 沿用 TLT-014 / GLD-016 / COPX-016 cross-asset
  divergence regime gate 的合法性論證

================================================================================
迭代計畫（最多三次）
================================================================================

Att1 (max_dxy_change=+2.0%, dxy_lookback=5)：
  - 直接移植 GLD-016 Att1 sweet spot（DXY 5d cap <= +2.0%）
  - Hypothesis：過濾 2022 Fed-hike SLs 與 2024 election surge SLs
  - 預期：Part A 過濾 1-2 筆 SL（DXY 5d > +2%），Part B 不變或微減
  - 接受標準：min(A,B) > 0.96，A/B cum gap < 30%, signal gap < 50%

Att2 (max_dxy_change=+1.0%, dxy_lookback=5)：
  - 收緊閾值至 +1.0%（GLD-016 Att2 收緊方向）
  - 觀察是否過嚴觸發 cooldown chain shift
  - 預期：可能過嚴誤殺 winners

Att3 (max_dxy_change=+1.5%, dxy_lookback=10)：
  - 改用 10d 維度（GLD-016 Att3 替代窗口）
  - 驗證 5d > 10d selectivity 假設
  - 預期：10d 較 noisy，可能 selectivity 較弱

================================================================================
跨資產假設（待驗證）
================================================================================
1. 若 DXY direction filter 在 TSLA 成功，可移植至其他 international-revenue
   高波動成長股（NVDA、AAPL、AMZN）;
2. 若 5d > 10d selectivity 結構成立，建議在其他 USD-sensitive equity 上
   優先測試 5d 維度（同 GLD-016 / COPX-016 pattern）;
3. lesson #24 family v7 spot FX direction filter 從商品/礦業 ETF 擴展至
   高波動 AI 個股的邊界驗證（可能成功也可能失敗——TSLA-QQQ divergence 與 DXY
   是否冗餘是核心問題）.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA018Config(ExperimentConfig):
    """TSLA-018 DXY 5d Direction Filter on TSLA-017 Att3 BB Squeeze Breakout 參數

    迭代計畫：
      Att1: DXY 5d cap <= +2.0%（GLD-016 sweet spot 直接移植）
      Att2: DXY 5d cap <= +1.0%（收緊變體）
      Att3: DXY 10d cap <= +1.5%（替代窗口）
    """

    # === BB Squeeze Breakout 基礎（同 TSLA-017 Att3 = TSLA-015 Att3）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === Same-Asset Multi-Week Trend Regime（同 TSLA-017 Att3 buffered SMA）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.99

    # === Cross-Asset Divergence Regime Gate（同 TSLA-017 Att3）===
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    min_relative_return: float = -0.005

    # === DXY Direction Filter（TSLA-018 核心新增）===
    # ticker: ICE US Dollar Index spot via Yahoo finance "DX-Y.NYB"
    # lookback: 5 日（GLD-016 / COPX-016 sweet spot 一致；5d > 10d selectivity）
    # max_dxy_change: DXY N 日變化必須 <= 此值
    # Att1 (max=+0.020, 5d): TIE baseline，全 15 訊號 DXY 5d ≤ +2.0% non-binding
    # Att2 (max=+0.010, 5d): REJECT min 0.77 — reverse selection 移除 2025-05-12
    #   winner 但保留 2024-09-23 SL（USD weakening 期間發生）
    # Att3 (max=+0.025, 10d): 替代窗口測試（5d → 10d），驗證更長 lookback 是否
    #   能捕捉 sustained USD-weakening regime（2024-09-23 SL 之 DXY 10d 預期負向）
    dxy_ticker: str = "DX-Y.NYB"
    dxy_lookback: int = 10
    max_dxy_change: float = 0.025


def create_default_config() -> TSLA018Config:
    return TSLA018Config(
        name="tsla_018_dxy_direction_breakout",
        experiment_id="TSLA-018",
        display_name="TSLA DXY Direction Filter on TSLA-QQQ Divergence BB Squeeze Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
