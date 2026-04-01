"""
SOXL 精選超賣 + 延長持倉策略配置
SOXL Selective Oversold + Extended Holding Configuration

基於 SOXL-005，收緊 RSI(5) 門檻至 <20（提升訊號品質），
並延長持倉至 25 天（給予慢速反彈更多時間達標）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLSelectiveOversoldConfig(ExperimentConfig):
    """SOXL 精選超賣策略專屬參數"""

    # 訊號指標參數 (Signal indicator parameters)
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25  # -25% 下限
    drawdown_cap: float = -0.40  # -40% 上限（過濾極端崩盤）
    rsi_period: int = 5
    rsi_threshold: float = 20.0  # 收緊：25 → 20
    drop_2d_threshold: float = -0.08  # 2日跌幅 ≤ -8%

    # 訊號冷卻 (Signal cooldown)
    cooldown_days: int = 7

    # 成交模型參數 (Execution model parameters)
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXLSelectiveOversoldConfig:
    """建立預設 SOXL-006 配置"""
    return SOXLSelectiveOversoldConfig(
        name="soxl_006_selective_oversold",
        experiment_id="SOXL-006",
        display_name="SOXL 精選超賣 + 延長持倉 — Selective Oversold + Extended Holding",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,  # +18%（SOXL 甜蜜點）
        stop_loss=-0.12,  # -12%
        holding_days=25,  # 延長：20 → 25 天
    )
