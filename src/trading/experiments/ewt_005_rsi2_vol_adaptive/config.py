"""
EWT-005: RSI(2) Volatility-Adaptive Mean Reversion
(EWT RSI(2) 波動率自適應均值回歸)

完全不同的進場框架：以 RSI(2) 極端超賣取代 pullback+WR，搭配 ATR 過濾。
EWT 日波動 1.41% 在 RSI(2) 有效邊界（≤1.5%），測試是否能改善 Part A Sharpe。

Att1: RSI(2)<10 + 2日跌幅-1.5% + ClosePos≥40% + ATR>1.15
      TP+4.5%/SL-4.5%/20d/冷卻5
      → Part A -0.12 (WR40%, 10訊號) / Part B 0.34 (WR66.7%, 6訊號)
      → 失敗：triple filter 太嚴（僅2訊號/年），4個SL全是地緣政治事件

Att2: 移除2日跌幅（RSI(2)已隱含），TP+4.0%/SL-3.5%/12d
      → Part A 0.05 (WR50%, 12訊號) / Part B 0.05 (WR50%, 6訊號)
      → A/B 平衡極佳但絕對績效太低，SL -3.5% 太緊翻轉贏家

Att3: 同 Att2 進場 + 恢復 SL -4.5% 甜蜜點 + TP+4.5%/12d
      → Part A -0.00 (WR50%, 12訊號) / Part B 0.31 (WR66.7%, 6訊號)
      → 恢復 SL 甜蜜點改善 Part B 但 Part A 仍無法獲利

結論：RSI(2) 對 EWT 無效。確認 cross-asset lesson #27：
非美國單一國家 ETF 受地緣政治事件影響，RSI(2) 訊號在延續性危機中無法恢復。
三次嘗試 min(A,B) 最佳僅 0.05（Att2），均不及 EWT-004 的 0.15。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT005Config(ExperimentConfig):
    """EWT-005 RSI(2) 波動率自適應均值回歸參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # >= 40%

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15  # EWT 甜蜜點

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> EWT005Config:
    return EWT005Config(
        name="ewt_005_rsi2_vol_adaptive",
        experiment_id="EWT-005",
        display_name="EWT RSI(2) Volatility-Adaptive MR",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.045,  # +4.5%（EWT 達標可期）
        stop_loss=-0.045,  # -4.5%（EWT SL 甜蜜點）
        holding_days=12,  # 12 天（縮短持倉，減少到期虧損）
    )
