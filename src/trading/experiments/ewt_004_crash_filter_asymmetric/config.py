"""
EWT-004: 2-Day Crash Filter + Asymmetric Exit Mean Reversion
(EWT 2日急跌過濾 + 非對稱出場均值回歸)

在 EWT-002 的 pullback+WR+ATR 基礎上加入 2 日急跌過濾，並調整為非對稱出場：
1. 2日報酬 ≤ -1.5% 確認急跌恐慌（過濾慢磨下跌假訊號）
2. TP +5.0% / SL -4.5% 非對稱出場（盈虧比 1.11:1）
3. 延長持倉至 20 天（配合較高 TP）

Att1: ATR > 1.15 + 2日急跌 -1.5% + TP +5.0% / SL -4.5% / 20d
  → Part A 0.15 (WR 50.0%, 16訊號), Part B 0.48 (WR 75.0%, 8訊號)
  → min(A,B) 0.15（vs EWT-002 的 0.13，+15%）

Att2: ATR > 1.1 + 2日急跌 -1.5%（ATR 放寬由 2日急跌補償）
  → Part A 0.02 (WR 47.4%, 19訊號), Part B 0.30 (WR 62.5%, 8訊號)
  → min(A,B) 0.02 ✗ 退化，ATR 1.1 讓入 3 個壞信號（2 SL + 1 中性），2日急跌無法補償

Att3: ATR > 1.15 + 2日急跌 -1.5% + TP +5.0% / SL -5.5% / 20d（加寬 SL 呼吸空間）
  → Part A 0.08 (WR 50.0%, 16訊號), Part B 0.38 (WR 75.0%, 8訊號)
  → min(A,B) 0.08 ✗ 退化，SL 加寬未轉換任何 SL 交易，只增加虧損金額
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT004Config(ExperimentConfig):
    """EWT-004 2日急跌過濾 + 非對稱出場均值回歸參數"""

    # 回檔參數
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

    # 2日急跌過濾
    drop_2d_threshold: float = -0.015  # 2日報酬 <= -1.5%

    # 冷卻期
    cooldown_days: int = 8


def create_default_config() -> EWT004Config:
    return EWT004Config(
        name="ewt_004_crash_filter_asymmetric",
        experiment_id="EWT-004",
        display_name="EWT 2-Day Crash Filter + Asymmetric Exit MR",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（非對稱出場，提高盈虧比）
        stop_loss=-0.045,  # -4.5%（Att1 最佳，收緊 SL，reward/risk 1.11:1）
        holding_days=20,  # 延長持倉，配合較高 TP
    )
