"""
TQQQ 多日動能崩潰策略配置 (TQQQ Multi-Day Momentum Collapse Strategy Configuration)
定義 TQQQ-006 專屬策略的所有參數與閾值。
Defines all parameters and thresholds for the TQQQ multi-day momentum collapse strategy.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQMomentumCollapseConfig(ExperimentConfig):
    """TQQQ 多日動能崩潰策略配置"""

    # 訊號指標參數 (Signal indicator parameters)
    lookback_period: int = 5                # 觀察天數 (5天)
    negative_days_threshold: int = 4        # 過去 N 天中下跌的天數門檻 (≥ 4天)
    cumulative_drop_threshold: float = -0.12 # N 日累計報酬門檻 (≤ -12%)
    sma_period: int = 50                    # 趨勢確認的 SMA 週期 (收盤價 < 50MA)

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 5             # 避免同一波下跌重複進場


def create_default_config() -> TQQQMomentumCollapseConfig:
    """建立預設配置 (Create default config)"""
    return TQQQMomentumCollapseConfig(
        name="tqqq_momentum_collapse",
        experiment_id="TQQQ-006",
        display_name="TQQQ 多日動能崩潰策略 — Multi-Day Momentum Collapse",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,
        stop_loss=-0.10,
        holding_days=10,
        cooldown_days=5,
    )
