"""
DIA-009: DIA/SPY 配對交易
DIA/SPY Pairs Trading Configuration

配對交易策略：利用 DIA 與 SPY 的價格比值 z-score 均值回歸。
當 DIA 相對 SPY 明顯低估（z-score < -2.5）且 DIA 仍在上升趨勢時買入。

DIA（道瓊 30 藍籌股，價格加權）與 SPY（S&P 500，市值加權）
同為美國大盤股指數 ETF，相關性極高，理論上價格比值應長期穩定。

三次嘗試結果（均未超越 DIA-005 的 min(A,B) Sharpe 0.47）：
- Att1: z<-2.0, 無過濾 → Part A 0.10/Part B 0.66, min(A,B) 0.10（25 訊號太多噪音）
- Att2: z<-2.5, +SMA(50) → Part A 0.26/Part B 0.26, min(A,B) 0.26（最佳，A/B 完美平衡）
- Att3: z<-1.5, +2日跌幅≥1.5% → Part A 0.05/Part B 2.99, min(A,B) 0.05（A/B 嚴重失衡）

結論：DIA/SPY 價格比值存在結構性漂移（SPY 科技股權重持續增加），
z-score 均值回歸假設不完全成立。與 SIVR/GLD、COPX/FCX、TSM/NVDA
配對交易失敗模式一致，即使是同資產類別（美國大盤指數 ETF）也無法避免。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIAPairsSPYConfig(ExperimentConfig):
    """DIA Pairs Trading 策略專屬參數"""

    pair_ticker: str = "SPY"
    zscore_lookback: int = 60
    zscore_entry: float = -2.5
    sma_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> DIAPairsSPYConfig:
    return DIAPairsSPYConfig(
        name="dia_009_pairs_spy",
        experiment_id="DIA-009",
        display_name="DIA Pairs Trading (DIA/SPY)",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=25,
    )
