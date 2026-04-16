"""
INDA-002: Volatility-Adaptive Mean Reversion
(INDA 波動率自適應均值回歸)

基於 INDA-001 改進：
- 新增 ATR(5)/ATR(20) > 1.15 波動率自適應過濾，選擇急跌恐慌進場
  （INDA 日波動 0.97% 與 XLU 1.0% 幾乎相同，XLU-011 用此過濾 +272%）
- 新增回檔上限 7%，隔離極端崩盤訊號（cross-asset lesson #13）
- 移除追蹤停損，使用固定 TP/SL
- 放寬出場：TP +3.5% / SL -4.0%

Att1（最終選擇）: ATR > 1.15, TP +3.5%, SL -4.0%, 20天, 無追蹤停損
  → Part A 0.19 / Part B 0.15，min(A,B) 0.15（vs INDA-001 的 0.03，+400%）
  ATR 過濾將 Part A 訊號從 36→13，移除慢磨下跌假訊號
Att2: ATR > 1.1, TP +3.0%, SL -3.5%, 20天, 追蹤停損
  → Part A -0.03 / Part B 0.13（追蹤停損壓縮獲利至 +1.1%，ATR 1.1 引入壞訊號）
Att3: ATR > 1.15, TP +3.5%, SL -3.5%, 18天, 無追蹤停損
  → Part A -0.01 / Part B 0.24（緊 SL 將 2 筆勝出交易轉為停損）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDAVolAdaptiveMRConfig(ExperimentConfig):
    """INDA 波動率自適應均值回歸參數"""

    # 進場 — 回檔
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_cap: float = -0.07  # 回檔 <= 7%（隔離極端崩盤）

    # 進場 — Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾
    close_position_threshold: float = 0.4

    # 進場 — 波動率自適應過濾
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15  # 甜蜜點（1.1 引入壞訊號）

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> INDAVolAdaptiveMRConfig:
    return INDAVolAdaptiveMRConfig(
        name="inda_002_vol_adaptive_mr",
        experiment_id="INDA-002",
        display_name="INDA Volatility-Adaptive Mean Reversion",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%（寬 SL 給波動呼吸空間）
        holding_days=20,
    )
