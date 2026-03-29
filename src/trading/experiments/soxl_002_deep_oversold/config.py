"""
SOXL 深度超賣均值回歸策略配置
SOXL Deep Oversold Mean Reversion Configuration

基於 SOXL-001，加深進場門檻（-25%）、提高 TP（+15%）以改善盈虧比，
延長持倉（15天）給予更充分的反彈時間。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLDeepOversoldConfig(ExperimentConfig):
    """SOXL 深度超賣策略專屬參數"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25  # -25%（vs SOXL-001 的 -20%，更深度恐慌）
    rsi_period: int = 5
    rsi_threshold: float = 25.0
    volume_multiplier: float = 1.5
    volume_sma_period: int = 20

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 7  # 7 天（vs SOXL-001 的 5 天）

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXLDeepOversoldConfig:
    """建立預設 SOXL-002 配置"""
    return SOXLDeepOversoldConfig(
        name="soxl_002_deep_oversold",
        experiment_id="SOXL-002",
        display_name="SOXL 深度超賣 + 成交模型 — Deep Oversold + Execution Model",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.15,  # +15%（vs +10%，半導體深度恐慌反彈力道強，改善盈虧比至 1.25:1）
        stop_loss=-0.12,  # -12%（維持不變，避免收緊 SL 的悲觀認定問題）
        holding_days=15,  # 15 天（vs 10 天，更多反彈時間）
    )
