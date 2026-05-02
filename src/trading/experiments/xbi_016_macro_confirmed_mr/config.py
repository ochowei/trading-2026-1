"""
XBI-016: Macro-Confirmed Pullback Mean Reversion (Broad-Market Macro Context Gate)

策略方向（Strategy Direction）：
    在 XBI-015 Att2（Multi-Week Regime-Aware Pullback MR，min(A,B) 0.46，
    repo 第 1 次 lesson #22 cross-strategy MR 移植）基礎上，疊加 **broad-market
    macro context confirmation gate**（lesson #25 hypothesis 跨資產驗證），
    要求 broad equity index 已進入 confirmed correction 才放行 XBI 生技
    capitulation 訊號。

動機（Motivation）：
    Lesson #25 IWM-015 首次驗證 broad-equity-index 作為 macro risk regime
    confirmation 對 sub-segment ETF capitulation MR 有效（QQQ 10d ≤ -1.5%
    對 IWM 小型股 MR），cross-asset 假設明確：

        > "QQQ 10d gate 應在 XBI / KRE / SOXX / IGV / XLF 等 sub-segment
        >  ETF 上有效（threshold 需依 sub-segment vs QQQ 相關性調整）"

    XBI 為「事件驅動板塊 ETF」，FDA 審批/臨床試驗 negative news 常導致
    生技板塊 isolated 急殺，與 broader market risk-off 解耦。XBI-015 Att2
    殘餘 3 筆 Part A SLs 分散於不同 regime：
        - 2021-05-06（post-peak 過熱回檔失敗）
        - 2022-04-19（mid-bear 假反彈）
        - 2023-09-21（chop regime 假訊號）

    **核心觀察（待驗證）**：
        若這些 SLs 發生於 broader market（QQQ / SPY / XLV）健康/輕微回檔
        區段，則 XBI 的「孤立急殺」屬於 biotech-specific 事件擴散，無
        broad confirmation 的 dip-buying 易被續跌；若 broader market 同步
        進入 confirmed correction，dip-buying 可受益於系統性 V 型反轉。

    **macro proxy 選擇（biotech sub-segment 特有考量）**：
        IWM (small-cap) → QQQ (large-cap tech) 為「不同市值的 broad-market
        risk regime」鏡像。XBI (biotech sub-sector) 與 QQQ 為「不同 sector
        composition」關係：
        - QQQ：NASDAQ-100，含部分大型 biotech（AMGN/REGN/GILD/VRTX 等
          ~6% 權重），主導為 tech mega-caps，與 XBI（小型 biotech）相關性
          中等（~0.55）
        - SPY：S&P 500，廣度最高，與 XBI 相關性 ~0.50
        - XLV：Healthcare sector，含大型 pharma + biotech，與 XBI 相關
          性最高 ~0.75 但失去「broad-market regime」獨立確認
        - 選擇 QQQ 為**首要 proxy**：(1) 直接驗證 lesson #25 hypothesis，
          (2) 與 IWM-015 採同 ticker 便於跨資產比較，(3) tech regime
          與 biotech 高 beta 屬性同類。SPY 為 fallback。

策略類型：均值回歸 + 多週期波動 regime gate + broad-market macro confirmation
    （Mean Reversion + Vol Regime Filter + Broad-Market Macro Context Gate）

================================================================================
基礎（同 XBI-015 Att2，當前全域最優）
================================================================================
- 10 日高點回檔 ∈ [-8%, -20%]
- Williams %R(10) ≤ -80
- ClosePos ≥ 35%
- ATR(20) ≤ 1.10 × ATR(60) vol stability gate
- 冷卻 10 日
- TP +3.5% / SL -5.0% / 15 天，0.1% 滑價

================================================================================
XBI-016 新增（lesson #25 cross-asset port）
================================================================================
- **Macro context confirmation gate**：QQQ N 日報酬 ≤ macro_max_return
- macro_lookback：10 日（同 IWM-015 baseline）
- macro_max_return：候選閾值依迭代調整

================================================================================
基準對照（XBI-015 Att2 ★ 2026-04-30 全域最優）
================================================================================
- Part A: 15 訊號, WR 80.0%, 累計 +25.13%, Sharpe 0.46, MDD -7.09%
- Part B:  6 訊號, WR 83.3%, 累計 +12.71%, Sharpe 0.64
- min(A,B) 0.46
- A/B 年化 cum 4.59%/yr vs 6.16%/yr（gap 25.5%）
- A/B 年化訊號比 1.0:1（gap 0%）

驗收目標：min(A,B) > 0.46（XBI 全域最優突破），維持 A/B 平衡
（年化 cum diff < 30%、訊號比 gap < 50%），同時透過 macro
confirmation 過濾殘餘 3 SLs。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI016Config(ExperimentConfig):
    """XBI-016 Macro-Confirmed Pullback MR 參數"""

    # === 進場指標（同 XBI-015 Att2）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 >= 8%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.35

    # === 多週期波動 regime gate（同 XBI-015 Att2）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.10
    use_vol_regime: bool = True

    # === XBI-016 新增：broad-market macro context confirmation gate ===
    # 候選閾值（依迭代）：
    #   Att1 (QQQ -1.5%): 直接 port from IWM-015 Att1
    #   Att2 (QQQ -3.0%): 放寬 (XBI 信號數較少，避免 over-filter)
    #   Att3 (SPY -2.0%): 替換 macro proxy 為更廣的 broad-market 指數
    macro_ticker: str = "QQQ"
    macro_lookback: int = 10
    macro_max_return: float = -0.015  # Att1 預設

    cooldown_days: int = 10


def create_default_config() -> XBI016Config:
    """建立預設配置（Att1：QQQ 10d <= -1.5% 宏觀確認閘門）"""
    return XBI016Config(
        name="xbi_016_macro_confirmed_mr",
        experiment_id="XBI-016",
        display_name="XBI Macro-Confirmed Pullback MR (QQQ 10d Gate)",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
    )
