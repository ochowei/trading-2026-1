"""
FXI-007: Relative Strength Momentum Pullback (FXI vs EEM)

策略理念：FXI（中國大盤 ETF）在 EEM 中權重約 25-30%，但其相對表現
受中國政策週期（刺激政策、地緣政治）驅動，與一般新興市場行為有明顯差異。
當 FXI 相對 EEM 展現結構性超額表現時，代表中國政策利多被市場定價。
在動量優勢下買入短期淺回調，避開 2022 中國熊市的均值回歸陷阱
（該期 FXI 相對 EEM 持續弱勢）。

參考實驗：
- EWT-007 (min 0.42)：EEM 作為參考基準於半導體出口驅動的台灣 ETF 成功
- INDA-007：失敗（印度結構性優勢由人口紅利驅動，不產生有效 RS 訊號）
- EWZ-005：失敗（巴西商品優勢由宏觀事件驅動）
- FXI 獨特點：中國相對 EM 的超額/劣勢由政策週期驅動，與印度/巴西不同

本實驗為 FXI 首次嘗試 RS 動量策略。

Att1: EEM ref, RS>=3%, pullback 2-5%, SMA(50), TP+4.0%/SL-4.5%/20d
  → Part A -0.22 (13 訊號, WR 46.2%, -12.31%), Part B 0.79 (9 訊號, WR 77.8%, +23.42%)
  → min(A,B) -0.22 ✗ 2022 中國熊市產生 4 SL 拖累 Part A
  → 失敗根因：SMA(50) 無法濾除 2022 熊市中的技術性反彈訊號，當 FXI 在
    SMA(200) 之下時，SMA(50) 常被反彈觸及但仍屬熊市規律

Att2: EEM ref, RS>=3%, pullback 2-5%, SMA(200), TP+4.0%/SL-4.5%/20d
  - 加強趨勢過濾至 SMA(200)，隔離 2022 中國熊市
  - 其他參數沿用 Att1
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI007Config(ExperimentConfig):
    """FXI-007 相對強度動量回調策略參數"""

    reference_ticker: str = "EEM"
    sma_trend_period: int = 200
    relative_strength_period: int = 20
    relative_strength_min: float = 0.03  # FXI - EEM 20日報酬差 >= 3%
    pullback_lookback: int = 5
    pullback_min: float = 0.02  # 5日高點回撤 >= 2%
    pullback_max: float = 0.05  # 5日高點回撤 <= 5%
    cooldown_days: int = 10


def create_default_config() -> FXI007Config:
    return FXI007Config(
        name="fxi_007_rs_momentum",
        experiment_id="FXI-007",
        display_name="FXI Relative Strength Momentum Pullback",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（中等波動 2.0% 配對 EM 標準）
        stop_loss=-0.045,  # -4.5%（需呼吸空間）
        holding_days=20,
    )
