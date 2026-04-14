"""
VGK-002: Volatility-Adaptive RSI(2) Mean Reversion
(VGK 波動率自適應 RSI(2) 均值回歸)

基於 VGK-001 的 RSI(2) 進場架構，加入 ATR(5)/ATR(20) 波動率飆升過濾：
- VGK-001 Part A Sharpe -0.06（2022 歐洲能源危機/俄烏戰爭慢跌產生假訊號）
- ATR 過濾在相近波動度資產上表現極佳：XLU(1.0%) ATR>1.15 → +272%，IWM(1.5%) ATR>1.1 → +67.7%
- VGK 日波動 1.12% 在 ATR 有效邊界內（≤2.25%）

Att1: ATR>1.15 + SL-3.5% → Part A -0.26 / Part B 0.89（ATR 太嚴，移除 5 個好訊號）
Att2: ATR>1.1 + SL-3.0% → Part A -0.19 / Part B 1.00（同 Att1 訊號，ATR 門檻無差異）
Att3: 無 ATR + TP3.5%/SL-3.5%/25d/cooldown10d → 延長持倉+寬出場（參考 DIA-005）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK002Config(ExperimentConfig):
    """VGK-002 波動率自適應 RSI(2) 均值回歸參數"""

    # RSI(2) 參數（同 VGK-001）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 VGK-001）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 VGK-001）
    close_position_threshold: float = 0.4

    # 冷卻期（從 5 天增加至 10 天，防止持續下跌中連續進場）
    cooldown_days: int = 10


def create_default_config() -> VGK002Config:
    return VGK002Config(
        name="vgk_002_vol_adaptive_rsi2",
        experiment_id="VGK-002",
        display_name="VGK Volatility-Adaptive RSI(2)",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（寬出場，參考 DIA-005）
        stop_loss=-0.035,  # -3.5%（寬出場，參考 DIA-005）
        holding_days=25,  # 延長持倉，給交易更多時間恢復
    )
