"""
USO-024: Multi-Week Regime-Aware BB Squeeze Breakout 配置
USO Multi-Week Regime-Aware BB Squeeze Breakout Configuration

策略方向：將 lesson #22（TSLA-015 / NVDA-012 / FCX-013 / COPX-011 跨資產驗證
buffered multi-week SMA trend regime）跨資產移植至 USO-021 BB Squeeze Breakout
之上。**Repo 第 5 次 lesson #22 試驗，首次純單一商品 ETF（原油）驗證**。

================================================================================
3 次迭代全部失敗 — 擴展 lesson #22 失敗邊界至「純單一商品 ETF」
================================================================================

基線比較：USO-013 全域最優 min(A,B) Sharpe 0.26（純 MR 框架，緊密回檔範圍 7-12% +
RSI(2)<15 + 2DD≤-2.5%），是要超越的目標。

本次實驗對齊 COPX-011（commodity ETF lesson #22 唯一成功案例）參數：
- BB(20, 2.0) + 60 日 30th 百分位擠壓 + Close > Upper BB + Close > SMA(50)
- TP+5%/SL-5%/holding 20d/cooldown 10d
- 0.10% 滑價（USO 高流動性）

================================================================================
Att1（k=1.00 嚴格，FCX-013 / COPX-011 純下限直接移植）：FAILED min(A,B) -0.01
================================================================================
參數：sma_regime_ratio_min = 1.00, sma_regime_ratio_max = 999（停用）
結果：
  Part A: 12 訊號 WR 66.7% Sharpe **0.38** cum +21.49% MaxDD -6.94% PF 2.10
    - 8 TP / 4 SL（2020-01-03 pre-COVID, 2022-05-16 oil-peak, 2022-11-04 post-peak,
      其他 1 SL）
  Part B: 4 訊號 WR 50.0% Sharpe **-0.01** cum -0.70% MaxDD -5.96% PF 0.98
    - 2 TP（2024-03-14, 2025-01-02）/ 2 SL（2025-06-12 Iran-Israel spike-reverse,
      2025-07-29 OPEC+ unwind）
  min(A,B) **-0.01**（vs USO-013 baseline 0.26，FAILED）

分析：
  - Part A 略改善（USO-021 baseline 0.22→0.38），規範閘門過濾部分弱 regime SLs
  - Part B 完全 break：2 個快速 SL（1日/3日）為 mid-2025 oil 地緣政治衝擊後反轉
  - SMA20/SMA60 ratio 在 mid-2025 仍處 [1.00, 1.05] 範圍（不算過熱），純下限無法過濾

================================================================================
Att2（regime BOX，COPX-011 移植：k_min=1.00 + k_max=1.09）：FAILED min(A,B) -0.01
================================================================================
參數：sma_regime_ratio_min = 1.00, sma_regime_ratio_max = 1.09
結果：
  Part A: 9 訊號 WR 55.6% Sharpe **0.13** cum +4.95% PF 1.31
  Part B: 4 訊號（**完全不變**）WR 50% Sharpe -0.01 cum -0.70%
  min(A,B) **-0.01**（FAILED）

分析：
  - **k_max=1.09 對 Part B 完全非綁定**：所有 4 個 Part B 訊號 ratio 皆 < 1.09，
    即 Part B 並非「過熱牛末」結構（不同於 COPX 2024-05-14 SL ratio 1.094）
  - k_max 在 Part A 移除 3 訊號（含部分 winners），Part A Sharpe 大幅退化（0.38→0.13）
  - **核心發現**：USO 2024-2025 處於「moderate regime」橫盤，整體 ratio 在 1.00-1.05
    區間，與 COPX 的「明顯過熱牛末」結構不同

================================================================================
Att3（squeeze 收緊：20th percentile + 3 日內，保留 BOX [1.00, 1.09]）：
FAILED min(A,B) -0.36（最差）
================================================================================
參數：bb_squeeze_percentile = 0.20, bb_squeeze_recent_days = 3,
     sma_regime_ratio_min = 1.00, sma_regime_ratio_max = 1.09
結果：
  Part A: 8 訊號 WR 62.5% Sharpe 0.29 cum +10.59% PF 1.79
  Part B: 3 訊號 WR 33.3% Sharpe **-0.36** cum -5.43% PF 0.49
    - 1 TP（2024-03-14）/ 2 SL（2025-06-12, 2025-07-29 — 仍未過濾）
    - 2025-01-02 winner 被收緊 squeeze 移除
  min(A,B) **-0.36**（三次最差）

分析：
  - 收緊 squeeze percentile 30th→20th + 5d→3d 反向選擇：
    - 移除 1 個 Part B winner（2025-01-02）
    - 兩個 mid-2025 SLs 保留（squeeze 條件本身已被滿足，緊度不是區分點）
  - **失敗根因**：USO 2025-06/07 SLs 為「真實 squeeze 後突破隨即反轉」結構，
    與假突破不同——squeeze percentile 不具區分力

================================================================================
核心跨資產發現：lesson #22 在純單一商品 ETF（油）失敗
================================================================================

USO-024 為 **repo 第 5 次 lesson #22 跨資產試驗，首次純單一商品 ETF**：
  - TSLA-015 ★ (3.72% vol AI growth stock, k=0.99 buffered)
  - NVDA-012 ★ (2.5-3% vol AI growth stock, k=0.97 buffered, BB Squeeze)
  - NVDA-013 ★ (cross-strategy MBPC, k=1.00 strict + ATR vol regime)
  - FCX-013 ★ (3% vol commodity/mining stock, k=1.00 strict)
  - COPX-011 ★ (2.25% vol commodity/mining ETF, BOX [1.00, 1.09])
  - **USO-024 ✗ (2.2% vol pure single-commodity ETF, ALL 3 ATTEMPTS FAILED)**

**結構性差異（為何 USO 失敗而 COPX 成功）**：
  1. **regime 結構**：COPX（銅礦 ETF）2024-2025 經歷明顯銅價週期過熱（2024-05 ratio
     >1.09），可被 k_max=1.09 過濾；USO（油 ETF）2024-2025 為地緣政治驅動的橫盤
     氛圍，ratio 集中於 [1.00, 1.05]，無「過熱牛末」訊號可被 k_max 過濾
  2. **SL 機制**：COPX SLs 集中於 transition zone（ratio<1.00）+ 過熱牛末（ratio>1.09），
     雙向過濾有效；USO Part B SLs 為 mid-regime 的「快速地緣政治反轉」
     （Iran-Israel spike, OPEC+ unwind），ratio 區間正常，regime gate 無區分力
  3. **資產驅動因子**：COPX 為「銅價 ETF」由銅礦企業基本面 + 銅價共同驅動，價格平滑；
     USO 為「原油期貨 ETF」直接 expose 油價，受 OPEC+/地緣政治單日衝擊明顯，
     即便 regime 健康時亦易發生 1-3 日反轉

**lesson #22 邊界精煉（USO-024 加入）**：
  - 適用：高波動單股（TSLA/NVDA/FCX）+ 混合驅動商品 ETF（COPX 銅礦企業）
  - 不適用：純單一商品 ETF（USO 原油），其 SLs 受地緣政治衝擊主導而非 regime
  - 此規則平行 lesson #20b（V-bounce hook 失敗家族）：當資產主驅動為「外部
    事件衝擊」（USO 油 / FXI 中國政策 / TLT 利率）時，技術面 regime gate 結構性
    失效

**USO-013 仍為全域最優**（24 次實驗、33+ 次嘗試），確認 USO 純技術面策略
Sharpe 結構性上限約 0.26。

================================================================================
最終配置：保留 Att1（純下限 k=1.00）為「最低傷害」失敗版本
================================================================================
雖然 3 次皆失敗，最終配置選擇 Att1（k_max 停用）作為書面記錄，因為：
  - Att1 Part A Sharpe 0.38（三次最佳），記錄「lesson #22 對 Part A 部分有效」
  - Att2/Att3 雖嘗試 k_max 與 squeeze 收緊，皆無法救援 Part B
  - 文件保留三次嘗試完整參數供後續複現

成交模型：
- 進場：next_open_market（隔日開盤市價）
- TP 出場：limit_order Day（當日限價單）
- SL 出場：stop_market GTC（持倉期間停損市價）
- 到期出場：next_open_market
- 滑價：0.10%（USO 高流動性）
- 悲觀認定：是（同日觸及 TP 與 SL 視為 SL 先成交）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO024Config(ExperimentConfig):
    """USO-024 Multi-Week Regime-Aware BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（最終 = Att1 baseline 30th + 5 日內）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime 過濾（lesson #22 + COPX-011 BOX 移植）===
    # SMA 短週期：20 日（約 4 週），長週期：60 日（約 12 週）
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    # 最終 = Att1：純下限 k_min=1.00（k_max=999 停用）為三次中最佳結構
    sma_regime_ratio_min: float = 1.00
    sma_regime_ratio_max: float = 999.0


def create_default_config() -> USO024Config:
    """建立預設配置（Att1 final：k_min=1.00 strict, k_max disabled）"""
    return USO024Config(
        name="uso_024_regime_breakout",
        experiment_id="USO-024",
        display_name="USO Multi-Week Regime-Aware BB Squeeze Breakout",
        tickers=["USO"],
        data_start="2019-01-01",
        profit_target=0.05,
        stop_loss=-0.05,
        holding_days=20,
    )
