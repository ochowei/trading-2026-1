"""
SOXL BB 擠壓突破策略配置
SOXL BB Squeeze Breakout Configuration

首次在 SOXL 上嘗試突破策略（此前 8 個實驗均為均值回歸）。
靈感來自 TSLA-005 的 BB 擠壓突破成功（Sharpe +150-185%），
針對 SOXL 3x 槓桿的高波動特性調整參數。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLBBSqueezeConfig(ExperimentConfig):
    """SOXL BB 擠壓突破策略專屬參數"""

    # Bollinger Band 參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 擠壓偵測參數
    bb_squeeze_percentile_window: int = 60  # 回看天數
    bb_squeeze_percentile: float = 0.25  # BB Width 在 60 日的 25th 百分位
    bb_squeeze_recent_days: int = 5  # 5 日內曾發生擠壓即可

    # 趨勢確認（突破策略適用，均值回歸禁用）
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 15

    # 成交模型參數
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXLBBSqueezeConfig:
    """建立預設 SOXL-009 配置"""
    return SOXLBBSqueezeConfig(
        name="soxl_009_bb_squeeze_breakout",
        experiment_id="SOXL-009",
        display_name="SOXL BB 擠壓突破 — BB Squeeze Breakout",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.15,  # +15%（TSLA +10% 按 ~1.5x 波動倍率縮放）
        stop_loss=-0.10,  # -10%（TSLA -7% 按波動倍率縮放）
        holding_days=20,
    )
