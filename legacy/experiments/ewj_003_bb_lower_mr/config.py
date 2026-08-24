"""
EWJ-003: BB Lower Band Mean Reversion

CIBR-007 驗證 BB 下軌在 1.53% vol 資產上優於固定回檔門檻（+17%）。
EWJ 日波動 1.15% 更低，BB(20,2.0) 下軌應提供更精準的自適應進場門檻：
低波動期淺門檻捕捉更多有效訊號，高波動期深門檻自動隔離極端崩盤。

保留 EWJ-002 驗證有效的品質過濾器：WR(10)<=80 + ClosePos>=40% + ATR>1.15。
出場參數同 EWJ-002（TP+3.5%/SL-4.0%/20天），先測試進場差異。

Att1: BB(20,2.0) 下軌 + WR + ClosePos + ATR > 1.15 + cooldown 7
      → Part A 0.70/Part B 0.49, min 0.49。Part A 優秀但 Part B 僅 4 訊號（75% WR）。
Att2: BB(20,1.5) 較寬下軌，增加訊號數。
      → Part A 0.26/Part B 1.01, min 0.26。Part B 優秀（8訊號 87.5%WR）但 Part A
      品質稀釋（3 筆新停損：COVID 前+2022 QT+2023 夏季）。
Att3: BB(20,1.5) + 10日高點回檔上限 7%（混合進場）。保留 Att2 的寬 BB 訊號捕捉
      同時用 7% pullback cap 隔離極端崩盤（COVID -24%, 日本利差交易 -16% 等）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWJ003Config(ExperimentConfig):
    """EWJ-003 BB 下軌均值回歸參數"""

    # BB 參數
    bb_period: int = 20
    bb_std: float = 1.5

    # 崩盤隔離（10日高點回檔上限，過濾 COVID 等極端事件）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07  # 回檔上限 7%（~6σ for 1.15% vol）

    # 品質過濾（同 EWJ-002 驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    cooldown_days: int = 7


def create_default_config() -> EWJ003Config:
    return EWJ003Config(
        name="ewj_003_bb_lower_mr",
        experiment_id="EWJ-003",
        display_name="EWJ BB Lower Band Mean Reversion",
        tickers=["EWJ"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
