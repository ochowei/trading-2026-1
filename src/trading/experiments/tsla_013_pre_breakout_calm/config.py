"""
TSLA-013: Pre-Breakout Calm Filter on BB Squeeze Breakout
TSLA-013: BB 擠壓突破 + 突破前平靜度過濾

Base: TSLA-009 Att2（當前最佳，min(A,B)=0.40）
    - BB(20,2.0) + 60日 30th 百分位擠壓 + Close > Upper BB + Close > SMA(50)
    - cd10, TP+8%/SL-7%/20d

新方向：突破前平靜度過濾（Pre-Breakout Calm）
    Att1 基線：T-1 日報酬 ∈ [-3%, +4%]
    Att2：上限唯一（下限非綁定）
    Att3：放棄 T-1 報酬過濾，改用 SMA(50) 延伸度上限 Close/SMA(50) ≤ 1.15
        位置型過濾器，直接針對「price 已遠離 SMA 的過熱延續性突破」特徵
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLAPreBreakoutCalmConfig(ExperimentConfig):
    """TSLA BB Squeeze Breakout + Pre-Breakout Calm Filter"""

    # === BB Squeeze Breakout 基礎（同 TSLA-009 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 突破前平靜度過濾（Pre-Breakout Calm Filter）===
    # 僅檢查訊號日前一日（T-1）的單日報酬
    # Att3: 放寬 T-1 上限至 +10% 實質停用，改用 SMA 延伸度過濾器
    prev_day_return_max: float = 0.10  # 實質無上限
    prev_day_return_min: float = -0.20  # 實質無下限

    # === SMA 延伸度上限（Att3 新增）===
    # 排除「已遠離 SMA(50) 的晚期延伸突破」（2021 bubble late-cycle 特徵）
    # Close / SMA(50) 若超過此倍率則跳過訊號
    sma_extension_max: float = 1.15


def create_default_config() -> TSLAPreBreakoutCalmConfig:
    """建立預設配置（Att1 基線）"""
    return TSLAPreBreakoutCalmConfig(
        name="tsla_013_pre_breakout_calm",
        experiment_id="TSLA-013",
        display_name="TSLA Pre-Breakout Calm Filter",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
