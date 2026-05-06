"""
COPX-013: Macro-Confirmed Vol-Adaptive Capitulation MR

策略方向：
- Base：COPX-007 vol-adaptive MR（min(A,B) Sharpe 0.45，A/B balance ✓）
- Add：SPY 10 日報酬 <= max_spy_return「broad-market macro context
  confirmation gate」
- Direction：lesson #25 cross-asset port from IWM-015 + cross-strategy
  port to commodity miners ETF（既有 lesson #25 僅驗證於 IWM 子板塊 ETF）

跨資產假設（待驗證）：
COPX 為銅礦 ETF，受全球工業景氣循環驅動。當 broad market（SPY）已 10 日下跌
時，COPX 的 deep capitulation 屬於 broad risk-off 的一部分，下跌動能多由全球
總經因素驅動，technical capitulation 後 mean-revert 機率高。當 SPY 10 日仍上
漲、COPX 反向深跌時，COPX 屬於「idiosyncratic decline」（中國需求疲軟、銅價
特定衝擊、地緣政治），與 broad market disconnect，續跌風險顯著高於 mean-revert
機率。

trade-level 證據（COPX-007 baseline，5 SL Part A + 2 SL Part B）：
- 2019-05-06 SL: SPY 10d +0.88%（broad up，COPX 中美貿易戰特定衝擊，續跌）
- 2019-08-01 SL: SPY 10d -1.34%（broad slightly down，COPX 8 月反彈失敗）
- 2020-02-25 SL: SPY 10d -6.58%（broad COVID 大跌，COPX 同步續跌）
- 2021-06-16 SL: SPY 10d +0.42%（broad up，COPX 銅價中國需求疲軟特定衝擊，續跌）
- 2022-06-13 SL: SPY 10d -9.70%（broad Fed 鷹派大跌，COPX 同步續跌）
- 2024-07-18 SL: SPY 10d +0.22%（broad calm，COPX 中國需求疲軟特定衝擊，續跌）
- 2025-03-31 SL: SPY 10d -1.07%（broad slightly down，COPX 關稅衝擊）

3 個 SL 落於 SPY 10d > 0% 區（broad up 期 COPX idiosyncratic decline）：
- 2019-05-06 / 2021-06-16 / 2024-07-18 — 占 7 個 SL 的 43%

Att1（SPY 10d <= 0%）：FAILED min(A,B) 0.42
- Part A: 20 sig / WR 80.0% / Sharpe 0.57 cum +43.39%
- Part B: 8 sig / WR 75.0% / Sharpe 0.42 cum +11.78%（cooldown chain shift
  引入新 SL 2024-07-22 替換 2024-07-18，且 3 winners 被過濾）

Att2（SPY 10d <= -1.5%，IWM-015 sweet spot）：FAILED min(A,B) 0.42
- Part A: 16 sig / WR 75.0% / Sharpe 0.42 cum +24.95%（-1.5% 閾值過嚴切除
  6 個 Part A winners 在 -1.5%~0 中性帶）
- Part B: 6 sig / WR 83.3% / Sharpe 0.71 cum +13.26%（Part B 改善 +25% vs
  baseline 0.57；過濾 2024-07-18 SL + chain shift 引入 2025-04-04 替換 2025-03-31）
- A/B 平衡 ✓（cum gap 24.7% < 30%, signal ratio 1.07:1）但 Part A 退化使 min 不變

Att3（SPY 10d <= 0 AND VIX 3d <= +5，雙來源 lesson #24 + #25 組合）：FAILED min 0.06
- 嘗試以 ^VIX 3d direction filter 補強 Att1，過濾 panic-acceleration false-bottom
- 雙閘門組合理論上覆蓋全部 7 SLs（5 Part A + 2 Part B 中 1 個）
- 結果：cooldown chain shift 災難性放大——過濾 9 winners 後解除多個 cooldown
  lockouts，激活原本被壓制的 5 個新 Part A SLs（含 2 連續 SLs 模式）
- Part A: 15 sig / WR 60.0%（!!） / Sharpe 0.06 cum +2.49%（嚴重退化）
- Part B: 8 sig / WR 75.0% / Sharpe 0.42（Att1 同樣的 chain shift 模式）
- 教訓：當基礎策略 cooldown 12 日且原始訊號密度 ~4/yr，疊加多重 macro filter
  使被過濾訊號占比超過 ~50% 時，cooldown chain shift 結構性激活更多 SL，
  filter selectivity 完全反轉

================================================================================
Acceptance criteria（vs current global best COPX-011 Att3 min 0.64）：
================================================================================
- Sharpe min(A,B) > 0.64 ✓（目標）
- A/B 累計報酬差 < 30%
- A/B 訊號數差 < 50%
- 使用成交模型（next_open_market + 0.15% slippage + 悲觀認定）
- Repo 較少使用方向：lesson #25 cross-asset 從 IWM-015 至 commodity miners
  ETF（既有 lesson #25 僅 2 次驗證 IWM 成功 / XBI 失敗，第 3 次跨資產試驗）

成交模型：
- 進場：next_open_market（隔日開盤市價）
- TP 出場：limit_order Day（當日限價單）
- SL 出場：stop_market GTC（持倉期間停損市價）
- 到期出場：next_open_market
- 滑價：0.15%（ETF 中等流動性）
- 悲觀認定：是
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX013Config(ExperimentConfig):
    """COPX-013 Macro-Confirmed Vol-Adaptive Capitulation MR 參數"""

    # === 進場條件（同 COPX-007 vol-adaptive MR baseline）===
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10  # 回檔 >= 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 12

    # 波動率自適應過濾器（同 COPX-007 Att3 sweet spot）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # === COPX-013 核心新增：dual-source forward-looking macro filter ===
    # (1) SPY broad-market macro context confirmation gate（lesson #25 source）
    # (2) ^VIX direction cap（lesson #24 family forward-looking IV direction）
    #
    # Att1：max_spy_return = 0.0 (loose) → REJECT min 0.42（chain shift Part B）
    # Att2：max_spy_return = -0.015 → REJECT min 0.42（Part A 過嚴退化）
    # Att3：SPY 10d <= 0 AND VIX 3d <= +5 → REJECT min 0.06（chain shift 災難）
    #
    # Default 設為 Att3 參數（最後一次迭代狀態，符合 NVDA-015 慣例）
    macro_ticker: str = "SPY"
    macro_lookback: int = 10
    max_spy_return: float = 0.0
    # ^VIX forward-looking macro vol direction filter（lesson #24 cross-asset port）
    vix_ticker: str = "^VIX"
    vix_direction_lookback: int = 3
    max_vix_change: float = 5.0


def create_default_config() -> COPX013Config:
    return COPX013Config(
        name="copx_013_macro_confirmed_mr",
        experiment_id="COPX-013",
        display_name="COPX Macro-Confirmed Vol-Adaptive Capitulation MR",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 COPX-007 baseline）
        stop_loss=-0.045,  # -4.5%（同 COPX-007 baseline）
        holding_days=20,  # 20 天（同 COPX-007 baseline）
    )
