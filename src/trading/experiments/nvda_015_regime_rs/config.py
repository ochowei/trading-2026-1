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
迭代歷程（Iteration Log，待回測後填入實際結果）
================================================================================
Att1：k_trend=1.00 strict（NVDA-013 MBPC 甜蜜點直接移植，停用 vol regime）
Att2：k_trend=0.97 buffered（NVDA-012 BB Squeeze 甜蜜點，停用 vol regime）
Att3：擇 Att1/Att2 之較佳 k_trend + 啟用 ATR vol regime k_vol=1.40
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
    sma_regime_ratio_min: float = 1.00

    # === 多週期波動 regime 過濾（NVDA-013 ATR vol regime）===
    # Att3 嘗試啟用，預期過濾 2021 H2 泡沫末段 ATR 擴張的假動量訊號
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = False


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
