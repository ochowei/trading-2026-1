"""
COPX-014: COPX-GLD Cross-Asset Divergence Regime-Gated BB Squeeze Breakout 配置
COPX-GLD Divergence Regime-Gated BB Squeeze Breakout Configuration

策略方向：
- 將 lesson #20「跨資產相對表現」延伸為「regime gate」，
  cross-strategy port from TLT-014（TLT vs SPY）/ TSLA-017（TSLA vs QQQ），
  repo 第 3 次 cross-asset divergence regime gate 試驗、首次商品/礦業類別嘗試。
- 假設「COPX 相對 GLD/SPY/XLB 顯著弱勢」=「金屬族群分歧或廣泛 risk-off」regime，
  此情境下 BB Squeeze breakout 多為失敗突破。

合理性：
- COPX-011 Att3（current global best, min(A,B) 0.64）為 BB Squeeze Breakout +
  buffered SMA regime BOX [k_min=1.00, k_max=1.09]。Part A 殘餘 1 SL
  （2019-04-01 -6.14%）+ 1 deep EX（2023-07-12 -4.63%）；Part B 僅 2 訊號（1 TP /
  1 mild EX -1.54%）。再壓 SL 與深 EX 是改善方向。
- TLT-014（+393% Sharpe vs TLT-013）/ TSLA-017（+81% vs TSLA-015）證明
  cross-asset divergence regime gate 在 rate-driven / AI 個股上有效，
  本實驗測試是否可移植至商品/礦業類別。

================================================================================
基準：COPX-011 Att3（current global best, min(A,B) 0.64）
================================================================================
- Part A: 10 訊號 WR 80.0% Sharpe 0.72 cum +40.03% MDD -6.57% PF 4.29
  - 殘餘 1 SL (2019-04-01 -6.14%) + 1 deep EX (2023-07-12 -4.63%) + 2 mild EX
- Part B: 2 訊號 WR 50.0% Sharpe 0.64 cum +5.35% MDD -4.72% PF 4.55
- min(A,B) **0.64**

================================================================================
Att1（GLD anchor, lookback=20, threshold=-0.05）：FAILED (no effect)
================================================================================
參數：benchmark_ticker="GLD", divergence_lookback=20, min_relative_return=-0.05
結果：訊號集完全等於 COPX-011 Att3 baseline（無任何訊號被過濾）。
分析（trade-level COPX 20d - GLD 20d Rel_GLD 分布）：
  Part A 12 訊號 Rel_GLD 範圍 [-0.0018, +0.1487]：
    最小：2019-12-10 TP -0.18%（接近持平，但仍 > -5%）
    最大：2021-02-16 TP +14.87%
  Part B 2 訊號 Rel_GLD：+10.27%, +12.92%
  - 所有 12 訊號的 Rel_GLD 皆 >= -5%（最低 -0.18% > -5%），threshold 過於寬鬆
  - GLD anchor 在 COPX BB Squeeze breakout 訊號日結構上「天然偏多」：
    breakout 訊號日 COPX 已突破上軌，COPX 20d 必然為正；GLD 20d 通常持平或正，
    Rel_GLD 多數為正
- **REJECT**：threshold -5% 對 COPX-GLD divergence 過於寬鬆，無過濾效果。

================================================================================
Att2（GLD anchor, lookback=20, threshold=+0.05）：FAILED (cooldown shift)
================================================================================
參數：benchmark_ticker="GLD", divergence_lookback=20, min_relative_return=+0.05
結果：
  Part A: 9 訊號 WR 66.7% Sharpe **0.36** cum +16.96%（vs 0.72/+40.03%，**-50% Sharpe**）
    - 過濾 5 訊號（2019-04-01 SL, 2019-12-10 TP, 2021-04-15 TP, 2023-01-06 EX+,
      2023-12-13 EX+），但 cooldown chain shift 重新激活鄰近日期的 4 個替代訊號：
      → 2019-04-04 SL -6.14%（同 SL 結構）
      → 2019-12-12 EX +2.28%（替換 +7% TP，淨損失）
      → 2023-01-10 EX **-3.49%**（替換 +0.79% EX+，**新增大型 EX-**）
      → 2023-12-14 EX +0.98%（替換 +3.42% EX+，淨損失）
    - 淨效果：移除 1 SL + 4 wins，新增 1 SL（同源） + 3 winners（部分降級）
  Part B: 2 訊號完全不變（兩個 Rel_GLD 皆 ≥ +10% 通過 +5% 門檻）
  min(A,B) **0.36** REJECT （-44% vs baseline 0.64）
分析：threshold +5% 的訊號移除集中於低/中等 Rel_GLD 訊號，皆被 cooldown 內鄰近
  訊號替代且替代訊號普遍劣於原訊號。**cooldown chain shift 結構性主導 COPX-011
  的訊號流**——COPX-011 cooldown_days=12 + 訊號密度 ~2/yr，移除任一訊號解除
  12 日 cooldown lockout 必然激活鄰近訊號。

================================================================================
Att3（XLB anchor, lookback=20, threshold=+0.005）：FAILED (cooldown shift)
================================================================================
參數：benchmark_ticker="XLB", divergence_lookback=20, min_relative_return=+0.005
動機：XLB（材料板塊 ETF）為更精準的 anchor——COPX 為材料板塊內子集合，
  Rel_XLB 衡量「礦業 vs 板塊整體」結構性差異而非「礦業 vs 防禦資產」。
trade-level Rel_XLB(20d) 分布：
  2019-04-01 SL: **+0.0018**（最低！明顯異常值）
  其餘 11 訊號: +0.0094 ~ +0.1469
  Threshold +0.005 設計為精準過濾此唯一 SL，理論上可移除 -6.14% 而不誤殺其他訊號。
結果：
  Part A: 10 訊號 WR 80.0% Sharpe **0.72** cum +40.03%（**完全等於 baseline**）
    - 2019-04-01 SL 確實被過濾（Rel_XLB +0.0018 < +0.005）
    - 但 cooldown chain shift 將下一訊號重新計算為 **2019-04-04 SL**（Rel_XLB
      ~+0.01 > +0.005，通過 filter），exit 結果相同 -6.14%
    - 訊號鏈：原 2019-04-01 → 2019-04-04（+3 trading days，cooldown 內），
      新訊號的 4-week 內 BB squeeze + breakout pattern 仍在，且 XLB 已稍微
      偏離初值，Rel_XLB 跨閾值
  Part B: 2 訊號完全不變
  min(A,B) **0.64**（**與 baseline 完全相同**）
分析：surgical XLB filter 精準命中 2019-04-01 SL 但 cooldown chain shift 重新
  激活 2019-04-04 SL（同源 -6.14% 結構）。**核心發現**：COPX-011 殘餘 SLs 為
  「持續性弱突破期」結構，單日 cross-asset divergence 過濾無法解決——失敗模式
  跨越多個交易日，任何「移除某單日訊號」皆會觸發 cooldown 內替代訊號。

================================================================================
最終結論（FAILED EXPERIMENT）
================================================================================
3 次迭代全部失敗，min(A,B) 最佳達 0.64（等於 baseline）。COPX-014 確認
**cross-asset divergence regime gate 在 COPX BB Squeeze Breakout 上結構性失效**：

1. **訊號日 Rel_anchor 結構偏多**（Att1）：BB Squeeze breakout 進場日 COPX
   已突破上軌（短期強勢），Rel_GLD/SPY/XLB 多為正值（COPX 領先），任何
   「下限 floor」式 divergence gate 過於寬鬆無過濾效果。

2. **過嚴 threshold 觸發 cooldown chain shift**（Att2）：threshold 加嚴
   過濾多個訊號後，cooldown_days=12 內必然激活鄰近替代訊號，COPX 多年期
   失敗模式（Q1 2019 base-metals false rally / mid-2023 China weakness /
   2025 Q2 metal pullback）橫跨 1-2 週，鄰近訊號通常具相同失敗結構。

3. **Surgical filter 受 cooldown shift 中性化**（Att3）：精準過濾單一 SL
   訊號（Rel_XLB outlier）的努力被 cooldown 內同源失敗訊號完全抵消。

跨資產貢獻（lesson #20 v3 邊界擴展）：
- TLT-014 / TSLA-017 cross-asset divergence regime gate 成功適用於：
  rate-driven 寬基資產（TLT 1% vol，cooldown_days=7）/
  AI 高 vol 個股（TSLA 4.6% vol，cooldown_days=10）+ BB Squeeze Breakout
- COPX-014 失敗適用範圍：商品/礦業 ETF（COPX 3% vol，cooldown_days=12）+
  BB Squeeze Breakout，當 cooldown_days × 訊號密度 < 1.0（即訊號間距 ~1/yr）
  時，cooldown chain shift 結構性主導任何 secondary filter
- **新跨資產規則**：cross-asset divergence regime gate 適用邊界 =
  「cooldown 視窗 × 訊號密度」應遠 < 1.0（密集訊號流，filter 效應不被
  cooldown shift 抵消）；COPX-011 cooldown 12d × density 0.05/d ≈ 0.6 處於
  邊界以下，secondary filter 結構性失效

COPX-011 Att3 仍為 COPX 全域最優（14 次實驗、42+ 次嘗試）。

成交模型（同 COPX-011）：
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
class COPX014Config(ExperimentConfig):
    """COPX-014 Cross-Asset Divergence Regime-Gated BB Squeeze Breakout 參數

    迭代紀錄（3 次迭代全部失敗，min(A,B) 維持 baseline 0.64）：
      Att1 (GLD, lb=20, thr=-0.05)：訊號集完全等於 baseline 無過濾效果
      Att2 (GLD, lb=20, thr=+0.05)：cooldown chain shift 引入更差替代訊號 → 0.36
      Att3 (XLB, lb=20, thr=+0.005)：surgical filter 被 cooldown shift 中性化 → 0.64

    最終配置：Att3（XLB anchor，作為 documented failure case 保留）
    """

    # === BB Squeeze Breakout 基礎（同 COPX-011）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 12

    # === 多週期趨勢 regime BOX（同 COPX-011 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00
    sma_regime_ratio_max: float = 1.09

    # === Cross-asset divergence regime gate（COPX-014 核心，最終 Att3 配置）===
    # COPX N 日報酬 - benchmark N 日報酬 >= min_relative_return
    # Att3：以 XLB（材料板塊 ETF）為 anchor + lookback 20 + threshold +0.005
    #   surgical filter 試圖過濾 2019-04-01 SL（Rel_XLB +0.0018 唯一 outlier）
    #   實際結果：cooldown chain shift 中性化 → min(A,B) 0.64（等於 baseline）
    benchmark_ticker: str = "XLB"
    divergence_lookback: int = 20
    min_relative_return: float = 0.005


def create_default_config() -> COPX014Config:
    """建立預設配置（Att3：XLB anchor，failed experiment 保留現狀）"""
    return COPX014Config(
        name="copx_014_gld_divergence_breakout",
        experiment_id="COPX-014",
        display_name="COPX Cross-Asset Divergence Regime-Gated BB Squeeze Breakout",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.07,
        stop_loss=-0.06,
        holding_days=20,
    )
