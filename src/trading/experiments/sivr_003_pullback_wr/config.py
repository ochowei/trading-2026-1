"""
SIVR 回檔 + Williams %R 均值回歸配置 (SIVR Pullback + Williams %R Mean Reversion Config)

參考 GLD-006 成功經驗，以「10 日高點回檔幅度」取代 RSI + SMA 乖離作為入場條件，
搭配 Williams %R 確認超賣。回檔幅度天然適應趨勢行情（參考點隨趨勢上移），
解決 SIVR-001 在 Part B (2024-2025) 僅 2 筆訊號的問題。

參數依 SIVR 波動率調整：
- 回檔門檻：7%（GLD-006 為 3%，白銀波動大需更嚴格過濾）
- 止盈/停損：+3.5% / -3.5%（風報比 1:1，利用勝率 > 60% 獲利）
- 不使用追蹤停損（SIVR-002 已驗證追蹤停損在高波動白銀上失敗）

Adapts GLD-006's pullback + Williams %R approach for SIVR with volatility-scaled params.
No trailing stop (SIVR-002 proved it fails on silver's high intraday volatility).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRPullbackWRConfig(ExperimentConfig):
    """SIVR 回檔 + Williams %R 均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> SIVRPullbackWRConfig:
    return SIVRPullbackWRConfig(
        name="sivr_003_pullback_wr",
        experiment_id="SIVR-003",
        display_name="SIVR Pullback + Williams %R Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%（收緊停損，風報比 1:1）
        holding_days=15,  # 15 天
    )
