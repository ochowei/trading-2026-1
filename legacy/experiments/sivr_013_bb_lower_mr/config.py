"""
SIVR-013: Bollinger Band 下軌均值回歸配置
(SIVR BB Lower Band Mean Reversion Config)

替代 SIVR-005 的固定 7% 回檔門檻，改用 BB(20,2) 下軌作為自適應進場門檻。
BB 下軌會隨波動度自動調整：高波動時門檻更寬（避免過早進場），
低波動時門檻更窄（捕捉溫和回檔）。

進場條件：
1. Close < BB(20, bb_std) 下軌（自適應超賣）
2. WR(10) <= -80（超賣確認）
3. 回檔上限 15%（過濾極端崩盤，同 SIVR-005）
4. 冷卻 10-12 天

Att1: BB(20,2.0), TP +3.5% / SL -3.5% / 15d → Part A Sharpe 0.01 / Part B 0.55
  BB(20,2.0) 在 2021-2022 熊市產生過多假訊號（9 連停損），SL -3.5% 太緊

Att2: BB(20,2.5), TP +3.5% / SL -4.5% / 20d / cd12 → Part A Sharpe -0.02 / Part B 0.00
  BB(20,2.5) 過嚴，Part B 僅 1 訊號無法評估，Part A WR 仍 50%

Att3: BB(20,2.0) + ATR(5)/ATR(20) > 1.05, TP +3.5% / SL -3.5% / 15d / cd10
  → Part A Sharpe -0.19 / Part B -0.02
  ATR 過濾反而惡化，SIVR 日波動 2-3% 使 ATR ratio 普遍偏高，無法區分好壞訊號

結論：三次嘗試均未超越 SIVR-005（min(A,B) 0.22）。BB 下軌入場在
SIVR 上不可行：熊市時 BB 持續觸及（假訊號），牛市時幾乎不觸及（訊號太少）。
確認 cross_asset_lesson #18（BB 不可替代固定回檔門檻）適用於 SIVR。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVR013Config(ExperimentConfig):
    """SIVR-013 BB 下軌均值回歸參數"""

    # BB 下軌進場
    bb_period: int = 20
    bb_std: float = 2.0  # Att3: 回到 2.0 std

    # WR 超賣確認
    wr_period: int = 10
    wr_threshold: float = -80.0

    # ATR 波動率飆升過濾（Att3 新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05  # ATR(5)/ATR(20) > 1.05

    # 回檔上限（過濾極端崩盤）
    pullback_lookback: int = 10
    pullback_cap: float = -0.15  # 回檔 <= 15%

    # 冷卻期
    cooldown_days: int = 10  # Att3: 回到 10 天


def create_default_config() -> SIVR013Config:
    return SIVR013Config(
        name="sivr_013_bb_lower_mr",
        experiment_id="SIVR-013",
        display_name="SIVR BB Lower Band Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 SIVR-005）
        stop_loss=-0.035,  # -3.5%（同 SIVR-005）
        holding_days=15,  # 15 天（同 SIVR-005）
    )
