"""
URA-001: 回檔 + Williams %R 均值回歸配置
(URA Pullback + Williams %R Mean Reversion Config)

URA (Global X Uranium ETF) 日波動度 ~2.34%，與 GLD 比率 2.11x。
參考 XBI-001 / COPX-001 回檔範圍 + Williams %R 架構，按 URA 波動度縮放參數：
- 回檔範圍：10-20%（過濾淺回檔與極端崩盤）
- WR(10) ≤ -80（標準超賣門檻）
- TP +6.0%（URA 高波動支撐較大均值回歸幅度）
- SL -6.0%（對稱出場，20天持倉）
- 不使用追蹤停損（日波動 2.34% 禁用區域）

Adapts XBI-001/COPX-001 pullback range + Williams %R approach for URA.
No trailing stop (daily vol ~2.34% is in the no-trailing zone).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URAPullbackWRConfig(ExperimentConfig):
    """URA 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> URAPullbackWRConfig:
    return URAPullbackWRConfig(
        name="ura_001_pullback_wr",
        experiment_id="URA-001",
        display_name="URA Pullback + Williams %R Mean Reversion",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,  # +6.0%
        stop_loss=-0.060,  # -6.0%（對稱出場）
        holding_days=20,  # 20 天
    )
