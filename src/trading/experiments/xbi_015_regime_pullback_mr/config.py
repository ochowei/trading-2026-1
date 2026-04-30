"""
XBI-015: Multi-Week Regime-Aware Pullback MR

策略方向（Strategy Direction）：
    將 lesson #22「buffered multi-week SMA trend regime + ATR vol regime」
    （TSLA-015 / NVDA-012 / FCX-013 / COPX-011 BB Squeeze + NVDA-013 MBPC，
    五次跨資產驗證）首次跨**策略類型**移植至 Pullback Mean Reversion 框架。

動機（Motivation）：
    XBI-005 baseline（10d 回檔 8-20% + WR(10) ≤ -80 + ClosePos ≥ 35%）
    Part A Sharpe 0.36 / Part B Sharpe 0.64，A/B Sharpe 落差 0.28（78%）
    為跨資產 Part A/B 落差最大者之一。XBI-014（2DD floor 加深）已確認
    XBI 為「事件驅動板塊 ETF，winners 2DD 分布雙峰化」，capitulation-depth
    維度濾波結構性失效（XBI 第 11 個失敗策略類型）。

    Part A 5 個 SLs 分散於不同 regime：
        - 2021-02-19（late-bull post-peak Feb 高點 +8 日）
        - 2021-05-06（post-peak 過熱回檔失敗）
        - 2022-01-06（bear regime 啟動初期）
        - 2022-04-19（mid-bear）
        - 2023-09-21（chop regime）

    **核心觀察**：5 個 SLs 並非統一聚集於 bear regime（純 SMA(20)<SMA(60)
    可能違反 lesson #5「趨勢濾波器+MR=災難」），但均**處於 vol expansion
    transition** —— ATR(20) 相對 ATR(60) 顯著升高的時點。

    **lesson #22 cross-strategy MR 假設**：
        ATR(20) ≤ k × ATR(60) vol stability gate 能在 MR 進場時
        過濾「波動正在放大」的 transition 期，保留「波動穩定/收縮」期。
        此維度與 ClosePos 反轉確認、Pullback 深度為**獨立**選擇力。

    與 XBI-009 的差異：
    - XBI-009：ATR(5)/ATR(20) > 1.05 / 1.10（**要求**高 ATR ratio，反向）
    - XBI-015：ATR(20)/ATR(60) ≤ k（**要求**低 ATR ratio，stability gate）
    XBI-009 失敗證明「進場時要求短期波動放大」反而過濾好訊號；XBI-015
    試驗「進場時要求中期波動穩定（vs 長期）」（NVDA-013 MBPC 成功方向）。

    **Repo 第 1 次 lesson #22 應用於 Pullback MR 框架**（先前皆於 BB
    Squeeze / MBPC 框架）。若成功，將拓展 lesson #22 適用範圍至「均值
    回歸類型」策略，並有可能突破 XBI-005 的 0.36 Sharpe 上限。

策略類型：均值回歸 + 多週期波動 regime gate
    （Mean Reversion + Multi-Week Volatility Regime Filter）

================================================================================
基礎（同 XBI-005）
================================================================================
- 10 日高點回檔 ∈ [-8%, -20%]
- Williams %R(10) ≤ -80
- ClosePos ≥ 35%
- 冷卻 10 日
- TP +3.5% / SL -5.0% / 15 天，0.1% 滑價

================================================================================
XBI-015 新增（lesson #22 cross-strategy MR port）
================================================================================
- **多週期波動 regime gate**：ATR(20) ≤ k × ATR(60)
- 預設 k = 1.10（Att2 ★ SUCCESS，閾值對齊 XBI 訊號分布中位）
- （可選）多週期趨勢 regime：SMA(20) ≥ k_sma × SMA(60)，預設停用
  以避免 lesson #5「趨勢濾波器+MR=災難」風險

================================================================================
基準對照（XBI-005）
================================================================================
- Part A: 21 訊號, WR 76.2%, 累計 +29.32%, Sharpe 0.36
- Part B:  6 訊號, WR 83.3%, 累計 +12.71%, Sharpe 0.64
- min(A,B) 0.36

驗收目標：min(A,B) > 0.36，維持 A/B 平衡（年化 cum diff < 30%、
訊號比 gap < 50%）。

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1（k=1.30，NVDA-013 vol regime 中位移植）：FAILED 非綁定
    參數：vol_regime_max_ratio = 1.30
    結果：Part A 21 訊號 / WR 76.2% / Sharpe 0.36 / 累計 +29.30%
          Part B  6 訊號 / WR 83.3% / Sharpe 0.64 / 累計 +12.71%
          min(A,B) **0.36**（與 XBI-005 baseline 持平）
    失敗分析：
        - k=1.30 對 XBI 訊號日 ATR(20)/ATR(60) 完全非綁定
        - XBI 訊號日 vol ratio 中位約 1.05-1.15，1.30 從未觸發
        - 與 XBI-009 結論一致：XBI 不存在 ATR ratio > 1.10 訊號
        - 結論：閾值需從 NVDA-013 的「multi-driver 高波動單股」假設
          下調至 XBI 的「事件驅動板塊 ETF」尺度

Att2 ★（k=1.10，閾值對齊 XBI 訊號分布）：SUCCESS min(A,B) 0.46
    參數調整：vol_regime_max_ratio 1.30 → 1.10
    結果：Part A 15 訊號 / WR **80.0%**（+3.8pp）/ Sharpe **0.46** /
              累計 +25.13% / MDD -7.09%
          Part B  6 訊號 / WR 83.3% / Sharpe 0.64 / 累計 +12.71%
                       （與 XBI-005 完全相同，k=1.10 對 Part B 非綁定）
          min(A,B) **0.46**（vs XBI-005 0.36，**+28%**）★
    A/B 平衡（驗收目標全達）：
        - Part A 年化 cum: (1+0.2513)^(1/5)-1 = 4.59%/yr
        - Part B 年化 cum: (1+0.1271)^(1/2)-1 = 6.16%/yr
        - 相對差: |6.16-4.59|/6.16 = **25.5% < 30% ✓**
        - 訊號比 3.0/yr vs 3.0/yr = **1.0:1（gap 0% < 50% ✓）**
    成功分析：
        - 過濾 6 個訊號（21→15）：4 winners + **2 SLs**（2021-02-19
          late-bull peak vol expansion、2022-01-06 early-bear vol
          expansion）
        - **vol expansion gate 在 MR 框架非冗餘**：Pullback+WR+ClosePos
          進場架構不含波動限制，ATR(20)/ATR(60) ≤ 1.10 提供獨立選擇力
          （與 NVDA-013 vol regime 在 MBPC 框架非冗餘的發現平行）
        - Part A WR 76.2%→80.0%、Sharpe 0.36→0.46 雙提升
        - 殘餘 3 SLs（2021-05-06 post-peak、2022-04-19 mid-bear、
          2023-09-21 chop）均處於 vol ratio < 1.10 環境，非 vol gate
          可解，需其他維度
        - **Repo 第 1 次驗證 lesson #22 cross-strategy: BB Squeeze /
          MBPC → MR 移植，且 vol regime 在 MR 框架非冗餘**
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI015Config(ExperimentConfig):
    """XBI-015 Multi-Week Regime-Aware Pullback MR 參數"""

    # === 進場指標（同 XBI-005）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 >= 8%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.35

    # === 多週期波動 regime gate（lesson #22 cross-strategy MR port）===
    # ATR(short) ≤ vol_regime_max_ratio × ATR(long)
    # Att1: k=1.30（NVDA-013 vol regime 中位移植）→ FAILED 非綁定（min 0.36 持平）
    # Att2 ★: k=1.10（閾值對齊 XBI 訊號日 vol ratio 分布中位）
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.10
    use_vol_regime: bool = True

    # === 多週期趨勢 regime gate（預設停用，避免 lesson #5 風險）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.97
    use_sma_regime: bool = False

    cooldown_days: int = 10


def create_default_config() -> XBI015Config:
    """建立預設配置（Att1：vol regime k=1.30 alone）"""
    return XBI015Config(
        name="xbi_015_regime_pullback_mr",
        experiment_id="XBI-015",
        display_name="XBI Multi-Week Regime-Aware Pullback MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
    )
