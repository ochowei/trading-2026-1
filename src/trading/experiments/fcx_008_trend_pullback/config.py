"""
FCX-008: Trend Pullback to SMA(50) 配置
FCX Trend Pullback Strategy Configuration

假說：FCX 為銅礦週期股，銅價上升週期中 FCX 常有強趨勢。
當 SMA(50)>SMA(200) 確認上升趨勢，且價格回檔測試 SMA(50) 後反彈，
提供順勢進場機會。

基於 DIA-007 趨勢回檔框架，按 FCX 日波動 2-4% 縮放參數。
FCX-001~007 未嘗試過純趨勢跟蹤方向。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXTrendPullbackConfig(ExperimentConfig):
    """FCX-008 Trend Pullback 策略專屬參數"""

    # SMA 參數
    sma_fast_period: int = 50
    sma_slow_period: int = 200

    # SMA(50) 斜率確認回看天數
    sma_slope_lookback: int = 10

    # 回測 SMA(50) 接近度：Low <= SMA(50) * (1 + proximity_pct)
    proximity_pct: float = 0.02  # 2% — FCX 高波動需要更寬的接近區間

    # 反彈確認：Close > SMA(50)（隱含在訊號邏輯中）

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FCXTrendPullbackConfig:
    return FCXTrendPullbackConfig(
        name="fcx_008_trend_pullback",
        experiment_id="FCX-008",
        display_name="FCX Trend Pullback to SMA(50)",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,  # +8%（同 FCX-004 突破策略）
        stop_loss=-0.07,  # -7%（同 FCX-004，突破/趨勢策略 SL 較緊）
        holding_days=20,  # 20 天持倉
    )
