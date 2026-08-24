"""
TSM-021: QQQ Macro-Health Gate on RS Momentum Pullback 配置
TSM QQQ Macro-Health Gate on RS Momentum Pullback Configuration

策略方向：在 TSM-011 Att3（RS Momentum Pullback + 5d return CEILING +10.5%，
min(A,B) 0.83 全域最優）基礎上，疊加 **QQQ broad-market macro-health regime
confirmation gate**，要求 NASDAQ-100 broad equity index 在訊號日近 N 日報酬處於
特定 regime（FLOOR 或 CEILING）以確保 TSM RS Momentum Pullback 訊號發生於
「TSM 動能 + QQQ broad market 同向 regime」的對齊環境。

跨資產移植動機（Cross-Asset Port Motivation）：
    Lesson #25: Broad-Market Macro Context Confirmation Gate
        - IWM-015 ★（IWM-013 Att3 + QQQ 10d <= -1.5% CEILING gate, +374% min Sharpe）
        - 機制：IWM 小型股 capitulation MR 殘餘 SLs 為「孤立小型股急殺」
          （Omicron / SVB），broad market QQQ 並未同步 risk-off
        - 解：要求 QQQ 10d 也在 confirmed correction (CEILING <= -1.5%)，
          過濾「孤立 sub-segment 急殺」訊號

    本實驗（TSM-021）為 lesson #25 的 cross-strategy 鏡像擴展：
        - 從「sub-cap-segment ETF capitulation MR」擴展至「半導體 ADR 個股 +
          RS Momentum Pullback」
        - 從「broad-market 已 confirmed risk-off」(IWM-015 CEILING) 反向至
          「broad-market 未進入 deep correction」(TSM-021 FLOOR)
        - 機制差異：MR 框架 (capitulation buy) 利用「broad-market 系統性 V 型反彈」
          ；Momentum 框架 (uptrend buy-the-dip) 利用「broad-market 持續 uptrend
          支撐 momentum 延續」。兩者方向相反但同源 lesson #25 broad-market
          context dependency。

核心假說（TSM Momentum Continuation Macro-Health Hypothesis）：
    TSM-011 Att3 殘餘 4 筆 SLs（Part A: 2022-11-21 / 2022-12-07，Part B:
    2024-07-16 / 2024-10-30）皆發生於：
    (a) 2022 Q4 升息熊市 broad-market 持續走弱
    (b) 2024 Q3 Trump Taiwan defense 政治風險 + 2024 Q4 Election 不確定性
    對應的 broad-market QQQ 5d return 在這些日期都顯著為負或處於 transitional
    regime，意味著 QQQ broad-market 系統性走弱使 TSM RS Momentum 失去 broad
    tech leadership 支撐。

    對比 winners 的 QQQ 環境：
    - Part A winners 多發生於 broad market 強勢（2019/2020/2021/2023 牛市階段）
    - Part B winners 多發生於 broad market 強勢（2024 H1 / 2024 Q4 / 2025 H1）

    解：要求 QQQ N 日報酬 >= floor 閾值（broad-market 健康確認），過濾
    「TSM RS momentum 訊號 + broad-market broad correction」雙弱共存的
    momentum 失敗訊號。

================================================================================
基礎（沿用 TSM-011 Att3 全域最優）
================================================================================
- TSM 20 日報酬 - SMH 20 日報酬 >= +5%（相對板塊超額表現）
- 5 日高點回檔 3-7%（短暫整理）
- Close > SMA(50)（上升趨勢確認）
- 訊號日 5 日報酬 <= +10.5%（rally exhaustion 過濾）
- 冷卻 10 日
- TP +8% / SL -7% / 25 天，0.10% 滑價

================================================================================
TSM-021 新增（lesson #25 cross-strategy mirror extension）
================================================================================
- **QQQ N 日報酬 >= macro_min_return**（FLOOR：broad-market 健康閘門）
- 或 **QQQ N 日報酬 <= macro_max_return**（CEILING：broad-market 過熱排除）
- 或雙條件 BAND（FLOOR + CEILING）

================================================================================
基準對照（TSM-011 Att3 全域最優，2026-05-02）
================================================================================
- Part A: 12 訊號 (2.4/yr), WR 83.3%, 累計 +74.10%, Sharpe 0.86 (2 SLs/1 EX)
- Part B: 10 訊號 (5.0/yr), WR 80.0%, 累計 +59.78%, Sharpe 0.83 (2 SLs)
- min(A,B) 0.83
- A/B 年化 cum diff: 19.3%（< 30% ✓），訊號比 1.2:1（gap 16.7% < 50% ✓）

驗收目標：min(A,B) > 0.83，維持 A/B 平衡（cum diff < 30%, signal gap < 50%）。

================================================================================
迭代歷程（Iteration Log）— 詳見 EXPERIMENTS_TSM.md
================================================================================
Att1 (FLOOR direction，QQQ 5d >= -3%): REJECT min(A,B) **0.78** (-6% vs baseline 0.83)
    Part A: 11 訊號 WR 81.8% Sharpe 0.78 cum +61.20%
    Part B: 10 訊號完全不變 WR 80% Sharpe 0.83 cum +59.78%
    過濾結果：
        ✓ 2022-12-07 Part A SL（QQQ_5d 在 2022 Q4 bear 期 < -3%）過濾
        ✗ 2022-01-05 Part A winner（QQQ_5d 在 Fed pivot 前夕 < -3%）誤殺
            → cooldown chain shift 引入 2022-01-13 SL（淨效果 -1 winner -1 SL +1 SL = 退化）
        ✗ Part B 全部訊號 QQQ_5d >= -3%（包含兩筆 SL：2024-07-16/2024-10-30），
          5d 短時框未能捕捉 broad-market 弱勢
    結論：FLOOR 方向 + 5d 短時框 over-filters Part A winners 同時對 Part B SLs 非綁定

Att2 ★ (CEILING direction，QQQ 10d <= +2%): SUCCESS min(A,B) **1.14** (+37% vs baseline 0.83)
    Part A: 9 訊號 WR **88.9%** Sharpe **1.14** cum +61.73% MDD -8.78%
    Part B: 8 訊號 WR **87.5%** Sharpe **1.23** cum +59.23% MDD -9.01%
    A/B cum diff: |61.73-59.23|/61.73 = **4.0%**（<<30% ✓ 大幅優於 baseline 19.3%）
    A/B signal gap: (9-8)/9 = **11.1%**（<<50% ✓ 與 baseline 16.7% 同等）
    過濾結果：
        ✓ 2022-12-07 Part A SL 過濾（QQQ_10d < +2%）
        ✓ 2022-11-21 Part A SL 過濾 → cooldown chain shift 至 2022-11-28 SL（退化但同質）
        ✓ 2024-07-16 Part B SL 過濾（QQQ_10d > +2%）★ 關鍵改善
        ✗ 2025-05-08 Part B winner 誤殺（collateral damage）
        ✗ 2021-01-26 / 2023-01-19 Part A winners 誤殺
    機制（lesson #25 cross-strategy mirror extension）：
        TSM RS Momentum Pullback 失敗訊號集中於 broad-market QQQ 已過度反彈 regime
        （QQQ_10d > +2%），代表 broad-tech leadership 已達短期 rally exhaustion，
        後續無 systemic momentum 支撐。CEILING +2% 切除「TSM RS 訊號 + QQQ 已過熱」
        雙過熱共存的失敗環境。

Att3a (CEILING +1% 加嚴 robustness check): REJECT min 0.83 = baseline TIE
    Part A: 7 訊號 WR 85.7% Sharpe 0.91 cum +38.66%
    Part B: 5 訊號 WR 80% Sharpe 0.83 cum +26.40%
    結論：+1% 過嚴 over-filter 大量 winners

Att3b (CEILING +3% 放鬆 robustness check): REJECT min 0.74
    Part A: 9 訊號 WR 88.9% Sharpe 1.11 cum +60.65%
    Part B: 9 訊號 WR 77.8% Sharpe 0.74 cum +47.94%（放回 2024-07-16 SL）
    結論：+3% 過鬆 放回 Part B 關鍵 SL，確認 +2% 為甜蜜點下界

================================================================================
跨資產貢獻（Cross-Asset Contribution）
================================================================================
1. **Repo 第 2 次 lesson #25 broad-market context confirmation gate 跨資產驗證**
   （繼 IWM-015 後）
2. **首次跨策略框架延伸**：lesson #25 從 capitulation MR (IWM-015 CEILING) 鏡像
   至 RS Momentum Pullback (TSM-021 CEILING) — 同方向 (CEILING) 但機制相反：
   - IWM-015：要求 QQQ 已 confirmed risk-off → 利用 systemic V-bounce
   - TSM-021：要求 QQQ 未過熱 → 排除 broad-market rally exhaustion 環境
3. **首次半導體 ADR 個股 + cross-asset macro context filter 成功**
   — TSM 經 8 次 cross-asset macro filter 試驗（TSM-013/014/015/016/017/019/020）
   全部 REJECT/PARTIAL，TSM-021 為首次達 min(A,B) > 0.83 突破
4. **TSM 結構性 0.83 ceiling 首次突破**（TSM-008/011/013/014/015/016/017/018/019/020
   經 12 次實驗、40+ 次嘗試後達 ceiling），TSM-021 +37% min(A,B) 改善為 repo
   TSM 系列首次突破
5. **新跨資產假設（待驗證）**：broad-market context CEILING gate 可能適用其他
   RS / MBPC momentum 框架（NVDA-013、SOXL-010、VOO-004）— TSM-021 為首例

================================================================================
Acceptance Criteria 達成情況（Att2 ★）
================================================================================
✓ Sharpe > 基線（min(A,B) 0.83 → 1.14，+37%）
✓ A/B 累積報酬差距 < 30%（4.0%，vs baseline 19.3%）
✓ A/B 訊號數差距 < 50%（11.1%，vs baseline 16.7%）
✓ 使用成交模型（隔日開盤市價，0.10% 滑價，悲觀認定）
✓ Repo 較少使用方向（broad-market context confirmation gate, lesson #25 cross-strategy
  mirror extension，TSM 系列首次突破 0.83 ceiling）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSM021Config(ExperimentConfig):
    """TSM-021 QQQ Macro-Health Gate on RS Momentum Pullback 參數"""

    # === RS Momentum Pullback 基礎（同 TSM-011 Att3 / TSM-008）===
    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # === Signal-day return CEILING（同 TSM-011 Att3）===
    ret_1d_max: float = 999.0
    ret_5d_max: float = 0.105

    # === TSM-021 新增：QQQ broad-market macro-health gate ===
    # Att1（baseline FLOOR）: macro_min_return = -0.03（QQQ 5d >= -3%）
    # Att2: 視 Att1 結果調整（FLOOR 加嚴或切換 CEILING / BAND）
    # Att3: 視 Att1/Att2 結果調整 lookback 或閾值
    macro_ticker: str = "QQQ"
    macro_lookback: int = 10
    macro_min_return: float = -999.0  # FLOOR 停用
    # Att2 ★ canonical：CEILING +2% 為三次迭代後的甜蜜點
    # Att1 (FLOOR -3%) REJECT min 0.78（cooldown chain shift 引入 2022-01-13 SL）
    # Att2 ★ (CEILING +2%) SUCCESS min(A,B) **1.14**（+37% vs baseline 0.83），
    #   Part A 9/88.9%/1.14 / Part B 8/87.5%/1.23，A/B cum gap 4.0% / signal gap 11.1%
    # Att3a (CEILING +1% 加嚴) REJECT min 0.83（過嚴 over-filter）
    # Att3b (CEILING +3% 放鬆 robustness) REJECT min 0.74（放回 2024-07-16 SL）
    macro_max_return: float = 0.02


def create_default_config() -> TSM021Config:
    return TSM021Config(
        name="tsm_021_qqq_macro_health_gate",
        experiment_id="TSM-021",
        display_name="TSM QQQ Macro-Health Gate on RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
