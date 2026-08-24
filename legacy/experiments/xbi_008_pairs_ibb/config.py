"""
XBI-008: XBI/IBB 配對交易
XBI/IBB Pairs Trading Configuration

配對交易策略：利用 XBI（等權重生技 ETF）與 IBB（市值加權生技 ETF）
的價格比值 z-score 均值回歸。當 XBI 相對 IBB 明顯低估時買入 XBI。

XBI（等權重）偏向小型生技股，IBB（市值加權）偏向大型生技股。
兩者追蹤同一板塊但權重方式不同，理論上價格比值應長期穩定。

三次嘗試結果（均未超越 XBI-005 的 min(A,B) Sharpe 0.36）：
- Att1: z<-2.0 + SMA(50) → Part A -0.19 (4訊號) / Part B 0.00 (1訊號)
- Att2: z<-1.5, 無過濾 → Part A -0.23 (41訊號) / Part B 0.07 (8訊號)
- Att3: z<-2.0 + WR(10)≤-80 → Part A -0.00 (19訊號) / Part B -0.19 (4訊號)

結論：XBI/IBB 價格比值不穩定。等權重 vs 市值加權的結構性差異
（小型生技 FDA 事件驅動、大型生技穩定營收）使得 z-score 均值回歸
假設不成立。與 DIA/SPY、SIVR/GLD、COPX/FCX 等配對交易失敗模式一致。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI008Config(ExperimentConfig):
    """XBI/IBB Pairs Trading 策略專屬參數"""

    pair_ticker: str = "IBB"
    zscore_lookback: int = 60
    zscore_entry: float = -2.0
    sma_period: int = 50
    use_sma_filter: bool = False
    wr_period: int = 10
    wr_threshold: float = -80.0
    use_wr_filter: bool = True
    cooldown_days: int = 10


def create_default_config() -> XBI008Config:
    return XBI008Config(
        name="xbi_008_pairs_ibb",
        experiment_id="XBI-008",
        display_name="XBI Pairs Trading (XBI/IBB)",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
    )
