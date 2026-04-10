"""
EEM-002: Volatility-Adaptive RSI(2) Mean Reversion
(EEM 波動率自適應 RSI(2) 均值回歸)

基於 EEM-001 的 RSI(2) 進場架構，加入 ATR(5)/ATR(20) 波動率飆升過濾。
EEM 日波動 ~1.17%，在 ATR 過濾有效邊界內（≤ 2.25%）。

參考成功案例：
- XLU (~1.0%): ATR > 1.15 → min Sharpe +272%
- IWM (~1.5%): ATR > 1.1 → min Sharpe +67.7%

Att1: ATR > 1.15, ClosePos≥40%, SL -3.0% → Part A -0.02/Part B 0.00(100%WR) ★ BEST
Att2: ATR > 1.1, ClosePos≥40%, SL -3.5% → Part A -0.02/Part B 0.00, 寬 SL 增加虧損不轉贏
Att3: ATR > 1.15, 無 ClosePos, SL -3.0% → Part A -0.07/Part B 1.48, 移除 ClosePos 傷 Part A
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM002Config(ExperimentConfig):
    """EEM-002 波動率自適應 RSI(2) 均值回歸參數"""

    # RSI(2) 參數（同 EEM-001）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 EEM-001）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 EEM-001）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期（同 EEM-001）
    cooldown_days: int = 5


def create_default_config() -> EEM002Config:
    return EEM002Config(
        name="eem_002_vol_adaptive_rsi2",
        experiment_id="EEM-002",
        display_name="EEM Volatility-Adaptive RSI(2)",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
