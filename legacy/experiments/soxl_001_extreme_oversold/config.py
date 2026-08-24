"""
SOXL 極端超賣均值回歸策略配置
SOXL Extreme Oversold Mean Reversion Configuration

以 TQQQ-010 為模板，按 SOXL 波動度（日均 ~6.6%，TQQQ 的 1.6 倍）縮放參數。
Based on TQQQ-010 template, parameters scaled for SOXL volatility (~6.6% daily, 1.6x TQQQ).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLExtremeOversoldConfig(ExperimentConfig):
    """SOXL 極端超賣策略專屬參數"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20  # 回撤計算的高點回望天數
    drawdown_threshold: float = -0.20  # 從 20 日高點回撤 ≥ 20%（TQQQ -15% × ~1.3）
    rsi_period: int = 5  # 短週期 RSI 捕捉急性恐慌
    rsi_threshold: float = 25.0  # RSI(5) < 25 極端超賣
    volume_multiplier: float = 1.5  # 成交量 > 1.5 倍均量
    volume_sma_period: int = 20  # 均量計算週期

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 5  # 同一波跌勢中僅取第一個訊號

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001  # 0.1%（ETF 流動性佳）


def create_default_config() -> SOXLExtremeOversoldConfig:
    """建立預設 SOXL 配置 (Create default SOXL config)"""
    return SOXLExtremeOversoldConfig(
        name="soxl_001_extreme_oversold",
        experiment_id="SOXL-001",
        display_name="SOXL 極端超賣 + 成交模型 — Extreme Oversold + Execution Model",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.10,  # +10%（TQQQ +7% × ~1.4，半導體反彈力道更強）
        stop_loss=-0.12,  # -12%（TQQQ -8% × ~1.5，適配更高波動）
        holding_days=10,  # 10 天（高波動 = 快速回歸）
    )
