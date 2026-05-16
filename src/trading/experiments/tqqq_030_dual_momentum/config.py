"""TQQQ-030 TQQQ Dual-Horizon Momentum Continuation 配置

策略方向：**動量 (Momentum)** — 純多時框動量堆疊（momentum stacking）。
repo 既有動量實驗：TQQQ-006（多日動量崩潰，下跌型）、TQQQ-015（**QQQ**
ROC(10) → trade TQQQ）；**從未於 TQQQ 自身做雙時框（短 + 中）動量堆疊
持續性確認**。

實驗動機 (Problem statement)：
- TQQQ-015 Att3（QQQ ROC10>5% + SMA50 + SMA200）Part A 0.19 / Part B
  0.17 失敗——訊號源為 1x QQQ。
- TQQQ-030 改於 TQQQ 自身計算雙時框動量（ROC 短 + ROC 中皆 > 閾值 =
  動量持續堆疊）+ 趨勢確認，測試「TQQQ-native 多時框動量持續性」是否
  較單一 QQQ ROC 乾淨。

迭代計畫（最多三次）：
- Att1: ROC(10) > 5% + ROC(20) > 8% + Close > SMA50，TP+10%/SL-8%/15d
- Att2: 視 Att1 結果 tune ROC 閾值 / 加 SMA200 bull regime
- Att3: 替代維度 — 縮短時框 或 加波動率上限（避開極端 vol regime 進場）

跨資產脈絡：
- 整合 TQQQ-006/015/027/028/029（動量/突破/趨勢/單日反轉皆失敗）——
  TQQQ-030 為「順勢動量」維度最後一塊拼圖，驗證 lesson #5 邊界：
  leveraged tech ETF 是否僅逆勢深度 capitulation 維度可產生 alpha。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQ030Config(ExperimentConfig):
    """TQQQ-030 TQQQ Dual-Horizon Momentum Continuation 參數"""

    # Att1: roc10>5, roc20>8, SMA50 → Part A 59/62.7%/Sharpe 0.31 /
    #   Part B 24/41.7%/Sharpe -0.11 cum -27.12% → min -0.11 REJECT
    #   （動量追高買 near-top，3x 放大 reversion，Part B 災難 -27%）
    # Att2: roc10>8, roc20>12 + SMA200 bull → Part A 38/57.9%/Sharpe 0.25 /
    #   Part B 14/57.1%/Sharpe 0.12 cum +9.53% → min 0.12 REJECT（Part B
    #   從 -27% 回正但 plateau 遠低 baseline 0.80）
    # Att3 ★ (saved as default): + 波動率上限 BB width/Close < 0.50（避開
    #   極端 vol regime blow-off-top 追高進場）
    roc_short_period: int = 10
    roc_short_threshold: float = 8.0  # ROC(10) > 8%
    roc_medium_period: int = 20
    roc_medium_threshold: float = 12.0  # ROC(20) > 12%

    trend_sma_period: int = 50  # Close > SMA(trend) 趨勢確認

    use_bull_filter: bool = True
    bull_sma_period: int = 200

    use_vol_cap: bool = True
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.50  # 避開極端 vol regime 進場

    cooldown_days: int = 10
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ030Config:
    return TQQQ030Config(
        name="tqqq_030_dual_momentum",
        experiment_id="TQQQ-030",
        display_name="TQQQ Dual-Horizon Momentum Continuation (TQQQ-native)",
        tickers=["TQQQ"],
        data_start="2018-06-01",  # 暖機 ROC/SMA/BB
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.10,
        stop_loss=-0.08,
        holding_days=15,
    )
