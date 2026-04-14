"""
CIBR-004: RSI(2) 波動率自適應均值回歸配置

策略假說：RSI(2) 極端超賣框架在美國寬基指數 ETF（SPY/DIA/IWM/VOO）上已驗證有效
（日波動 ≤ 1.5-2.0%）。CIBR 日波動 1.53% 處於有效範圍內，且作為美國上市的
網路安全板塊 ETF，可能與美國寬基指數有類似的均值回歸特性，而非像非美國 ETF
（VGK/INDA/EWT）受宏觀/地緣政治事件干擾。

進場參數設計邏輯：
- RSI(2) < 10：極端超賣，跨資產通用門檻
- 2日跌幅 >= 2.0%：按 CIBR 波動度縮放（SPY 1.5% @ 1.2% vol, IWM 2.5% @ 1.75% vol）
- ClosePos >= 40%：日內反轉確認，CIBR 1.53% 在有效邊界內
- ATR(5)/ATR(20) > 1.15：CIBR-002 已驗證此門檻有效

出場參數設計邏輯：
- TP +3.5% / SL -4.0%：沿用 CIBR-002 已驗證的出場參數
- 持倉 15天：RSI(2) 捕捉更極端超賣，預期回復更快（vs CIBR-002 的 18天）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBRRSI2Config(ExperimentConfig):
    """CIBR-004 RSI(2) 波動率自適應均值回歸參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.02  # 2日跌幅 >= 2.0%

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.40  # >= 40%

    # 波動率自適應過濾器
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15  # CIBR-002 已驗證

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> CIBRRSI2Config:
    return CIBRRSI2Config(
        name="cibr_004_rsi2_vol_adaptive",
        experiment_id="CIBR-004",
        display_name="CIBR RSI(2) Volatility-Adaptive",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=15,  # 15天
    )
