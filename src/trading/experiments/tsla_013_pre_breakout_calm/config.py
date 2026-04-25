"""
TSLA-013: Pre-Breakout Calm Filter on BB Squeeze Breakout
TSLA-013: BB 擠壓突破 + 突破前平靜度過濾

Base: TSLA-009 Att2（當前最佳，min(A,B)=0.40）
    - BB(20,2.0) + 60日 30th 百分位擠壓 + Close > Upper BB + Close > SMA(50)
    - cd10, TP+8%/SL-7%/20d

新方向：突破前平靜度過濾（Pre-Breakout Calm）
    Att1 基線：T-1 日報酬 ∈ [-3%, +4%]
        - 上限排除過熱延續性突破（2021 bubble 晚期特徵）
        - 下限排除熊市 V 型反彈突破（2022 bear 特徵）
    Att2：移除下限（設為 -20% 實質非綁定），驗證下限是否在 BB Squeeze 框架下
        結構性互斥（BB Squeeze 要求近期低波動，T-1 < -3% 應從不出現）
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
    # Att2: 僅保留上限（排除過熱延續性），下限放寬至 -20% 實質非綁定
    prev_day_return_max: float = 0.04  # T-1 日報酬上限（排除過熱延續性突破）
    prev_day_return_min: float = -0.20  # 實質無下限（驗證下限結構性非綁定）


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
