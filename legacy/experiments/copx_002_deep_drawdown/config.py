"""
COPX-002: 回檔 10-18% + Williams %R 均值回歸配置
(COPX Pullback 10-18% + Williams %R Mean Reversion Config)

基於 COPX-001 架構（8%→9% 提升 Sharpe 0.00→0.08），
進一步收緊回檔下限至 10%，測試是否延續改善趨勢：
- 回檔範圍：10-18%（比 COPX-001 的 9% 更嚴格）
- WR(10) ≤ -80（與 COPX-001 相同）
- TP +3.5% / SL -5.0% / 15 天（與 COPX-001 相同）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX002Config(ExperimentConfig):
    """COPX-002 回檔 10-18% + WR 參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%（比 COPX-001 的 9% 更嚴格）
    pullback_upper: float = -0.18  # 回檔上限 18%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80
    cooldown_days: int = 10


def create_default_config() -> COPX002Config:
    return COPX002Config(
        name="copx_002_deep_drawdown",
        experiment_id="COPX-002",
        display_name="COPX Pullback 10-18% + WR Mean Reversion",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.050,  # -5.0%
        holding_days=15,  # 15 天
    )
