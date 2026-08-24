"""
IBIT-004: 波動率自適應 / 2日急跌 均值回歸配置
(IBIT Volatility-Adaptive / 2-Day Drop Mean Reversion Config)

基於 IBIT-001 的回檔 + WR(10) 進場架構，測試兩種額外過濾器：
- Att1: ATR(5)/ATR(20) > 1.05 → Part A Sharpe -3.45（僅 2 訊號全敗，過濾掉所有贏家）
- Att2: ATR(5)/ATR(20) > 1.0 → Part A Sharpe -0.39（3 訊號，仍移除 2 個贏家）
- Att3: 2日跌幅 ≤ -5%（USO-013 模式，按波動度縮放）

ATR 過濾在 IBIT 失敗的原因：日波動 3.17% 超出 ATR 有效邊界（≤ 2.25%），
好的均值回歸訊號在 Bitcoin 上常發生在低/正常波動率的有序回檔期間。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBIT004Config(ExperimentConfig):
    """IBIT-004 波動率自適應 / 2日急跌均值回歸參數"""

    # 進場指標（同 IBIT-001）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.12  # 回檔 >= 12%
    pullback_upper: float = -0.22  # 回檔上限 22%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 15

    # Att3: 2日急跌過濾器
    two_day_drop_threshold: float = -0.05  # 2日跌幅 ≤ -5%


def create_default_config() -> IBIT004Config:
    return IBIT004Config(
        name="ibit_004_vol_adaptive",
        experiment_id="IBIT-004",
        display_name="IBIT Volatility-Adaptive Mean Reversion",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,  # +5.0%（同 IBIT-001）
        stop_loss=-0.07,  # -7.0%（同 IBIT-001）
        holding_days=15,  # 15 天（同 IBIT-001）
    )
