"""
NVDA-015: Multi-Week Regime-Aware Relative Strength Momentum Pullback

策略方向（Strategy Direction）：
    將 lesson #22「buffered multi-week SMA trend regime」+ ATR vol regime
    （NVDA-013 Att3 在 MBPC 框架的雙重 gate 突破）跨**策略類型**首次移植至
    NVDA-006 Relative Strength Momentum Pullback 框架。

動機（Motivation）：
    NVDA-013 Att3 將 lesson #22（trend regime）+ ATR vol regime 雙重 gate
    應用於 MBPC（Donchian breakout + 5d 淺回檔），把 NVDA-009 baseline
    min(A,B) 從 0.41 推到 0.55，為 NVDA 全域最佳。

    NVDA-006 Att1（RS Momentum Pullback）：
        Part A: 35 訊號, WR ?, Sharpe **0.47**, 累計 ~+90%
        Part B: 12 訊號, WR ?, Sharpe **0.64**
        min(A,B) 0.47, A/B 訊號比 1.17:1（極佳）
    NVDA-006 與 NVDA-009 MBPC 的訊號集**互補非冗餘**：RS 框架捕捉 NVDA
    跑贏板塊（SMH）超額表現後的回調，MBPC 捕捉 Donchian 突破後回檔；
    兩者於 Part A 訊號重合度低（NVDA-006 35 vs NVDA-009 34）。

    **Repo 第 1 次 lesson #22 跨策略類型移植至 RS Momentum 框架**：
    先前 lesson #22 成功僅於 BB Squeeze（TSLA-015 / NVDA-012 / FCX-013 /
    COPX-011）+ MBPC（NVDA-013）+ Pullback MR（XBI-015）三類框架，
    RS Momentum 為第 4 類。若 NVDA-013 的「雙重 regime gate」能擴展至
    RS Momentum 框架，將驗證該組合對「動量延續類型」策略的通用性，
    並有可能突破 NVDA-013 Att3 的 0.55 全域最佳。

    **核心觀察**：NVDA-006 Part A 11 SLs 集中於 2021 泡沫期（NVDA-007 文件
    指出「主要集中在 2021 泡沫期」為結構性虧損），與 NVDA-009 MBPC Part A
    11 SLs 散佈於多 regime 邊界結構不同。
    - 2021 H2 NVDA 泡沫末段的 RS 訊號伴隨 ATR 急速擴張（vol regime gate
      預期可過濾）
    - 2022 bear 期間 SMA(20) 跌破 SMA(60)（trend regime gate 預期可過濾）
    雙重 gate 預期同時對 RS 框架的 Part A SLs 有選擇性。

策略類型：相對強度動量延續 + 多週期 regime gate
    （Relative Strength Momentum Continuation + Multi-Week Regime Filter）

================================================================================
基礎（同 NVDA-006 Att1 baseline）
================================================================================
- NVDA 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
- 5日高點回撤 3-8%（短暫整理）
- Close > SMA(50)（上升趨勢確認）
- 冷卻 10 日
- TP +8% / SL -7% / 20 天，0.15% 滑價

================================================================================
NVDA-015 新增（lesson #22 + ATR vol regime）
================================================================================
- **多週期趨勢 regime**：SMA(20) ≥ k_trend × SMA(60)
- **多週期波動 regime**（可選）：ATR(20) ≤ k_vol × ATR(60)

================================================================================
基準對照（NVDA-006 Att1 / NVDA-013 Att3 全域最佳）
================================================================================
- NVDA-006 Att1: Part A 0.47 / Part B 0.64 / min 0.47
- NVDA-013 Att3: Part A 0.55 / Part B 2.44 / min **0.55**（全域最佳）

驗收目標：min(A,B) > 0.55，維持 A/B 平衡（cum diff < 30%、訊號比 < 50%）。

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1（k_trend=1.00 strict, vol regime disabled）：REJECT min(A,B) 0.37
    結果：
        Part A: 33 訊號, WR 63.6%, 累計 +117.18%, Sharpe **0.37**
        Part B: 11 訊號, WR 81.8%, 累計  +72.37%, Sharpe **0.90**
        min(A,B): **0.37**（vs NVDA-006 0.47 退化 -21%, vs NVDA-013 0.55 -33%）
    失敗分析：
        k=1.00 strict 過濾 2 Part A 訊號（NVDA-006 baseline 35→33）但 Part A
        Sharpe 反而從 0.47 退化至 0.37。NVDA-006 Part A 11 SLs 集中於 2021 H2
        泡沫期，當時 NVDA 持續強勢 SMA20 仍 > SMA60，SMA regime gate 對該批
        SL 結構性無選擇性。

Att2（k_trend=0.97 buffered, vol regime disabled）：REJECT min(A,B) 0.37（=Att1）
    結果：與 Att1 完全相同（Part A 33/0.37, Part B 11/0.90, min 0.37）
    失敗分析（核心發現）：
        k=0.97 vs k=1.00 訊號集**完全相同**——RS 框架 signal-day SMA20/SMA60
        ratio 全部 >= 1.00，無訊號落於 (0.97, 1.00) transition zone。

        **核心發現（lesson #22 邊界精煉）**：RS Momentum 框架的進場條件
        「NVDA 20d return - SMH 20d return >= 5%」**已隱含 NVDA 處於明顯
        uptrend regime**——20 日 outperformance 幾乎不可能在 SMA20 < SMA60
        的 bear regime 出現。因此 lesson #22 multi-week SMA regime gate 對
        RS Momentum 框架**結構性非綁定**。

        框架選擇力對比：
        - BB Squeeze（TSLA-015/NVDA-012/FCX-013/COPX-011）→ SMA regime 提供
          獨立選擇力（過濾 bear regime 假突破）
        - MBPC（NVDA-013）→ SMA regime 提供部分選擇力 + ATR vol regime 提供
          獨立選擇力（雙 gate 必要）
        - Pullback MR（XBI-015）→ ATR vol regime 提供獨立選擇力
        - **RS Momentum（NVDA-015）→ SMA regime gate 結構性冗餘**（RS 條件
          已隱含 uptrend）

Att3（k_trend=0.97 + ATR vol regime k_vol=1.40 啟用）：REJECT min(A,B) 0.48
    結果：
        Part A: 28 訊號, WR 67.9%, 累計 +132.53%, Sharpe **0.48**
        Part B: 10 訊號, WR 90.0%, 累計  +85.63%, Sharpe **1.43**
        min(A,B): **0.48**（vs NVDA-006 0.47 略升 +2%, vs NVDA-013 0.55 -13%）
    A/B 平衡：
        - 訊號比 5.6/yr vs 5.0/yr = 1.12:1（gap 11% < 50% ✓）
        - cum 年化: Part A 18.3%/yr vs Part B 36.5%/yr, |36.5-18.3|/36.5
          = 49.9% > 30% ❌（A/B 累計差 fail）
    失敗分析：
        ATR vol regime k=1.40 過濾 5 Part A 訊號（33→28）+ 1 Part B 訊號
        （11→10），Part A WR 從 63.6% 升至 67.9%，Sharpe 0.37→0.48。
        微幅改善，但仍未達 NVDA-013 Att3 全域最佳 0.55。
        Part A 殘餘 SLs（Att3 仍有 9 LOSS）多為 2021 末段非 ATR 擴張的
        高位 LOSS（pullback 過淺進場後續跌），ATR vol regime 無法捕捉。

================================================================================
跨資產 / 跨策略貢獻（Cross-Asset / Cross-Strategy Findings）
================================================================================
1. **lesson #22 邊界精煉（repo 第 1 次 RS Momentum 框架移植 — REJECT）**：
   RS Momentum 框架因進場條件已隱含 uptrend regime，buffered multi-week SMA
   regime gate **結構性冗餘**。lesson #22 適用框架更新為：
   - 適用：BB Squeeze、MBPC、Pullback MR（進場無顯式趨勢限制）
   - 不適用：RS Momentum（進場 RS 條件已隱含 uptrend）

2. **NVDA-013 Att3 ATR vol regime 跨策略移植部分有效**：
   ATR(20) ≤ 1.40 × ATR(60) 對 RS 框架提供 +0.11 Sharpe 改善（0.37→0.48），
   但無法突破 NVDA-013 0.55 全域最佳。RS 框架 Part A 殘餘 SLs 集中於
   non-ATR-expansion 結構（高位淺回檔後續跌），需其他維度過濾器。

3. **NVDA 結構性 Sharpe 上限**：
   NVDA-013 Att3 0.55 仍為全域最佳。RS 框架在 NVDA 上 min(A,B) 結構性
   上限約 0.48-0.50，需突破需引入新維度（如 RS 動能 ROC、交易量確認、
   Part-A-specific event filter）。

4. **NVDA-014（負向 RS pairs MR）+ NVDA-015（lesson #22 至 RS）兩次 RS
   framework 子方向 cross-strategy port 均失敗**——RS framework 與
   regime/divergence overlay 結合於 NVDA 上達結構性飽和。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA015Config(ExperimentConfig):
    """NVDA-015 Multi-Week Regime-Aware RS Momentum Pullback 參數"""

    # === RS Momentum Pullback 基礎（同 NVDA-006 Att1）===
    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.08
    cooldown_days: int = 10

    # === 多週期趨勢 regime 過濾（lesson #22）===
    # SMA(20) ≥ sma_regime_ratio_min × SMA(60)
    # Att1: k=1.00（NVDA-013 MBPC 甜蜜點移植）
    # Att2: k=0.97（NVDA-012 BB Squeeze 甜蜜點移植）
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.97

    # === 多週期波動 regime 過濾（NVDA-013 ATR vol regime）===
    # Att3 ★ 啟用 vol regime（Att1/Att2 證實 SMA regime 對 RS 框架冗餘）
    # k=1.40 為 NVDA-013 MBPC 框架甜蜜點直接移植
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = True


def create_default_config() -> NVDA015Config:
    """建立預設配置"""
    return NVDA015Config(
        name="nvda_015_regime_rs",
        experiment_id="NVDA-015",
        display_name="NVDA Multi-Week Regime-Aware Relative Strength Momentum Pullback",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
