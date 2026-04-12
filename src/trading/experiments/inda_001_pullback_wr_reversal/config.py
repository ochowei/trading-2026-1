"""
INDA 回檔 + Williams %R + 反轉K線確認配置
(INDA Pullback + Williams %R + Reversal Candle Confirmation Config)

基於 GLD-007 模板，INDA 日波動約 0.97%（略低於 GLD 1.12%，比值 0.87x），
出場參數按波動度比例略微縮放：TP +3.0%、SL -3.5%，追蹤停損啟動 +2.5%/距離 1.3%。
進場條件維持與 GLD-007 相同（低波動資產適用）。

Based on GLD-007 template. INDA daily vol ~0.97% (0.87x GLD),
exit parameters scaled slightly: TP +3.0%, SL -3.5%, trail activation +2.5%/distance 1.3%.
Entry conditions kept same as GLD-007 (suitable for low-vol assets).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDAPullbackWRReversalConfig(ExperimentConfig):
    """INDA 回檔 + Williams %R + 反轉K線確認參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 ≥3% 觸發
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 7

    # 收盤位置過濾
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4

    # 追蹤停損（按 0.87x 波動度比例縮放）
    trail_activation_pct: float = 0.025  # 獲利 +2.5% 啟動（≥TP×80%）
    trail_distance_pct: float = 0.013  # 追蹤距離 1.3%


def create_default_config() -> INDAPullbackWRReversalConfig:
    return INDAPullbackWRReversalConfig(
        name="inda_001_pullback_wr_reversal",
        experiment_id="INDA-001",
        display_name="INDA Pullback + Williams %R + Reversal Candle",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.03,  # +3.0%（按 0.87x 波動度比例從 3.5% 縮放）
        stop_loss=-0.035,  # -3.5%（按 0.87x 波動度比例從 -4.0% 縮放）
        holding_days=20,  # 20 天
    )
