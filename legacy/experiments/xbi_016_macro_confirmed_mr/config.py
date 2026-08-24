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
- **Macro context confirmation gate**：macro_ticker N 日報酬 ≤ macro_max_return
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

================================================================================
迭代歷程（Iteration Log）— 2026-05-02 三次迭代均失敗
================================================================================
Att1 FAILED: macro_ticker = "QQQ", macro_max_return = -0.015（IWM-015 直接 port）
    結果：
        Part A: 8 訊號 / WR 75.0% / Sharpe **0.36** / cum +10.71% / MDD -6.32%
            交易明細：6 TP / 2 SL（2022-04-19、2023-09-21 仍 SL）
        Part B: 3 訊號 / WR 33.3% / Sharpe **-0.55** / cum -6.79%
            交易明細：1 TP（2024-04-19）/ 2 SL（2024-03-15、2025-03-31）
        min(A,B) **-0.55**（vs XBI-015 Att2 0.46，崩壞 -220%）
    失敗分析：
        - 對 XBI-015 殘餘 3 SLs 過濾力弱：2/3 仍通過 QQQ 10d <= -1.5%
          gate（2022-04-19 mid-bear、2023-09-21 chop 期 QQQ 同步深度修正）
        - 副作用嚴重：Part B 6 winners → 1 winner（移除 2024 多筆 biotech
          反彈訊號，QQQ 10d 未達 -1.5% 閾值）
        - Cooldown chain shift（lesson #19）：2024-03-14 winner 被過濾後
          下一個訊號日 2024-03-15 變為 SL
        - 結構性失敗：XBI biotech 為**事件驅動板塊 ETF**（FDA/臨床試驗），
          與 IWM 小型股**結構鏡像反向**——XBI SLs 多發於 broad market 同步
          修正期（QQQ 通過 gate），winners 多發於 biotech-specific 反彈
          （QQQ 未跌深，被 gate 移除）

Att2 FAILED: macro_ticker = "SPY", macro_max_return = -0.030（SPY 替代 + 加嚴）
    結果：
        Part A: 5 訊號 / WR **100%** / Sharpe 0.00 (zero-var, 5 TPs +3.5%) /
            cum +18.77% / MDD -3.62%
        Part B: 2 訊號 / WR **100%** / Sharpe 0.00 (zero-var, 2 TPs +3.5%) /
            cum +7.12% / MDD -2.92%
        min(A,B): zero-var 結構（採 EWJ-003/SPY-009/IWM-013 慣例 †）
            Part A zero-var、Part B zero-var → 統計顯著性不足
    失敗分析（A/B 平衡標準）：
        - A/B 訊號比 5:2 = 2.5:1 = **60% gap > 50% 目標 ✗**
        - A/B 年化 cum 差 ((1+0.1877)^(1/5)-1)/((1+0.0712)^(1/2)-1) = 3.51%/3.50%
          = **< 1% 差**？等等實際計算：
            A: (1.1877)^0.2 - 1 = 3.50%/yr
            B: (1.0712)^0.5 - 1 = 3.50%/yr
            gap = 0%
          但 raw cum 差 (18.77-7.12)/18.77 = 62% > 30% 目標 ✗
        - Over-filter：signal count 從 baseline 21 降至 7（-67%）
        - 統計顯著性嚴重不足，雙 zero-var 為「零風險小樣本」非真實邊際提升
        - SPY 10d <= -3.0% 為深度 broad correction，僅 2020 COVID 週期、
          2022 Q1 中段、2025-04 tariff shock 等少數時段觸發

Att3 FAILED: macro_ticker = "SPY", macro_max_return = -0.015（SPY threshold 放寬）
    結果：
        Part A: 9 訊號 / WR 66.7% / Sharpe **0.34** / cum +10.67% / MDD -6.32%
            交易明細：6 TP / 3 SL
        Part B: 2 訊號 / WR **100%** / Sharpe 0.00 (zero-var, 2 TPs +3.5%) /
            cum +7.12% / MDD -2.92%
        min(A,B) **0.34**（採 IWM-013 慣例 † Part B zero-var 時 Part A 為約束，
            vs XBI-015 Att2 0.46，**-26%**）
    失敗分析：
        - SPY -1.5% 放寬後 Part A 訊號數 5→9 但 Sharpe 退化（zero-var SLs 進入）
        - Part A WR 100%→66.7%，3 SLs 重新出現（含 2022-04-19、2023-09-21
          原 XBI-015 殘餘 SL）
        - Part B 仍 2 訊號（SPY -3.0% → -1.5% 對 Part B 非綁定，2024-04-19
          + 2024-12-19 已通過 -1.5% 但無新增）
        - 確認：SPY 10d threshold 在 (-3.0%, -1.5%) 區間 trade-off 為「Part A
          訊號數 vs WR」單向，無雙贏 sweet spot

