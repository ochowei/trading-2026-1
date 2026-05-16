"""
DIA-017 Buffered Multi-Week SMA Trend-Regime-Gated MR 配置

策略方向（lesson #22 Buffered Multi-Week SMA Trend Regime Gate，
cross-strategy port from XBI-015 lesson #22→Pullback MR 擴展）：
  在 DIA-012 Att2（min(A,B)† 1.31）的 RSI(2)+2DD+ClosePos+1d cap+3d cap MR
  框架上，新增 lesson #22 buffered SMA(20) >= k × SMA(60) 趨勢 regime 閘門
  （可選 Close > SMA(200)），測試 trend-regime classifier 能否移除
  DIA-012 殘餘 Part A SL 2022-01-18。

trade-level signal-day lesson #22 SMA(20)/SMA(60) ratio pre-analysis
（DIA-012 12 Part A + 3 Part B）：

  | date       | tag | SMA20/SMA60 | Close>SMA200 |
  |------------|-----|-------------|--------------|
  | 2022-01-18 | SL  | **1.0096**  | **True**     | ★ 殘餘 SL：偽多頭 regime
  | 2022-06-14 | TP  | 0.9668      | False        | ← bear-rally 贏家
  | 2022-09-23 | TP  | 0.9801      | False        | ← bear-rally 贏家
  | 2019-05-29 | TP  | 0.9951      | False        | ← bear/neutral 贏家
  | 2020-02-28 | TP  | 1.0005      | False        | ← COVID-bottom 贏家
  | 其餘 8 TP  | —   | >= 1.0013   | mostly True  |

  **預期結構性失敗（reverse-selection）**：DIA-012 殘餘 SL 2022-01-18
  發生於 2022 升息熊市「起點」——SMA(20)/SMA(60)=1.0096 仍偽多頭、
  Close > SMA(200)，**通過任何 bull-regime gate**；反之 DIA 最佳 MR 贏家
  恰為 bear-regime / oversold capitulation 進場（2022-06-14 / 2022-09-23
  ratio < 0.98 + below SMA200；2019-05-29 / 2020-02-28 ratio ~1.0 +
  below SMA200），**bull-regime gate 將系統性移除這些 bear-rally V-bounce
  贏家而保留 regime-shift SL**——確認 DIA-013 Att2（SMA(200) regime gate
  非選擇性）發現，建立 lesson #22 family 失敗邊界。

跨資產脈絡（lesson #22 family）：
- TSLA-015 / NVDA-012 / FCX-013 ✓（高 vol 單股 BB Squeeze Breakout）
- COPX-011 ✓（商品/礦業 ETF，regime BOX 雙向過濾）
- XBI-015 ✓（生技板塊 ETF，lesson #22→Pullback MR cross-strategy 首次）
- USO-024 ✗（純單一商品 ETF，event-driven driver 無區分力）
- **DIA-017（本實驗）：低波動美國寬基指數 ETF capitulation MR，預期
  lesson #22 family 第 2 次失敗——首次「broad index MR 之 bear-rally
  winner 被 bull-regime gate 反向移除」失敗類型**

迭代計畫：
- Att1：sma_fast=20, sma_slow=60, k=1.00（bull regime gate）
- Att2：k=0.99（XBI-015 buffered 風格，放寬 1%）
- Att3：+ Close > SMA(200) 嚴格 regime（DIA-013 Att1 風格）/ ablation

驗收目標（goal）：min(A,B) Sharpe > DIA-012 Att2 1.31†；A/B cum gap < 30%；
signal gap < 50%；必須使用成交模型（execution model）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA017Config(ExperimentConfig):
    """DIA-017 Buffered Multi-Week SMA Trend-Regime-Gated MR 參數"""

    # === MR 進場框架（完全沿用 DIA-012 Att2）===
    rsi_period: int = 2
    rsi_threshold: float = 10.0
    decline_lookback: int = 2
    decline_threshold: float = -0.015
    close_position_threshold: float = 0.4
    oneday_return_cap: float = -0.020
    threeday_return_cap: float = -0.07
    cooldown_days: int = 5

    # === DIA-017 核心新增：lesson #22 buffered multi-week SMA trend regime ===
    sma_fast: int = 20
    sma_slow: int = 60
    sma_long: int = 200
    # bull-regime gate：SMA(fast) >= regime_k × SMA(slow)
    # Att1 1.00 / Att2 0.99（buffered，XBI-015 風格）/ Att3 + require_above_long
    regime_k: float = 1.00
    # Att3：是否額外要求 Close > SMA(200)（DIA-013 Att1 嚴格 secular bull）
    require_above_long: bool = False


def create_default_config() -> DIA017Config:
    return DIA017Config(
        name="dia_017_trend_regime_gate_mr",
        experiment_id="DIA-017",
        display_name="DIA Buffered Multi-Week SMA Trend-Regime-Gated MR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=25,
    )
