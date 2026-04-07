"""
NVDA-008: RS Parameter Exploration 配置
NVDA Relative Strength Parameter Exploration Configuration

基於 NVDA-006（RS Momentum Pullback，min(A,B) 0.47）成功，
探索尚未嘗試的 RS 參數維度：

- NVDA-006 已驗證：20日 RS ≥5%（最佳），RS ≥7%（過嚴），pullback 4-8%（過濾好訊號）
- 本實驗探索：不同 RS 回看窗口（10日/40日）和不同基準（SPY vs SMH）

三次嘗試結果（全部未超越 NVDA-004/006 的 min(A,B) 0.47）：
- Att1: SMH 10日 RS≥3% + 3日回撤 2-6% → Part A 0.48/Part B 0.17, min 0.17（短窗口太噪）
- Att2: SMH 40日 RS≥8% + 5日回撤 3-8% → Part A 0.57/Part B 0.03, min 0.03（長窗口嚴重過擬合）
- Att3: SPY 20日 RS≥8% + 5日回撤 3-8% → Part A 0.46/Part B 0.57, min 0.46（最接近但未超越）

結論：20日 RS 回看是甜蜜點（10日太噪、40日過擬合），SMH 仍是最佳基準（SPY 略差）。
出場參數固定為已驗證最優：TP+8%/SL-7%/20天/冷卻10天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDARSParamExploreConfig(ExperimentConfig):
    """NVDA RS Parameter Exploration 策略專屬參數"""

    reference_ticker: str = "SPY"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.08
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.08
    cooldown_days: int = 10


def create_default_config() -> NVDARSParamExploreConfig:
    return NVDARSParamExploreConfig(
        name="nvda_008_rs_param_explore",
        experiment_id="NVDA-008",
        display_name="NVDA RS Parameter Exploration",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
