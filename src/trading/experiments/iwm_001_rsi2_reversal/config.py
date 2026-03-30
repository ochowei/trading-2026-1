"""
IWM-001: RSI(2) 極端超賣均值回歸
(IWM RSI(2) Extreme Oversold Mean Reversion)

IWM (Russell 2000 ETF) 日波動度 ~1.5-2%，介於 SPY (~1.2%) 和 SIVR (~2-4%) 之間。
參考 VOO-002/DIA-003 的 RSI(2) 非對稱出場架構，按 IWM 波動度微調：
- TP +3.0%（SPY/VOO +2.5% 的 1.2x）
- SL -4.5%（非對稱寬停損，匹配 IWM 較高波動）
- 持倉 20 天（給予充分回歸時間）
- 2 日跌幅 >= 2.0%（SPY 1.5% 的 ~1.3x，匹配更高波動）
- 無 trailing stop（日波動 ~1.5-2%，邊界區域不用）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWMRsi2Config(ExperimentConfig):
    """IWM RSI(2) 極端超賣均值回歸參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10（極端超賣）

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.025  # 2 日跌幅 >= 2.5%（IWM 波動較高，嚴格過濾）

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) >= 40%

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> IWMRsi2Config:
    return IWMRsi2Config(
        name="iwm_001_rsi2_reversal",
        experiment_id="IWM-001",
        display_name="IWM RSI(2) Extreme Oversold Reversal",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.045,  # -4.5%（非對稱寬停損，匹配 IWM 較高波動）
        holding_days=20,  # 20 天
    )
