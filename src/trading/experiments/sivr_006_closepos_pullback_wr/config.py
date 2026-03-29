"""
SIVR 非對稱出場 + 回檔範圍 + Williams %R 均值回歸配置
(SIVR Asymmetric Exit + Capped Pullback + Williams %R Mean Reversion Config)

基於 SIVR-005，調整出場策略為非對稱出場：
- 放寬止盈至 +4.5%（利用 SIVR 2-4% 日波動捕捉更大上行空間）
- 維持停損 -3.5%（已驗證有效）
- 延長持倉至 20 天（給更大止盈更多達標時間）
盈虧比從 1.0 提升至 1.29，搭配 >60% 勝率可望改善風險調整報酬。

Based on SIVR-005, uses asymmetric exit:
- Wider TP +4.5% (captures more upside in SIVR's 2-4% daily vol)
- Keep SL -3.5% (proven effective)
- Extended hold 20d (more time for wider TP to hit)
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRClosePosConfig(ExperimentConfig):
    """SIVR 非對稱出場 + 回檔範圍 + Williams %R 參數"""

    # 進場指標（同 SIVR-005）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    pullback_cap: float = -0.15  # 回檔 ≤15%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> SIVRClosePosConfig:
    return SIVRClosePosConfig(
        name="sivr_006_closepos_pullback_wr",
        experiment_id="SIVR-006",
        display_name="SIVR Asymmetric Exit + Capped Pullback + Williams %R Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（適度放寬止盈）
        stop_loss=-0.035,  # -3.5%（維持）
        holding_days=20,  # 20 天（延長）
    )
