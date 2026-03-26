"""
GLD 優化出場均值回歸配置 (GLD Optimized Exit Mean Reversion Configuration)
進場條件不變，僅優化出場參數（TP +2.5%、SL -4%、持倉 15 天）。
Entry conditions unchanged, exit parameters optimized (TP +2.5%, SL -4%, hold 15d).
"""

from dataclasses import dataclass

from trading.experiments.gld_001_mean_reversion.config import GLDMeanReversionConfig


@dataclass
class GLDOptimizedExitConfig(GLDMeanReversionConfig):
    """GLD 優化出場配置 — 繼承 GLD-001 進場參數，覆寫出場參數"""

    pass


def create_default_config() -> GLDOptimizedExitConfig:
    return GLDOptimizedExitConfig(
        name="gld_002_optimized_exit",
        experiment_id="GLD-002",
        display_name="GLD Optimized Exit Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5% (GLD-001: +1.5%)
        stop_loss=-0.04,  # -4.0% (GLD-001: -3.0%)
        holding_days=15,  # 15 天 (GLD-001: 10)
    )
