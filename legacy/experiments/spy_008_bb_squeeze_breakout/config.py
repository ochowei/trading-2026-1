"""
SPY-008: Bollinger Band Squeeze Breakout 配置
SPY BB Squeeze Breakout Configuration

假說：SPY 作為科技股權重最高的大盤指數，在波動收縮後的突破可能產生有意義的動能。
基於 TSLA-005/NVDA-004/FCX-004 成功經驗（日波動 2-5%），適配至 SPY（日波動 ~1.0-1.2%）。
SPY-001~007 均為均值回歸或趨勢跟蹤策略，本實驗首次嘗試突破方向。
注意：DIA-006 BB Squeeze 在低波動指數上結果較差（Part A 0.10），SPY 需驗證是否因科技權重較高而有更好表現。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPYBBSqueezeConfig(ExperimentConfig):
    """SPY BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> SPYBBSqueezeConfig:
    """建立預設配置"""
    return SPYBBSqueezeConfig(
        name="spy_008_bb_squeeze_breakout",
        experiment_id="SPY-008",
        display_name="SPY BB Squeeze Breakout",
        tickers=["SPY"],
        data_start="2018-01-01",
        profit_target=0.03,
        stop_loss=-0.03,
        holding_days=20,
    )
