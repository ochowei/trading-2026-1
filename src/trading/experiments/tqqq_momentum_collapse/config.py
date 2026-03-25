"""
TQQQ 多日動能崩潰策略配置 (TQQQ Multi-Day Momentum Collapse Configuration)
捕捉連續賣壓 + 累計跌幅較大的底部型態。
Captures bottoming patterns with sustained selling pressure and large cumulative drops.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQMomentumCollapseConfig(ExperimentConfig):
    """TQQQ 多日動能崩潰策略配置"""

    # 多日動能崩潰參數 (Multi-day collapse parameters)
    lookback_days: int = 5                  # 回看區間天數
    min_down_days: int = 4                  # 至少 N 天下跌
    cumulative_drop_threshold: float = -0.12  # N 日累計跌幅需 <= -12%

    # 趨勢過濾 (Trend filter)
    trend_sma_period: int = 50              # 價格需低於 SMA50

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 5                  # 避免同波段重複進場


def create_default_config() -> TQQQMomentumCollapseConfig:
    """建立預設多日動能崩潰配置 (Create default config)"""
    return TQQQMomentumCollapseConfig(
        name="tqqq_momentum_collapse",
        experiment_id="TQQQ-006",
        display_name="TQQQ 多日動能崩潰策略 — Multi-Day Momentum Collapse",
        tags=["tqqq", "momentum", "collapse"],
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
    )
