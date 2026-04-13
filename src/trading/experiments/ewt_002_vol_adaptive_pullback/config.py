"""
EWT-002: Volatility-Adaptive Pullback + WR Mean Reversion
(EWT 波動率自適應回檔均值回歸)

EWT-001 追蹤停損啟動/TP 比 = 55.6%（遠低於 80% 安全門檻），壓縮獲利導致 Part A
Sharpe 僅 0.10。本實驗移除追蹤停損，改用固定 TP/SL + ATR 波動率飆升過濾。

以 VGK-002 框架為基礎，按 EWT 日波動 1.41%（VGK 1.12% 的 1.26 倍）縮放參數。
增加回檔上限 -10%（約 7 sigma）隔離極端崩盤訊號。

Att1（最佳）: ATR > 1.15（VGK 甜蜜點）→ Part A 0.13 / Part B 0.64, min 0.13 ★
Att2: ATR > 1.1（IWM 甜蜜點）→ Part A 0.08 / Part B 0.37, min 0.08
  → 1.1 太鬆，讓入 2021-07/09 慢磨信號，品質下降
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT002Config(ExperimentConfig):
    """EWT-002 波動率自適應回檔均值回歸參數"""

    # 回檔參數（VGK-002 × 1.26 vol ratio）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.04  # 10日高點回檔 >= 4%
    pullback_cap: float = -0.10  # 回檔上限 -10%（隔離極端崩盤）

    # Williams %R 參數
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期
    cooldown_days: int = 8


def create_default_config() -> EWT002Config:
    return EWT002Config(
        name="ewt_002_vol_adaptive_pullback",
        experiment_id="EWT-002",
        display_name="EWT Volatility-Adaptive Pullback MR",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.045,  # +4.5%（VGK 3.5% × ~1.3）
        stop_loss=-0.050,  # -5.0%（VGK -4.0% × 1.25）
        holding_days=18,  # 18天（VGK 20 × 0.9，較高波動=較快回歸）
    )
