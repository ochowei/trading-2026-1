"""
COPX-012: Volatility-Acceleration-Bounded MR 配置
COPX Volatility-Acceleration-Bounded Mean Reversion Configuration

策略方向：跨資產移植驗證 lesson #15 v2 BAND 結構與 lesson #19 v8 5d return cap
維度於 COPX 商品/礦業 ETF。3 次迭代全部失敗 vs COPX-007 baseline 0.45 與
COPX-011 Att3 全域最佳 0.64。

**Repo 第 3 次 ATR ratio CEILING 跨資產試驗、首次商品/礦業 ETF 驗證 — 失敗**
（繼 CIBR-014 1.53% vol event-driven sector ETF 與 FXI-014 2.0% vol
policy-driven EM ETF 成功後，COPX 2.25% vol commodity miners ETF 結構性反向）。

================================================================================
跨資產假設來源（cross_asset_lessons.md lesson #15 邊界擴展）
================================================================================
CIBR-014 Att2 發現：lesson #15「ATR(5)/ATR(20) > 1.15 分離 panic 與 slow-grind」
為 FLOOR-only 認知；ATR ratio > X 反而標誌 in-crash 加速階段，對稱失敗模式
形成 BAND 結構（FLOOR + CEILING）。

CIBR-014: ATR ratio BAND ∈ (1.15, 1.40]，min(A,B) 0.49 → 4.08（+733%）
FXI-014: ATR ratio BAND ∈ (1.05, 1.35]，min(A,B) 0.38 → 1.01（+166%）

CIBR-014 提出跨資產假設：
> ATR ratio BAND（FLOOR + CEILING）may extend to other assets with existing
> ATR FLOOR application — XBI（event-driven 1.94% vol）、COPX（commodity 2.25%）、
> FXI（policy-driven 2.0%）、URA（uranium 2.34%）

驗證進展（更新至本實驗結束）：
- FXI-014 Att2 ✓（CEILING 1.35）
- XBI-015 ✗（CEILING 1.40 反向）→ 改用 ATR(20)/ATR(60) ratio 不同公式 ✓
- URA-013 ✗（CEILING 1.40 反向）→ 改用 5d return cap 不同維度 ✓
- **COPX-012 ✗ ALL（CEILING 1.40/1.55 反向 + 5d cap -8% 反向）— 確認 BAND 結構性失敗**

================================================================================
基礎：COPX-007 baseline（已執行驗證，min(A,B) Sharpe 0.45）
================================================================================
- Part A: 21 訊號 WR 76.2% Sharpe 0.45 cum +36.73% MDD -6.97% PF 2.41
- Part B: 10 訊號 WR 80.0% Sharpe 0.57 cum +19.74% MDD -7.23% PF 3.02
- A/B 年化 cum: A 7.35%/y / B 9.87%/y → gap 25.5%（< 30% ✓ 已達標）
- A/B 年化 signals: A 4.2/y / B 5.0/y → gap 16%（< 50% ✓ 已達標）
- min(A,B) **0.45**（Part A 為瓶頸）

vs 全域最佳 COPX-011 Att3（regime BOX BB Squeeze Breakout，min(A,B) 0.64）：
  COPX-011 雖 Sharpe 較高，但 A/B cum gap 66.4% 嚴重失衡。
  COPX-012 目標：在保持 COPX-007 A/B 平衡優勢下提升 Sharpe 至 > 0.64
  → 三次迭代均未達成（最高 Att2 0.32 仍低於 baseline）

================================================================================
Att1（CEILING <= 1.40，CIBR-014 reference 直接移植）：FAILED min(A,B) 0.28
================================================================================
參數：atr_ratio_floor=1.05, atr_ratio_ceiling=1.40, 無 5d cap
結果：
  Part A: 20 訊號 WR 70.0% Sharpe **0.28** cum +21.72% MDD -6.97%（vs baseline 0.45 退化 -38%）
  Part B: 9 訊號 WR 77.8% Sharpe 0.50 cum +15.70%（vs baseline 0.57 退化 -12%）
  min(A,B) **0.28**（vs baseline 0.45 退化 -38%）
分析：
  - CEILING 1.40 過濾 1 個 Part A 訊號 + 1 個 Part B 訊號
  - 兩個被過濾的訊號**都是 winners**（baseline WR Part A 76.2% → Att1 70.0%、Part B 80% → 77.8%）
  - **觸發 lesson #19 cooldown chain shift**：Part A max consec losses 從 baseline 2 暴增至 4
    （連續 SL：2019-05-06 → 2019-08-01 → 2020-01-28 → 2020-02-25），
    與 NVDA-010 Att3、TLT-010 失敗模式平行
  - **核心發現**：COPX winners 在 ATR ratio 維度的分布**反向於 CIBR/FXI**——
    COPX 高品質訊號（panic flush bounces）伴隨 ATR ratio > 1.40 的 in-crash acceleration，
    CEILING 過濾系統性移除這類 winners

================================================================================
Att2（CEILING <= 1.55，放鬆 CEILING 至最極端）：FAILED min(A,B) 0.32
================================================================================
參數：atr_ratio_floor=1.05, atr_ratio_ceiling=1.55, 無 5d cap
結果：
  Part A: 21 訊號 WR 71.4% Sharpe **0.32** cum +25.98%（與 baseline 訊號數同但 WR 降）
  Part B: 10 訊號 WR 80.0% Sharpe 0.57 cum +19.74%（與 baseline 完全相同）
  min(A,B) **0.32**（vs baseline 0.45 退化 -29%）
分析：
  - CEILING 1.55 對 Part B 完全非綁定（10 訊號全保留），但 Part A 訊號數雖同 baseline
    （21）但**訊號日期不同**（cooldown chain shift 將 1 個被過濾訊號替換成 1 個新訊號）
  - 新訊號為 SL（max consec losses 仍為 4），系統性引入 SLs
  - **驗證 CEILING 方向結構性失敗**：即使極寬 CEILING（1.55）仍透過 cooldown chain shift
    反向引入 SLs，與 Att1 同方向失敗

================================================================================
Att3（停用 CEILING + 5d return cap >= -8%，URA-013 cross-asset port）：FAILED min(A,B) 0.00
================================================================================
參數：atr_ratio_floor=1.05, atr_ratio_ceiling=99（停用）, return_cap_window=5,
      return_cap_threshold=-0.08
結果：
  Part A: 14 訊號 WR 57.1% Sharpe **0.00** cum -0.98% MDD -7.50%（vs baseline 0.45 嚴重崩壞）
  Part B: 8 訊號 WR 87.5% Sharpe **0.92** cum +21.32% MDD -4.62%（**+62% vs baseline 0.57**）
  min(A,B) **0.00**（Part A 完全崩壞）
分析：
  - 5d cap -8% 過濾 7 個 Part A 訊號（21→14），**幾乎全為 winners**
    （Part A wins baseline 16 → Att3 8，移除 8 個 winners、僅 1 SL；同時 cooldown chain shift
    引入 1 個新 SL，淨 SL 數 5→6）
  - Part B 受惠：過濾 2024-07-19 SL（5d -8.5%）+ 2025-03-31 邊際訊號，
    保留 8 個 winners（Sharpe 0.57→0.92，+62%）
  - **不對稱失敗**：Part B 顯著改善但 Part A 災難性退化，
    顯示 COPX Part A 的「panic flush bounces」winners 系統性伴隨**深 5d 累計跌幅**
    （-8%~-15% 範圍），與 URA Part A 結構**反向**
  - **核心發現**：URA-013 5d cap 維度**結構性不適用 COPX**——URA winners 集中於淺 5d
    cumulative decline（-3%~-8%），losers 集中於深 5d（-9%~-15%）；COPX 反之
    （winners 集中深 5d，losers 跨淺-深廣分布）

================================================================================
整合失敗結論（cross_asset_lessons.md lesson #15 v2 + #19 v8 邊界精煉）
================================================================================
**lesson #15 v2 BAND CEILING 適用條件精煉**：
- 適用：CIBR (1.53% vol event-driven sector ETF) ✓ + FXI (2.0% vol policy-driven EM) ✓
- 結構性反向：COPX (2.25% vol commodity miners ETF) ✗
- 機制差異：commodity miners ETF 的 winners 結構**包含 in-crash acceleration phase**
  （FCX 銅礦企業 + COPX 整體商品超級週期），與 sector ETF (FDA news-driven) 或
  EM ETF (policy continuation) 的「acceleration = 持續崩盤」結構不同

**lesson #19 v8 5d return cap 適用條件精煉**：
- 適用：URA (2.34% vol uranium policy-driven ETF) ✓
- 結構性反向：COPX (2.25% vol commodity miners ETF) ✗
- 機制差異：URA winners 為 oscillator hook 後的「淺 5d 反彈」；
  COPX winners 為「深 5d capitulation 後的 panic flush bounces」

**新跨資產規則（lesson #15 v2 + lesson #19 v8 邊界擴展）**：
任何 oscillator/return-based 上限濾波器（CEILING / cap 方向）對「商品超級週期驅動的
礦業 ETF」（COPX、CIBR-XME 類別）結構性失效——因 winners 與 losers 在
acceleration / multi-day decline 維度的分布橫跨完整範圍且 winners 偏深，無單一
切點可區分。COPX 與 FCX-013 lesson #22 反向（k=1.00 嚴格優於 k<1 buffered）
共同確認商品/礦業類別的「extreme regime entry 策略空間」與其他資產類別不同。

================================================================================
進場/出場條件（Att3 final state，最具研究價值版本）
================================================================================
1. 收盤價相對 20 日最高價回檔 10-20%
2. Williams %R(10) <= -80（超賣確認）
3. ATR(5)/ATR(20) > 1.05（FLOOR only，CEILING 停用）
4. 5 日累計報酬 >= -8%（URA-013 direction，failed but documented）
5. 冷卻期 12 個交易日

成交模型（同 COPX-007）：
- 進場：next_open_market（隔日開盤市價）
- TP 出場：limit_order Day（當日限價單）
- SL 出場：stop_market GTC（持倉期間停損市價）
- 到期出場：next_open_market
- 滑價：0.15%（商品 ETF 中等流動性）
- 悲觀認定：是（同日觸及 TP 與 SL 視為 SL 先成交）

**結論**：COPX-012 為 negative-result 實驗。COPX-011 Att3 仍為全域最優（min(A,B) 0.64）；
COPX-007 仍為 MR 框架最優（min(A,B) 0.45 + A/B balance）。本實驗確認 COPX
不適用 ATR CEILING 與 5d cap 兩個 oscillator/return-based 維度的 cap 方向。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX012Config(ExperimentConfig):
    """COPX-012 Volatility-Acceleration-Bounded MR 參數"""

    # 進場指標（同 COPX-007）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10  # 回檔 >= 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 12

    # 波動率自適應 BAND 過濾器（FLOOR + CEILING）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.05  # ATR(5)/ATR(20) > 1.05（同 COPX-007）
    atr_ratio_ceiling: float = 99.0  # Att3: 停用 CEILING（Att1/Att2 證實 CEILING 對 COPX 反向）

    # 多日 return cap 過濾器（URA-013 cross-asset direction）
    # 過濾 5 日累計跌幅過深的「multi-day continuation」訊號
    return_cap_window: int = 5  # 5 日窗口
    return_cap_threshold: float = -0.08  # 5 日累計報酬 >= -8%（COPX 2.25% vol scaling）


def create_default_config() -> COPX012Config:
    """建立預設配置（最佳迭代結果，updated after experimentation）"""
    return COPX012Config(
        name="copx_012_atr_ceiling_mr",
        experiment_id="COPX-012",
        display_name="COPX Volatility-Acceleration-Bounded MR",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 COPX-007）
        stop_loss=-0.045,  # -4.5%（同 COPX-007）
        holding_days=20,  # 20 天（同 COPX-007）
    )
