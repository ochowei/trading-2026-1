"""
IWM-008: Bollinger Band Squeeze Breakout 優化配置
IWM BB Squeeze Breakout Optimized Configuration

基於 IWM-006 (Sharpe 0.31/0.37) 的優化假說：
- Att1 (失敗): 30th 百分位 + 25d + cd10 → Part A 0.19/Part B 0.31（30th 引入劣質訊號）
- Att2 (失敗): 25th 百分位 + 25d + cd10 + SL -4.25% → Part A 0.29/Part B 0.09（SL 太緊翻轉 Part B 贏家）
- Att3 (失敗): 25th 百分位 + 25d + cd10 + SL -4.5% → Part A 0.26/Part B 0.31（cd10 引入邊際訊號稀釋品質）
結論：三次嘗試均未超越 IWM-006 (0.31/0.37)。IWM-006 的 cd15/SL-4.5%/20d 已是 BB Squeeze 最優組合。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM008BBSqueezeConfig(ExperimentConfig):
    """IWM-008 BB Squeeze Breakout 優化策略參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> IWM008BBSqueezeConfig:
    """建立預設配置"""
    return IWM008BBSqueezeConfig(
        name="iwm_008_bb_squeeze_optimized",
        experiment_id="IWM-008",
        display_name="IWM BB Squeeze Breakout Optimized",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.05,
        stop_loss=-0.045,
        holding_days=25,
    )
