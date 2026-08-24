"""
EWT-006: Optimized Exit Mean Reversion
(EWT 出場優化均值回歸)

基於 EWT-004 的 pullback+WR+ATR+2日急跌入場框架，優化出場參數：
1. 降低 TP 至 +3.5%（TP/vol 比從 79% 降至 55%，匹配成功實驗如 XLU-011 的 56%）
2. 縮短持倉至 15 天（減少到期交易的時間曝露）
3. 保留 SL -4.5% 甜蜜點與 2日急跌過濾

Att1: 移除 2日急跌 + TP +4.0% / SL -4.5% / 15d
  → Part A 0.15 (21訊號, WR 61.9%), Part B 0.89 (12訊號, WR 83.3%)
  → min(A,B) 0.15 ✗ 與 EWT-004 相同，額外訊號品質差（+1 SL +3 到期）

Att2★: 保留 2日急跌 + TP +3.5% / SL -4.5% / 15d
  → Part A 0.28 (WR 68.8%, 16訊號), Part B 0.50 (WR 75.0%, 8訊號)
  → min(A,B) 0.28（vs EWT-004 的 0.15，+87%）★ 3 expiry→TP 轉換

Att3: 保留 2日急跌 + TP +3.5% / SL -4.5% / 12d（進一步縮短時間曝露）
  → Part A 0.26 (WR 68.8%, 16訊號), Part B 0.34 (WR 62.5%, 8訊號)
  → min(A,B) 0.26 ✗ 退化，12d 太短導致 Part B 1 個 TP 到期轉換失敗
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT006Config(ExperimentConfig):
    """EWT-006 出場優化均值回歸參數"""

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


def create_default_config() -> EWT006Config:
    return EWT006Config(
        name="ewt_006_optimized_exit_mr",
        experiment_id="EWT-006",
        display_name="EWT Optimized Exit Mean Reversion",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（TP/vol 比 55%，匹配 XLU-011 的 56%）
        stop_loss=-0.045,  # -4.5%（EWT 甜蜜點）
        holding_days=15,  # 縮短持倉，減少時間曝露（Att2 最佳）
    )
