"""
USO-021: Bollinger Band Squeeze Breakout 配置
USO BB Squeeze Breakout Configuration

假說：USO 追蹤原油期貨（單一商品），與 COPX 等分散 ETF 不同，
不受 ETF 分散化削弱突破動能的問題。油價在盤整後常有爆發性突破，
BB Squeeze Breakout 可捕捉這類趨勢啟動。

USO 過去 20 次實驗均為均值回歸變體，從未嘗試突破策略。
本實驗基於 NVDA-004/FCX-004/TSLA-009 成功經驗，移植至 USO。

參數設計依據：
- USO 日波動 ~2.2%，介於 FCX(2-4%) 和 XLU(1.08%) 之間
- TP/SL 從 FCX-004 (TP+8%/SL-7%, vol 3%) 按 2.2/3.0 = 0.73x 縮放
- TP +6.0%：突破後趨勢延續可達此水平（不同於均值回歸的 +3.0% 硬上限）
- SL -5.0%：允許日內波動空間，避免假停損
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOBBSqueezeConfig(ExperimentConfig):
    """USO BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> USOBBSqueezeConfig:
    """建立預設配置"""
    return USOBBSqueezeConfig(
        name="uso_021_bb_squeeze_breakout",
        experiment_id="USO-021",
        display_name="USO BB Squeeze Breakout",
        tickers=["USO"],
        data_start="2019-01-01",
        profit_target=0.06,  # +6.0%（突破策略，非均值回歸的 +3.0% 上限）
        stop_loss=-0.05,  # -5.0%（允許日波動 2.2% 呼吸空間）
        holding_days=20,
    )
