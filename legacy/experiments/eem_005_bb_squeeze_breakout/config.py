"""
EEM-005: BB Squeeze Breakout
(EEM 布林帶擠壓突破)

EEM 前 4 個實驗均為均值回歸策略，Part A Sharpe 最高僅 0.06。
本實驗嘗試完全不同的策略類型：突破。

設計理據：
- EEM 受 EM risk-on/risk-off 資金流驅動，波動率壓縮後常有方向性突破
- Lesson #28 警告分散化 ETF 上 BB Squeeze 可能失效，但 EEM 未實測
- 突破策略天然迴避 EM 熊市問題（不在下跌中買入）
- 參數參考 TSLA-009 Att2 框架，按 EEM 波動度 (1.17%) 縮放

Att1: BB(20,2.0) + 30th pct squeeze + SMA(50) + TP3.5%/SL3.0%/15天 + cooldown 10
  → Part A 0.29 (18訊號, WR 61.1%), Part B 0.14 (10訊號, WR 60.0%)
  問題：Part B 50% 交易到期（TP 3.5% 對 1.17% vol ETF 偏高）

Att2: 降 TP 至 3.0% + 延長持倉至 20 天（更多時間達標，減少到期出場）
  → Part A 0.20 (18訊號, WR 61.1%), Part B 0.18 (10訊號, WR 60.0%) ★
  改善：Part B 從 0.14 → 0.18（多 3 筆 TP 命中），min(A,B) 0.18 > 0.14
  A/B 平衡極佳：Sharpe gap 0.02

Att3: 擠壓門檻收緊至 25th 百分位（減少假突破）
  → Part A 0.29 (17訊號, WR 64.7%), Part B 0.18 (10訊號, WR 60.0%)
  移除 1 假突破（2021-06-01 中國監管），但 A/B gap 擴大
  min(A,B) 0.18 同 Att2，但 A/B 平衡較差

Final: 選擇 Att2（30th pct）— min(A,B) 0.18 且 A/B 平衡最佳 (0.20/0.18)
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM005Config(ExperimentConfig):
    """EEM-005 BB 擠壓突破參數"""

    # 布林帶參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 擠壓偵測
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30  # 30th percentile
    bb_squeeze_recent_days: int = 5

    # 趨勢確認
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EEM005Config:
    return EEM005Config(
        name="eem_005_bb_squeeze_breakout",
        experiment_id="EEM-005",
        display_name="EEM BB Squeeze Breakout",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（EEM 1.17% vol 適當目標）
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
