"""
EEM-008: Optimized Breakout
(EEM 優化突破策略)

EEM-005 BB Squeeze Breakout 是目前最佳（min Sharpe 0.18），但絕對績效偏低。
本實驗嘗試從出場和進場兩個方向優化突破策略。

Att1: BB Squeeze + 寬 SL -4.0% + 延長持倉 25 天
  → Part A 0.12 (18訊號, 61.1% WR), Part B 0.10 (10訊號, 60% WR)
  失敗：寬 SL 增加虧損幅度（-4.1% vs -3.1%），延長持倉讓到期交易惡化
  結論：EEM 停損交易為真正的 EM 結構性崩潰，非暫時性回撤

Att2: Range Compression Breakout（全新進場機制）
  → Part A -0.17 (40訊號, 42.5% WR), Part B 0.27 (18訊號, 66.7% WR)
  失敗：訊號過多（40 vs BB Squeeze 的 18），Part A 假突破過多
  Part B 0.27 證明壓縮突破概念在趨勢市有效，但 Part A EM 事件導致嚴重市場狀態依賴
  結論：進場訊號品質比數量重要，回歸 BB Squeeze 框架

Att3: BB Squeeze + 環境波動率過濾（20日實現波動率 ≤ 1.4%）
  - 回歸 EEM-005 的 BB Squeeze 進場（已證明 A/B 平衡最佳）
  - 新增環境波動率過濾：移除高波動期（EM 危機）的假突破
  - 假設：BB Squeeze 衡量相對壓縮，環境波動率衡量絕對水平。
    高波動期的「壓縮」仍是絕對高波動，突破更可能是噪音非趨勢。
  - 已知失敗模式：2021-2022 EM 壓力期 5 筆停損全在高波動環境
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM008Config(ExperimentConfig):
    """EEM-008 優化突破參數"""

    # 布林帶參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 擠壓偵測
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30  # 30th percentile
    bb_squeeze_recent_days: int = 5

    # 環境波動率過濾
    realized_vol_period: int = 20  # 實現波動率計算期間
    realized_vol_threshold: float = 0.014  # 1.4% 日波動上限

    # 趨勢確認
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EEM008Config:
    return EEM008Config(
        name="eem_008_optimized_breakout",
        experiment_id="EEM-008",
        display_name="EEM Optimized Breakout",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0% (same as EEM-005)
        holding_days=20,
    )
