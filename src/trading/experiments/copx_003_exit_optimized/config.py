"""
COPX-003: 20日回檔 + Williams %R + 出場優化 均值回歸配置
(COPX 20-Day Pullback + Williams %R + Exit Optimization Config)

相比 COPX-002（TP +3.5% / SL -5.0%）：
- SL -4.5%（收窄 0.5%，純粹改善：WR 不變，每筆虧損降低 0.5%）
- SL -4.0% 太緊（Part B WR 從 72.7% 崩至 54.5%），-4.5% 是甜蜜點
- TP +4.0% 測試失敗（Part A 2筆達標→到期/停損，Sharpe 0.34→0.25）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPXExitOptimizedConfig(ExperimentConfig):
    """COPX 20日回檔 + Williams %R + 出場優化參數"""

    # 進場指標（同 COPX-002）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 12


def create_default_config() -> COPXExitOptimizedConfig:
    return COPXExitOptimizedConfig(
        name="copx_003_exit_optimized",
        experiment_id="COPX-003",
        display_name="COPX 20-Day Pullback + Williams %R + Exit Optimization",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 COPX-002）
        stop_loss=-0.045,  # -4.5%（vs COPX-002 -5.0%，甜蜜點）
        holding_days=20,  # 20 天（同 COPX-002）
    )
