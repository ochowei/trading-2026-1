"""
EWT 回檔 + Williams %R + 反轉K線確認配置
(EWT Pullback + Williams %R + Reversal Candle Confirmation Config)

以 GLD-007 為模板，根據 EWT 日波動度 1.41%（GLD 的 1.26 倍）縮放參數。
回檔門檻加深至 4%，TP/SL 放寬，持倉縮短至 18 天。
追蹤停損適用（日波動 ≤ 1.5%），啟動門檻與距離按波動度上調。

Based on GLD-007 template, scaled for EWT daily volatility 1.41% (1.26x GLD).
Deeper pullback threshold (4%), wider TP/SL, shorter holding (18 days).
Trailing stop enabled (daily vol <= 1.5%), activation and distance scaled up.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWTPullbackWRReversalConfig(ExperimentConfig):
    """EWT 回檔 + Williams %R + 反轉K線確認參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.04  # 回檔 ≥4% 觸發（GLD -3% × 1.26 vol ratio）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 8  # 冷卻 8 天（GLD 7 × 1.14）

    # 收盤位置過濾
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) ≥ 0.4

    # 追蹤停損
    trail_activation_pct: float = 0.025  # 獲利 +2.5% 啟動（GLD 2% scaled）
    trail_distance_pct: float = 0.02  # 追蹤距離 2.0%（GLD 1.5% scaled）


def create_default_config() -> EWTPullbackWRReversalConfig:
    return EWTPullbackWRReversalConfig(
        name="ewt_001_pullback_wr_reversal",
        experiment_id="EWT-001",
        display_name="EWT Pullback + Williams %R + Reversal Candle",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.045,  # +4.5%（GLD 3.5% × ~1.3）
        stop_loss=-0.05,  # -5.0%（GLD -4% × 1.25）
        holding_days=18,  # 18 天（GLD 20 × 0.9）
    )
