"""
FCX 優化出場均值回歸策略配置
FCX Optimized Exit Mean Reversion Configuration

基於 FCX-001 的三重極端超賣進場，加入反轉K線過濾：
- 新增 close position ≥ 40% 條件（過濾仍在下跌的訊號）
- SL/TP/Holding 維持 FCX-001 原始參數（+10%/-12%/25天）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXOptimizedExitConfig(ExperimentConfig):
    """FCX 優化出場策略專屬參數"""

    # 回撤條件：收盤價低於 N 日高點的幅度
    drawdown_lookback: int = 60
    drawdown_threshold: float = -0.18  # 低於 60 日高點 18%

    # RSI 條件
    rsi_period: int = 10
    rsi_threshold: float = 28.0  # RSI(10) < 28

    # SMA 乖離條件
    sma_period: int = 50
    sma_deviation_threshold: float = -0.08  # 收盤價低於 SMA50 超過 8%

    # 反轉K線過濾
    close_position_threshold: float = 0.40  # 收盤位置 ≥ 40%（過濾仍在下跌的訊號）

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> FCXOptimizedExitConfig:
    """建立預設配置"""
    return FCXOptimizedExitConfig(
        name="fcx_003_optimized_exit",
        experiment_id="FCX-003",
        display_name="FCX Optimized Exit Mean Reversion",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.10,  # +10% 獲利目標（維持不變）
        stop_loss=-0.12,  # -12% 停損（維持原始）
        holding_days=25,  # 25 天持倉（維持原始）
    )
