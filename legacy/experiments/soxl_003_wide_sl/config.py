"""
SOXL 高盈虧比均值回歸策略配置
SOXL High Reward-Risk Mean Reversion Configuration

基於 SOXL-002，提高 TP（+18%）並延長持倉（20天），
改善盈虧比至 1.5:1（平衡點勝率 40%）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLWideSLConfig(ExperimentConfig):
    """SOXL 寬停損策略專屬參數"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25  # -25%（同 SOXL-002）
    rsi_period: int = 5
    rsi_threshold: float = 25.0
    volume_multiplier: float = 1.5
    volume_sma_period: int = 20

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 7

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXLWideSLConfig:
    """建立預設 SOXL-003 配置"""
    return SOXLWideSLConfig(
        name="soxl_003_wide_sl",
        experiment_id="SOXL-003",
        display_name="SOXL 寬停損 + 成交模型 — Wide SL + Execution Model",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,  # +18%（vs +15%，盈虧比 1.5:1，平衡點勝率 40%）
        stop_loss=-0.12,  # -12%（同 SOXL-002，維持不變）
        holding_days=20,  # 20 天（vs 15 天，更充分的反彈時間）
    )
