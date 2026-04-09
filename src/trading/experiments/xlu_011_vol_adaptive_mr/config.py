"""
XLU-011: Volatility-Adaptive Mean Reversion
(XLU 波動率自適應均值回歸)

基於 XLU-010 的 ATR 波動率飆升過濾發現：
- ATR(5)/ATR(20) > 1.2 完美過濾（100% WR Part A）但僅 8 訊號
- ATR > 1.1 增加訊號至 14 但重新引入 3 個停損
- 本實驗探索未測試的中間值，在品質和數量間取得平衡

Att1（最終選擇）: ATR > 1.15 → Part A Sharpe 0.67 / Part B 1.56，min(A,B) 0.67
  比 XLU-010 Att2 多 2 個 Part A + 1 個 Part B 好訊號（11 vs 8）
Att2: ATR > 1.12 → Part B 引入 2025-10-22 壞訊號，Sharpe 0.38，嚴格劣化
Att3: 回檔上限 8%（vs 7%）→ 與 Att1 完全相同，無 7-8% 範圍的額外訊號
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLUVolAdaptiveMRConfig(ExperimentConfig):
    """XLU 波動率自適應均值回歸參數"""

    # 回檔參數（同 XLU-003）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035  # 回檔 >= 3.5%
    pullback_cap: float = -0.07  # 回檔 <= 7%（8% 結果相同，保持一致）

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉K線確認）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15  # 甜蜜點（1.12 引入 Part B 壞訊號，1.2 太嚴）

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> XLUVolAdaptiveMRConfig:
    return XLUVolAdaptiveMRConfig(
        name="xlu_011_vol_adaptive_mr",
        experiment_id="XLU-011",
        display_name="XLU Volatility-Adaptive Mean Reversion",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（XLU 均值回歸甜蜜點）
        stop_loss=-0.040,  # -4.0%（XLU 全域甜蜜點）
        holding_days=20,
    )
