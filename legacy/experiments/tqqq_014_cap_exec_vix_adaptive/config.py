"""
TQQQ VIX 自適應出場 + 成交模型配置 (TQQQ VIX-Adaptive Exit + Execution Model Configuration)
保持基線三條件進場，根據訊號日 VIX 水準動態調整 TP/SL/持倉天數。
Baseline 3-condition entry, dynamically adjust TP/SL/holding based on VIX at signal time.
"""

from dataclasses import dataclass, field

from trading.experiments.tqqq_001_capitulation.config import TQQQConfig


@dataclass
class VIXTier:
    """VIX 區間對應的出場參數"""

    vix_min: float
    vix_max: float
    profit_target: float
    stop_loss: float
    holding_days: int
    label: str


@dataclass
class TQQQVixAdaptiveConfig(TQQQConfig):
    """TQQQ VIX 自適應出場 + 成交模型配置"""

    # VIX 資料來源
    vix_ticker: str = "^VIX"

    # 成交模型參數
    slippage_pct: float = 0.001  # 0.1%

    # VIX 分層出場參數（訊號日 VIX 決定出場條件）
    # 預設使用 TQQQ-010 的 TP +7%/SL -8%/10d 作為中間層
    vix_tiers: list[VIXTier] = field(
        default_factory=lambda: [
            VIXTier(
                vix_min=35.0,
                vix_max=999.0,
                profit_target=0.09,
                stop_loss=-0.10,
                holding_days=12,
                label="extreme_fear",
            ),
            VIXTier(
                vix_min=0.0,
                vix_max=35.0,
                profit_target=0.07,
                stop_loss=-0.08,
                holding_days=10,
                label="baseline",
            ),
        ]
    )


def create_default_config() -> TQQQVixAdaptiveConfig:
    """建立預設配置"""
    return TQQQVixAdaptiveConfig(
        name="tqqq_014_cap_exec_vix_adaptive",
        experiment_id="TQQQ-014",
        display_name="TQQQ VIX 自適應出場 + 成交模型 — VIX-Adaptive Exit + Execution Model",
        tickers=["TQQQ"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        # 基線出場參數作為 fallback（VIX 資料不可用時）
        profit_target=0.07,
        stop_loss=-0.08,
        holding_days=10,
    )
