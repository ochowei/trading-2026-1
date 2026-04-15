"""
FXI-004: 2-Day Decline Mean Reversion
(FXI 2日急跌均值回歸)

策略假設：
- 2 日急跌過濾取代 ATR+ClosePos，直接測量賣壓加速度
- 回檔門檻 5%（2.5σ for 2% vol）確保只進場在深度回檔
- 回檔上限 12% 隔離 COVID/監管風暴等極端崩盤

Att1: PB>=5% + RSI(5)<28 + 2d decline<=-2.0% + cap12% + cooldown10d
      TP+5%/SL-4.5%/18d
  → Part A -0.03 (38訊號, WR47.4%, -9.76%), Part B 0.24 (7訊號, WR57.1%, +6.22%)
  → 訊號過多（Part A 7.6/年），品質低（20停損 vs 16達標），A/B 5.4:1 嚴重失衡
  → 失敗原因：RSI(5)<28 + 2d decline -2.0% 門檻太鬆，中國熊市慢磨大量假訊號

Att2: RSI(5)<22 + 2d decline<=-3.0%（大幅收緊門檻，只捕捉極端恐慌）
      PB>=5% + cap12% + cooldown10d + TP+5%/SL-4.5%/18d
  → Part A -0.11 (24訊號, WR41.7%, -14.00%), Part B 0.31 (4訊號, WR50%, +4.73%)
  → 收緊門檻反而降低 WR（47.4%→41.7%），RSI(5) 在 FXI 2.0% vol 根本無法區分恐慌 vs 慢磨
  → 失敗原因：RSI(5) 對中國政策驅動資產無效（教訓 #27 延伸）

Att3★: 回歸 WR(10) + 2d decline 作為品質過濾（取代 ATR+ClosePos）
       PB>=5% + WR(10)<=−80 + 2d decline<=-2.0% + cap12% + cooldown10d
       TP+5%/SL-4.5%/18d
  → Part A 0.01 (45訊號, WR48.9%, -2.06%), Part B 0.05 (12訊號, WR50%, +1.67%)
  → WR(10) 大幅優於 RSI(5)，但 2d decline 選擇性不足（45訊號 vs FXI-002的26）
  → 結論：ATR+ClosePos 仍為 FXI 最佳品質過濾，2d decline 無法取代
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI004Config(ExperimentConfig):
    """FXI-004 2日急跌均值回歸參數"""

    # 回檔參數
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # 10日高點回檔 >= 5%
    pullback_cap: float = -0.12  # 回檔上限 12%

    # Williams %R 超賣確認（Att3: 回歸 WR(10)）
    wr_period: int = 10
    wr_threshold: float = -80.0  # WR(10) <= -80

    # 2日急跌過濾
    decline_2d_threshold: float = -0.020  # 2日累計跌幅 <= -2.0%

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FXI004Config:
    return FXI004Config(
        name="fxi_004_rsi5_2d_decline",
        experiment_id="FXI-004",
        display_name="FXI 2-Day Decline MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%
        stop_loss=-0.045,  # -4.5%
        holding_days=18,
    )
