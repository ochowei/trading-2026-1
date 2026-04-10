"""
SOXL-011: SOXX-Based Strategies for SOXL

三次嘗試均未超越 SOXL-006 基線（min(A,B) 0.47）：
- Att1: SOXX ATR(5)/ATR(20) > 1.05 + SOXL-006 均值回歸 → Part A 0.34/Part B 0.79
  ATR 過濾移除 3 個 Part A 訊號（2 好/1 壞），min(A,B) 0.34
- Att2: SOXX ATR(5)/ATR(20) > 1.1 + SOXL-006 均值回歸 → Part A 0.34/Part B 0.79
  結果與 Att1 完全相同，ATR 門檻在 1.05-1.1 之間無梯度區分力
- Att3: SOXX SMA(20)>SMA(50) 黃金交叉 + SOXL 5日回檔 10-20% + SOXX RSI(14)<45
  Part A 0.42/Part B 0.11，嚴重 A/B 失衡（趨勢跟蹤的結構性問題）

教訓：SOXX ATR 過濾對底層指數（~2-2.5% 日波動）仍在 ATR 有效邊界外，
趨勢跟蹤回檔在半導體板塊有嚴重的市場制域依賴問題。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXLSoxxAtrConfig(ExperimentConfig):
    """SOXL SOXX ATR-Adaptive 策略專屬參數"""

    # 訊號指標參數（同 SOXL-006）
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25
    drawdown_cap: float = -0.40
    rsi_period: int = 5
    rsi_threshold: float = 20.0
    drop_2d_threshold: float = -0.08

    # SOXX ATR 波動率過濾
    soxx_ticker: str = "SOXX"
    atr_fast_period: int = 5
    atr_slow_period: int = 20
    atr_ratio_threshold: float = 1.1

    # 冷卻期
    cooldown_days: int = 7

    # 成交模型
    slippage_pct: float = 0.001


def create_default_config() -> SOXLSoxxAtrConfig:
    """建立預設 SOXL-011 Att2 配置（最佳嘗試）"""
    return SOXLSoxxAtrConfig(
        name="soxl_011_soxx_atr_adaptive",
        experiment_id="SOXL-011",
        display_name="SOXL SOXX ATR-Adaptive Mean Reversion",
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
