"""
COPX-002: 20日回檔 + Williams %R + 延長持倉 均值回歸配置
(COPX 20-Day Pullback + Williams %R + Extended Holding Config)

相比 COPX-001（10日回檔 9-18%）：
- 20日回看窗口（更深的確認回檔，過濾短期震盪噪音）
- 回檔 ≥ 10%（對應更高的 20 日參考高點）
- 上限 ≤ 20%（稍微放寬以適應更寬的回看窗口）
- 持倉 20 天（vs 15 天，給予更充裕的反彈時間）
- 冷卻 12 天（介於 COPX-001 的 10 天和 FCX-001 的 15 天）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPXDeepDrawdownConfig(ExperimentConfig):
    """COPX 20日回檔 + Williams %R 延長持倉參數"""

    # 進場指標
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 12


def create_default_config() -> COPXDeepDrawdownConfig:
    return COPXDeepDrawdownConfig(
        name="copx_002_deep_drawdown",
        experiment_id="COPX-002",
        display_name="COPX 20-Day Pullback + Williams %R + Extended Holding",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 COPX-001，已證明的 TP 上限）
        stop_loss=-0.050,  # -5.0%（同 COPX-001）
        holding_days=20,  # 20 天（延長 5 天）
    )
