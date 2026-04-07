"""
TSM-009: Pairs Trading (TSM/NVDA) 配置
TSM/NVDA Pairs Trading Configuration

配對交易策略：利用 TSM 與 NVDA 的價格比值 z-score 均值回歸。
當 TSM 相對 NVDA 明顯低估（z-score < -2.0）時買入 TSM，預期比值回歸。

TSM 與 NVDA 同屬半導體產業鏈（NVDA 設計、TSM 代工），
理論上長期維持穩定的相對價值關係。

三次嘗試結果（均未超越 TSM-008 的 min(A,B) Sharpe 0.79）：
- Att1: z<-2.0, TP+7%/SL-7%/20d → Part A 0.40/Part B 0.57, min(A,B) 0.40（最佳）
- Att2: z<-2.0, TP+8%/SL-7%/25d → Part A 0.17/Part B 0.65, min(A,B) 0.17
- Att3: z<-2.5, TP+7%/SL-7%/20d → Part A 0.21/Part B 1.02, min(A,B) 0.21

結論：TSM/NVDA 價格比值存在結構性漂移（NVDA AI 驅動成長），
z-score 均值回歸假設不成立，與 SIVR/GLD、COPX/FCX 配對交易失敗模式一致。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMPairsTradingConfig(ExperimentConfig):
    """TSM Pairs Trading 策略專屬參數"""

    pair_ticker: str = "NVDA"
    zscore_lookback: int = 60
    zscore_entry: float = -2.0
    cooldown_days: int = 10


def create_default_config() -> TSMPairsTradingConfig:
    return TSMPairsTradingConfig(
        name="tsm_009_pairs_trading",
        experiment_id="TSM-009",
        display_name="TSM Pairs Trading (TSM/NVDA)",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.07,
        holding_days=20,
    )
