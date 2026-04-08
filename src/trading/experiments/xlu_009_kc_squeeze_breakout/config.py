"""
XLU-009: Keltner Channel Squeeze Breakout 配置
XLU KC Squeeze Breakout Configuration

假說：Keltner Channel 使用 ATR（含缺口/日內波動）而非標準差衡量波動度，
可能產生與 BB Squeeze 不同且更均勻分布的突破訊號。
XLU 日波動 ~1.08%，與 GLD 相似，低波動資產的 KC 突破可能比 BB 更穩定。

KC 與 BB 的關鍵差異：
- BB 使用 SMA + N × σ（收盤對收盤波動）
- KC 使用 EMA + N × ATR（含缺口和日內極端波動）
- ATR 對缺口敏感，可能捕捉 BB 遺漏的波動收縮後真正突破
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU009KCSqueezeConfig(ExperimentConfig):
    """XLU-009 KC Squeeze Breakout 策略專屬參數"""

    ema_period: int = 20
    atr_period: int = 10
    kc_multiplier: float = 2.5
    kc_squeeze_percentile_window: int = 60
    kc_squeeze_percentile: float = 0.30
    kc_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> XLU009KCSqueezeConfig:
    """建立預設配置"""
    return XLU009KCSqueezeConfig(
        name="xlu_009_kc_squeeze_breakout",
        experiment_id="XLU-009",
        display_name="XLU KC Squeeze Breakout",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.04,
        holding_days=20,
    )