================================================================================
跨資產 lesson #25 邊界發現（重要！）
================================================================================
**lesson #25 broad-equity-index macro context confirmation gate 在 XBI biotech
sub-segment ETF 上結構性失敗**——repo 第 1 次跨資產驗證 lesson #25 hypothesis，
首次 sub-segment ETF 失敗確認。

**結構性失敗根因**：
    XBI biotech 為**事件驅動板塊 ETF**（FDA / 臨床試驗 / 政策審批驅動），與
    IWM 小型股寬基結構截然不同：
    - IWM SLs 為「broad market 健康時的小型股 isolated 急殺」（Omicron 個別
      變異衝擊、SVB 區域銀行擠兌），QQQ 10d 顯著高於 winners 同期
    - XBI SLs 多發於「broad market 同步修正期的 biotech 持續續跌」
      （bear regime 的 mid-cycle 假反彈、chop regime 的 false bounce），
      QQQ/SPY 10d 與 winners 重疊
    - XBI winners 多為「biotech-specific 事件後反彈」（FDA approval /
      clinical positive data）或「broad market shallow 修正期的高品質 dip」
      （QQQ/SPY 10d 未達 -1.5% 閾值）

**lesson #25 適用邊界精煉**：
    | 資產類型 | 適用性 | 機制 |
    |----------|--------|------|
    | broad cap-segment ETF (IWM small-cap) | ✓ SUCCESS | macro 健康時 SL = isolated cap-segment 急殺 |
    | event-driven sector ETF (XBI biotech) | ✗ FAILED | SLs 與 macro 同步，gate 無區分力 |

    **新跨資產假設（待驗證）**：
    - lesson #25 應限縮於「broad cap-segment ETF」（IWM small-cap、
      MDY mid-cap、SPLG large-cap），不適用於「sector / sub-segment ETF」
    - 待跨資產驗證：KRE 區域銀行（事件驅動類同 XBI）、SOXX 半導體
      （cyclical sub-segment 介於兩者之間）、XLF 金融（broad sector）

================================================================================
最終配置選擇
================================================================================
雖然 Att2（SPY -3.0%）有最佳 risk metric（雙 100% WR），但統計顯著性不足
（5/2 訊號）且 A/B cum 差 62% 超過目標。Att3（SPY -1.5%）為 Sharpe 最高
（0.34）但仍低於 baseline 0.46。

預設保留 Att3 為 canonical 配置（min(A,B) 0.34，最接近 baseline 的失敗點），
完整保留 baseline-failure 跨資產證據作為 lesson #25 邊界發現。

XBI-015 Att2 仍為 XBI 全域最優（16 次實驗、50+ 次嘗試確認）。

================================================================================
Acceptance Criteria 達成情況
================================================================================
✗ Sharpe > 基線（min(A,B) 0.46 → 0.34，**-26%**）
✗ A/B 累積報酬差距 < 30%（Att3 未達標 26.4% 接近邊界，但 Sharpe 不達標）
✓ A/B 訊號數差距 < 50%（Att3: 9:2 = 78% gap > 50% **✗**，Att2: 5:2 = 60% **✗**，
    Att1: 8:3 = 63% **✗**——三次迭代均未達標）
✓ 使用成交模型（隔日開盤市價，0.1% 滑價，悲觀認定）
✓ Repo 較少使用方向（lesson #25 cross-asset port，repo 第 1 次跨資產驗證）

實驗失敗，但成功貢獻 lesson #25 邊界發現（broad cap-segment ETF vs
event-driven sector ETF）。
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
    # 迭代歷程（三次迭代均失敗，詳見模組 docstring）：
    #   Att1: macro_ticker="QQQ", macro_max_return=-0.015 → min -0.55 (FAIL)
    #   Att2: macro_ticker="SPY", macro_max_return=-0.030 → zero-var both, count 5/2 (FAIL)
    #   Att3: macro_ticker="SPY", macro_max_return=-0.015 → min 0.34 (FAIL)
    # 預設保留 Att3（最接近 baseline 的失敗，min 0.34 < XBI-015 0.46）
    macro_ticker: str = "SPY"
    macro_lookback: int = 10
    macro_max_return: float = -0.015  # Att3 canonical

    cooldown_days: int = 10


def create_default_config() -> XBI016Config:
    """建立預設配置（Att3：SPY 10d <= -1.5% 宏觀確認閘門，最接近 baseline 的失敗點）"""
    return XBI016Config(
        name="xbi_016_macro_confirmed_mr",
        experiment_id="XBI-016",
        display_name="XBI Macro-Confirmed Pullback MR (SPY 10d Gate)",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
    )
