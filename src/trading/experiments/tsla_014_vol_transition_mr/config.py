"""
TSLA Post-Capitulation Vol-Transition 均值回歸配置 (TSLA-014)

動機：TSLA-009 Att2（BB Squeeze 突破，當前最佳 min(A,B) Sharpe 0.40）的 Part A/B
平衡仍偏弱（Part A 累計 +64% / Part B +26%，cum 差 59%）。TSLA 13 個既有實驗中，
均值回歸（TSLA-001~004）均使用 60 日回撤框架（drawdown_lookback=60，threshold
≤ -20%），尚未測試 INDA-010 / EEM-014 / VGK-008 / USO-013 等成功的「10 日 pullback
+ 2DD floor + ATR ratio + WR」短期框架。

核心假設：USO-013（事件驅動 OPEC/地緣政治商品 ETF，2.2% vol，min(A,B) 0.26）的
10 日緊密 pullback 範圍 + 2DD floor 框架成功；TSLA 為事件驅動單一股票（特斯拉
新聞/交付/AI hype，3.72% vol），雖 vol 倍數約 1.7x USO 但事件驅動結構相似，預期
框架可移植。

跨資產縮放（TSLA / INDA = 3.72% / 0.97% ≈ 3.8x）：
- 10 日 pullback：INDA [-7%, -3%] → TSLA [-25%, -10%]（3-4x scale）
- 2DD floor：INDA -2.0% → TSLA -5%（2.5x scale，Att1 baseline）
- TP / SL：INDA ±3.5/4% → TSLA ±7%（2x for high-vol breathing room）
- 持倉：INDA 15d → TSLA 15d
- 冷卻：INDA 7d → TSLA 10d

========================================================================
Att1（baseline，2026-04-25）：FAILED min(A,B) -0.01
========================================================================
參數：10 日 pullback [-25%, -10%] + WR(10) ≤ -80 + ClosePos ≥ 0.35
      + ATR(5)/ATR(20) > 1.15 + 2DD floor ≤ -5%
      + TP +7% / SL -7% / 15 天 / 冷卻 10 天
結果：Part A 4 訊號 50% WR Sharpe -0.01 / Part B 1 訊號 0% WR / min -0.01
失敗：訊號過稀（8 年 4/1），多重綁定 + 深 2DD 過嚴

========================================================================
Att2（放寬 pullback 與 2DD，2026-04-25）：FAILED min(A,B) -0.59
========================================================================
參數調整：pullback_threshold -10% → -8%，drop_2d_floor -5% → -3%
結果：Part A 7/42.9%/-0.15 / Part B 4/25%/**-0.59** / min -0.59
失敗：放寬引入 bear regime 訊號集，Part B 7/12 為 SL

========================================================================
Att3（收緊品質而非放寬，2026-04-25）：
========================================================================
參數調整：pullback_threshold -8% → -12%，drop_2d_floor -3% → -4%，
WR_threshold -80 → -85，ClosePos 0.35 → 0.50

直覺：Att1 過嚴 / Att2 過鬆均失敗，測試「中度深度 + 強反轉確認」是否能
過濾出真實 capitulation 反轉（vs 持續下跌 mid-decline）

成交模型：0.15% slippage（高波動單一股票）、隔日開盤市價進場
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA014Config(ExperimentConfig):
    """TSLA-014 Post-Capitulation Vol-Transition MR 參數"""

    # 進場 — 10 日高點回檔（深度 capitulation）
    # Att1 -10%：訊號過稀（4/1）
    # Att2 -8%：訊號 7/4 但 Part B 25% WR 大量 bear regime SL
    # Att3：收緊至 -12%，要求更深 capitulation
    pullback_lookback: int = 10
    pullback_threshold: float = -0.12
    pullback_cap: float = -0.25  # 回檔 ≤ 25%（隔離極端崩盤如 2022 -65%）

    # 進場 — Williams %R 超賣（Att3 加深至 -85）
    wr_period: int = 10
    wr_threshold: float = -85.0

    # 進場 — 收盤位置（Att3 加強至 0.50，要求更明顯日內反轉）
    close_position_threshold: float = 0.50

    # 進場 — 波動率自適應過濾
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 進場 — 2 日急跌下限
    # Att1 (-5%)：訊號過稀
    # Att2 (-3%)：訊號 7/4 但 Part B 25% WR
    # Att3：加深至 -4%（介於 Att1/Att2 之間，要求中度 capitulation 深度）
    drop_2d_floor: float = -0.04

    # 冷卻天數
    cooldown_days: int = 10


def create_default_config() -> TSLA014Config:
    return TSLA014Config(
        name="tsla_014_vol_transition_mr",
        experiment_id="TSLA-014",
        display_name="TSLA Post-Capitulation Vol-Transition MR",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.07,
        holding_days=15,
    )
