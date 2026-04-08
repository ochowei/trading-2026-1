"""
XLU-009: Keltner Channel Squeeze Breakout 配置
XLU Keltner Channel Squeeze Breakout Configuration

假說：使用 TTM Squeeze 概念（BB 收縮至 KC 內部）偵測波動壓縮，
當 BB 擴張超過 KC（squeeze 釋放）且價格突破 KC 上軌時進場。
Keltner Channel 使用 ATR（平滑化的真實波幅）而非標準差，
在低波動資產（XLU 日波動 ~1.08%）上可能提供更穩定的突破訊號。

vs XLU-004 關鍵差異：
1. Squeeze 偵測：BB 在 KC 內部（TTM 概念）vs BB 寬度百分位
2. 突破閾值：KC 上軌（ATR-based）vs BB 上軌（StdDev-based）
3. KC 使用 EMA（反應更快）vs BB 使用 SMA
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU009KeltnerSqueezeConfig(ExperimentConfig):
    """XLU-009 Keltner Channel Squeeze Breakout 策略專屬參數"""

    # Bollinger Bands（用於 Squeeze 偵測）
    bb_period: int = 20
    bb_std: float = 2.0

    # Keltner Channel
    kc_ema_period: int = 20
    kc_atr_period: int = 10
    kc_multiplier: float = 1.5

    # Squeeze 條件
    squeeze_recent_days: int = 5

    # 趨勢確認
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> XLU009KeltnerSqueezeConfig:
    """建立預設配置"""
    return XLU009KeltnerSqueezeConfig(
        name="xlu_009_keltner_squeeze_breakout",
        experiment_id="XLU-009",
        display_name="XLU Keltner Channel Squeeze Breakout",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.04,
        holding_days=20,
    )
