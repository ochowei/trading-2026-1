"""
SOXL-008: Williams %R(10) 振盪器測試
SOXL Williams %R(10) Oscillator Test

基於 SOXL-006 框架，以 Williams %R(10) 取代 RSI(5) 作為超賣振盪器，
測試跨資產成功的 WR 指標在 3x 槓桿 ETF 上的適用性。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLWROscillatorConfig(ExperimentConfig):
    """SOXL Williams %R 振盪器策略專屬參數"""

    # 回撤參數（同 SOXL-006）
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25
    drawdown_cap: float = -0.40

    # Williams %R 參數（取代 RSI(5)）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 2日跌幅（同 SOXL-006）
    drop_2d_threshold: float = -0.08

    # 冷卻期（同 SOXL-006）
    cooldown_days: int = 7

    # 成交模型參數
    slippage_pct: float = 0.001


def create_default_config() -> SOXLWROscillatorConfig:
    """建立預設 SOXL-008 配置"""
    return SOXLWROscillatorConfig(
        name="soxl_008_wr_oscillator",
        experiment_id="SOXL-008",
        display_name="SOXL Williams %R(10) 振盪器測試 — WR Oscillator Test",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,
        stop_loss=-0.12,
        holding_days=25,
    )
