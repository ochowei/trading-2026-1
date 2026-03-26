"""
TQQQ 放寬進場策略配置 (TQQQ Relaxed Entry Strategy Configuration)
放寬進場門檻並收緊停損，以增加訊號數量同時控制風險。
Relaxes entry thresholds and tightens stop-loss to increase signal frequency while managing risk.
"""

from dataclasses import dataclass

from trading.experiments.tqqq_001_capitulation.config import TQQQConfig


@dataclass
class TQQQCapRelaxedConfig(TQQQConfig):
    """TQQQ 放寬進場策略配置"""

    # 放寬的進場閾值 (Relaxed entry thresholds)
    drawdown_threshold: float = -0.12  # -15% -> -12%
    rsi_threshold: float = 30.0  # 25 -> 30
    volume_multiplier: float = 1.3  # 1.5x -> 1.3x

    # 收緊的停損 (Tighter stop-loss)
    stop_loss: float = -0.06  # -8% -> -6%

    # 增加冷卻期（防止放寬後過度交易）
    cooldown_days: int = 5  # 3 -> 5


def create_default_config() -> TQQQCapRelaxedConfig:
    """建立預設放寬進場配置 (Create default relaxed entry config)"""
    return TQQQCapRelaxedConfig(
        name="tqqq_002_cap_relaxed_entry",
        experiment_id="TQQQ-002",
        display_name="TQQQ 放寬進場策略 — Relaxed Entry Strategy",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,
        holding_days=7,
    )
