"""
SIVR-008: Bollinger Band Squeeze Breakout 配置
SIVR BB Squeeze Breakout Configuration

假說：SIVR 為實體白銀 ETF，白銀價格在波動收縮後常出現趨勢性突破。
日波動 2-3% 類似 FCX（2-4%），FCX-004 BB Squeeze 已驗證有效。
SIVR-001~007 均為均值回歸策略，本實驗首次嘗試突破方向。

參數設計（Attempt 3 最佳）：
- BB(20,2) + 60日 20th 百分位擠壓 + 5日內：比 FCX-004 更嚴格
- SMA(50) 趨勢確認：同 FCX-004
- TP +5.0% / SL -5.0% / 20天：SIVR 波動低於 FCX，TP/SL 從 +8%/-7% 縮放
- 冷卻 15 天：延長以避免連續假突破

結果：三次嘗試均失敗，最佳 Part A Sharpe 0.11 / Part B 0.10，
遠不如 SIVR-005 均值回歸（0.22/0.26）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRBBSqueezeConfig(ExperimentConfig):
    """SIVR BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.20
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> SIVRBBSqueezeConfig:
    """建立預設配置"""
    return SIVRBBSqueezeConfig(
        name="sivr_008_bb_squeeze_breakout",
        experiment_id="SIVR-008",
        display_name="SIVR BB Squeeze Breakout",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.05,
        stop_loss=-0.05,
        holding_days=20,
    )
