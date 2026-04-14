"""
FXI-002: BB Squeeze Breakout
(FXI 布林帶擠壓突破)

FXI-001 均值回歸策略 Part A/B 均虧損（min Sharpe -0.08），嘗試截然不同的策略類型。

設計理據：
- FXI 為中國大型股 ETF，受政策/地緣政治驅動，與 EEM 同屬 EM ETF
- EEM-005 驗證 BB Squeeze 在 EM ETF 上有效（EM risk-on/risk-off 資金流驅動突破）
- 中國市場「政策底→反彈」模式天然適合波動率壓縮後突破
- 參數由 EEM-005 Att2 框架按波動度（FXI 2.0% / EEM 1.17% = 1.71x）縮放

Att1: BB(20,2.0) + 30th pct squeeze + SMA(50) + TP5.0%/SL-4.0%/20天 + cooldown 10
  → Part A -0.22 (18訊號, WR 33.3%), Part B 0.33 (10訊號, WR 60.0%)
  問題：Part A 9/18 停損（假突破多），A/B gap 0.55

Att2: 降 TP 至 4.0% + 縮短持倉至 15天 + 擠壓門檻收緊至 25th
  → Part A -0.23 (18訊號, WR 33.3%), Part B 0.35 (8訊號, WR 62.5%)
  問題：25th pct 移除 2 筆 Part B 好訊號但 Part A 不變，反效果

Att3: 回到 Att1 參數 + SMA(50) 上升斜率過濾（20日正斜率）
  → 過濾下行趨勢中的假突破（Part A 多數停損發生在 SMA 下行期間）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI002Config(ExperimentConfig):
    """FXI-002 BB 擠壓突破參數"""

    # 布林帶參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 擠壓偵測
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30  # 30th percentile
    bb_squeeze_recent_days: int = 5

    # 趨勢確認
    sma_trend_period: int = 50
    sma_slope_lookback: int = 20  # SMA(50) 上升斜率回看天數

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FXI002Config:
    return FXI002Config(
        name="fxi_002_bb_squeeze_breakout",
        experiment_id="FXI-002",
        display_name="FXI BB Squeeze Breakout",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（FXI 2.0% vol 突破目標）
        stop_loss=-0.040,  # -4.0%（EM 停損不宜過寬，R:R = 1.25）
        holding_days=20,
    )
