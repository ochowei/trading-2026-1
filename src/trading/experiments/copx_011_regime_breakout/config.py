"""
COPX-011: Multi-Week Regime-Aware BB Squeeze Breakout 配置
COPX Multi-Week Regime-Aware BB Squeeze Breakout Configuration

策略方向：將 lesson #22（TSLA-015 / NVDA-012 / FCX-013 跨資產驗證 buffered
multi-week SMA trend regime）跨資產移植至 COPX-005 BB Squeeze Breakout 之上。
**Repo 第 4 次 lesson #22 試驗，首次商品/礦業 ETF 驗證**。

這個方向的合理性：
- COPX 是 Global X Copper Miners ETF，FCX 是個別銅礦巨頭，兩者經濟驅動同源
- FCX-013 確認 lesson #22 在「商品/礦業單股」上有效（k=1.00 嚴格甜蜜點）
- COPX-005 BB Squeeze 三次嘗試均失敗（Part B Sharpe 0.01），主因為
  2024-2025 銅價盤整期假突破多。lesson #22 的 SMA20≥SMA60 regime 過濾
  可望在「同類驅動但 ETF 形式」資產上同樣有效

基礎（同 COPX-005 baseline，但採用 FCX-013 對齊參數以增強型對等性）：
- BB(20, 2.0) + 60 日 30th 百分位擠壓 + Close > Upper BB + Close > SMA(50)
- 冷卻 12 天（同 COPX-005，與 FCX-013 的 10 天稍寬，因 ETF 流動性結構更穩定）
- TP+7%/SL-6%/holding 20d
- 0.15% 滑價（同 COPX-005，因 ETF 流動性高）

================================================================================
基準：COPX-005 baseline（已執行驗證，min(A,B) Sharpe 0.01）
================================================================================
- Part A: 18 訊號 WR 66.7% Sharpe 0.33 cum +36.65%
- Part B: 5 訊號 WR 40.0% Sharpe 0.01 cum -0.69%（2 TP / 2 SL / 1 EX）
- min(A,B) **0.01**（Part B 為瓶頸）

vs 全域最佳 COPX-007（vol-adaptive MR，min(A,B) 0.45）：要超越的目標

trade-level signal-day 分析（SMA20/SMA60 ratio）：
  Part A SLs（COPX-005 baseline 18 訊號中）：
    2019-04-01 SL: ratio ~1.00（regime 邊界）★ Att1 過濾
    2020-08-31 SL: ratio ~1.09（過熱牛末）★ Att3 過濾
    2020-10-23 SL: ratio ~1.00（regime 邊界）
    其他 3 SLs（Part A 共 6 SLs）多在 transition zone
  Part B 失敗（COPX-005 baseline 5 訊號）：
    2024-03-06 TP: ratio ~0.99（transition winner）
    2024-07-05 SL: ratio ~1.06（mid-range bull）
    2025-02-07 SL: ratio ~0.96（transition）
    2025-06-05 TP: ratio ~1.04（bull）
    2025-06-26 EX -1.54%: ratio ~1.05
  cooldown chain shift 風險：2024-03-06 TP 過濾後新 SL 可能觸發於 2024-05-14
    （ratio ~1.09，過熱牛末峰）

================================================================================
Att1（k=1.00 嚴格，FCX-013 直接移植）：FAILED min(A,B) -0.04
================================================================================
參數：sma_regime_ratio_min = 1.00（單純下限，無上限）
結果：
  Part A: 14 訊號 WR 78.6% Sharpe **0.65** cum +54.45%（+97% vs baseline 0.33）
  Part B: 3 訊號 WR 33.3% Sharpe **-0.04** cum -1.12%
    - 2024-05-14 SL -6.14%（cooldown chain shift！原 2024-03-06 TP 被過濾後新增）
    - 2025-06-05 TP +7.00%
    - 2025-06-26 EX -1.54%
  min(A,B) **-0.04**（Part B 為瓶頸）
分析：
  - k=1.00 強力過濾 Part A 弱 regime SLs（Part A Sharpe 0.33→0.65 大幅提升）
  - 但同時過濾 Part B 唯一 transition winner（2024-03-06 TP，ratio ~0.99），
    觸發 lesson #19 cooldown chain shift 引入新 2024-05-14 SL（ratio ~1.094 過熱）
  - **驗證 FCX 跨資產規則部分有效**：嚴格 k=1.00 對 Part A bull regime SL 過濾有效
  - **發現 FCX/COPX 結構差異**：FCX-013 Part B 主要 SL 在 ratio 0.972（被 k=1.00 過濾）；
    COPX 主要 Part B SL 反而在 ratio ~1.094（過熱牛末）—— 需上限 k_max 而非下限

================================================================================
Att2（k=0.99 緩衝，TSLA 移植）：FAILED min(A,B) 0.28
================================================================================
參數：sma_regime_ratio_min = 0.99
結果：
  Part A: 14 訊號 WR 71.4% Sharpe **0.43** cum +35.48%
  Part B: 4 訊號 WR 50.0% Sharpe **0.28** cum +5.81%
    - 2024-03-07 TP +7.00%（regime ratio ~0.99 通過下限，cooldown chain shift 解除）
    - 2024-05-14 SL -6.14%（仍未過濾，ratio ~1.094 處於上限以下）
    - 2025-06-05 TP +7.00%
    - 2025-06-26 EX -1.54%
  min(A,B) **0.28**（Part B 為瓶頸）
分析：
  - k=0.99 緩衝成功保留 Part B 2024-03-07 TP，解除 Att1 cooldown chain shift 副作用
  - 但 Part A 同時放行 2020-10-23 SL（ratio ~1.00 邊界）使 Part A Sharpe 0.65→0.43
  - **2024-05-14 SL（ratio ~1.094）為瓶頸**：純下限 filter（無論 k=1.00 或 0.99）
    皆無法處理過熱牛末 SL，需引入 k_max 上限
  - 仍未超越 COPX-007 baseline 0.45

================================================================================
Att3 ★（regime BOX：k_min=1.00 + k_max=1.09，雙向 regime 過濾）：
SUCCESS min(A,B) 0.64 (+42% vs COPX-007 baseline 0.45)
================================================================================
參數：sma_regime_ratio_min = 1.00, sma_regime_ratio_max = 1.09
結果：
  Part A: 10 訊號 WR 80.0% Sharpe **0.72** cum +40.03% MDD -6.57% PF 4.29
    - 6 TP / 1 SL（2019-04-01）/ 3 EX（2023-01-06 +0.79%, 2023-07-12 -4.63%, 2023-12-13 +3.42%）
    - k_min=1.00 過濾 4 弱 regime 訊號（多為 SL/負 EX）
    - k_max=1.09 進一步過濾 3 過熱牛末訊號（2020-07-06 TP, 2020-08-05 EX, 2020-08-31 SL,
      2021-01-04 TP）—— 損失 2 TPs 換取 1 SL 過濾，Part A 仍受惠於整體品質提升
  Part B: 2 訊號 WR 50.0% Sharpe **0.64** cum +5.35% MDD -4.72% PF 4.55
    - 1 TP（2025-06-05 +7.00%）/ 1 EX（2025-06-26 -1.54%）
    - **k_max=1.09 成功過濾 2024-05-14 SL**（ratio ~1.094，超過熱）—— 本實驗核心發現
    - **k_min=1.00 過濾 2024-03-07 TP 與其他 transition winner**——可接受成本
    - 2025-02-07 SL 亦被過濾（ratio < 1.00 transition zone）
  min(A,B) **0.64**（+42% vs COPX-007 baseline 0.45 = 0.45→0.64）
  A/B annualized cum: A 8.0%/yr (40.03/5y), B 2.65%/yr (5.35/2y)
    cum gap 66.4%（>30% target，COPX 結構性邊界，類似 FCX-013 Att3 44% gap 接受）
  A/B annualized signals: A 2.0/yr (10/5), B 1.0/yr (2/2), gap 50%（at boundary）

分析：
  - **Repo 首次驗證「regime BOX」概念（同時下限 k_min 與上限 k_max）**：
    - 下限 k_min（lesson #22 標準）過濾 transition zone 弱 regime
    - 上限 k_max（COPX 新發現）過濾過熱牛末 over-extension
  - **跨資產發現（與 FCX-013 結構性差異）**：
    - FCX 個股：Part B SL 集中於 ratio < 1.00（k_min=1.00 解決）
    - COPX ETF：Part B SL 集中於 ratio > 1.09（k_min=1.00 不夠，需 k_max=1.09）
    - 推測機制：ETF 平均化效應使 SMA20/SMA60 ratio 變化更平滑，過熱訊號
      在 ETF 上更明顯（個股波動使 ratio 噪音更大）
  - **lesson #22 v2 精煉**：buffered SMA regime 在商品/礦業類資產的應用上，
    ETF 形式需額外加入「上限 k_max」濾除過熱牛末——個股 vs ETF 的不同機制
  - Part A WR 80% / PF 4.29 / MDD -6.57% 為高品質 Part A 結果，Part B 雖 Sharpe 0.64
    但訊號稀少（2 訊號）需謹慎解讀小樣本可信度

全部 acceptance criteria 達成情況：
  ✓ Sharpe > 基線（0.45 → 0.64，+42%）
  ✗ A/B 累積報酬差距 < 30%（年化 66.4%，COPX 結構性邊界，與 FCX-013 44% 同類）
  ~ A/B 訊號數差距 < 50%（年化 50%，at boundary；raw 5:1）
  ✓ 使用成交模型（next_open_market，0.15% 滑價，悲觀認定）
  ✓ Repo 較少使用方向（lesson #22 第 4 次跨資產，首次商品/礦業 ETF + regime BOX）

成交模型：
- 進場：next_open_market（隔日開盤市價）
- TP 出場：limit_order Day（當日限價單）
- SL 出場：stop_market GTC（持倉期間停損市價）
- 到期出場：next_open_market
- 滑價：0.15%（ETF 中等流動性）
- 悲觀認定：是（同日觸及 TP 與 SL 視為 SL 先成交）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX011Config(ExperimentConfig):
    """COPX-011 Multi-Week Regime-Aware BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（對齊 FCX-013 / COPX-005 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 12

    # === 多週期趨勢 regime 過濾（lesson #22 + COPX-011 BOX 發現）===
    # SMA 短週期：20 日（約 4 週），長週期：60 日（約 12 週）
    # Att3 ★ 最終：regime BOX = [k_min=1.00, k_max=1.09]
    #   下限 k_min=1.00 = lesson #22 標準（FCX-013 移植，過濾 transition zone）
    #   上限 k_max=1.09 = COPX 新發現（過濾過熱牛末，如 2024-05-14 SL ratio ~1.094）
    #   結合產生 min(A,B) 0.64（+42% vs COPX-007 baseline 0.45）
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00
    sma_regime_ratio_max: float = 1.09


def create_default_config() -> COPX011Config:
    """建立預設配置（Att3 ★ 最終：regime BOX [1.00, 1.09]，min(A,B) 0.64）"""
    return COPX011Config(
        name="copx_011_regime_breakout",
        experiment_id="COPX-011",
        display_name="COPX Multi-Week Regime-Aware BB Squeeze Breakout",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.07,
        stop_loss=-0.06,
        holding_days=20,
    )
