"""
USO-021: Bollinger Band Squeeze Breakout 配置
USO BB Squeeze Breakout Configuration

假說：USO 追蹤原油期貨（單一商品），與 COPX 等分散 ETF 不同，
不受 ETF 分散化削弱突破動能的問題。油價在盤整後常有爆發性突破，
BB Squeeze Breakout 可捕捉這類趨勢啟動。

USO 過去 20 次實驗均為均值回歸變體，從未嘗試突破策略。

Att1: BB(20,2.0), 25th pct, TP+6%/SL-5% → Part A 0.53 / Part B -0.05
  Part A 優異但 Part B 假突破過多。

Att2: BB(20,2.5) 寬帶, 30th pct, TP+5%/SL-6% → Part A 0.25 / Part B -0.10
  BB(2.5) 過嚴：Part A 訊號 14→6，好訊號被移除。

Att3: BB(20,2.0), 20th pct（更嚴格擠壓）, SMA(100)（更強趨勢）, TP+5%/SL-5%
  假說：SMA(100) 過濾非趨勢環境的假突破（2022 H2、2024 衰退期），
  20th 百分位確保只有真正極端壓縮才觸發，BB(2.0) 保持足夠訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOBBSqueezeConfig(ExperimentConfig):
    """USO BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.20
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 100
    cooldown_days: int = 10


def create_default_config() -> USOBBSqueezeConfig:
    """建立預設配置"""
    return USOBBSqueezeConfig(
        name="uso_021_bb_squeeze_breakout",
        experiment_id="USO-021",
        display_name="USO BB Squeeze Breakout",
        tickers=["USO"],
        data_start="2019-01-01",
        profit_target=0.05,  # +5.0%（收窄 TP 提升達標率）
        stop_loss=-0.05,  # -5.0%（平衡：不太緊不太寬）
        holding_days=20,
    )
