"""
INDA-009: CCI Oversold Reversal Mean Reversion
(INDA CCI 深度超賣 + 反轉均值回歸)

動機：INDA-005 Att3（10日回檔 3-7% + WR+ClosePos+ATR+2日跌幅，TP+3.5%/SL-4%/15d）
min(A,B) Sharpe 0.23，Part A Sharpe 0.23 / Part B Sharpe 0.31。INDA 已證明 pullback+WR
框架飽和（INDA-006 三次調參失敗），BB 混合進場失敗（INDA-008），RS 動量失敗
（INDA-007）。本實驗探索 repo 中尚未使用的指標方向 —— Commodity Channel Index (CCI)
作為主要進場訊號。**repo 首次試驗 CCI 指標**。

CCI 與 RSI/BB 的關鍵差異：
- CCI 用「平均絕對偏差 (MAD)」量化當前 Typical Price 偏離 SMA 的程度，對極端值
  較不敏感（vs BB 用 std 對極端值放大）
- CCI 無邊界（與 RSI/WR 0-100 區間不同），可達 -200/-300 極端值，允許「很深但仍
  在回歸範圍」與「深到崩盤」之間的區分
- CCI(20) < -100 傳統「超賣」，< -200 傳統「極端超賣」

INDA-009 的設計邏輯：
- 進場主訊號：CCI(20) 觸及深度超賣，然後「今日 CCI > 過去 2 日 CCI 最低點」
  （CCI 轉折向上確認反轉）
- 反轉確認：Close > Open（K 線收紅，日內反轉證據）
- 冷卻期 10 天（同 INDA-005）
- 出場：TP+3.5% / SL-4.0% / 持倉 15 天（同 INDA-005 甜蜜點）

Att1 (baseline): CCI(20) ≤ -100 + CCI 轉折 + Close > Open + cd=10
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA009Config(ExperimentConfig):
    """INDA-009 CCI 超賣反轉均值回歸參數"""

    # CCI 參數
    cci_period: int = 20
    cci_oversold: float = -100.0  # Att1：標準超賣門檻
    # CCI 轉折確認：今日 CCI 比 N 日前低點高出至少 delta 點
    cci_turn_lookback: int = 2
    cci_turn_delta: float = 0.0

    # 反轉 K 線確認
    require_close_gt_open: bool = True

    # ClosePos 過濾（Att1 預設關閉）
    use_close_pos: bool = False
    close_pos_threshold: float = 0.40

    # 10 日高點回檔（Att1 預設關閉，pullback_threshold 0 相當於不過濾）
    pullback_lookback: int = 10
    pullback_threshold: float = 0.0  # 0 = 無門檻；負值 = 要求至少此比例回檔

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> INDA009Config:
    return INDA009Config(
        name="inda_009_cci_oversold_mr",
        experiment_id="INDA-009",
        display_name="INDA CCI Oversold Reversal Mean Reversion",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=15,  # 同 INDA-005 Att3
    )
