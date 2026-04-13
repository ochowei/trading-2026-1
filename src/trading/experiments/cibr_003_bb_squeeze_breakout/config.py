"""
CIBR-003: BB Squeeze Breakout
(CIBR 布林帶擠壓突破)

CIBR 前 2 個實驗均為均值回歸策略，Part A Sharpe 最高 0.18（CIBR-002）。
本實驗嘗試完全不同的策略方向：突破。

設計理據：
- 網路安全板塊具有主題投資特性，當板塊輪動進入/退出時有方向性突破
- CIBR 日波動 1.53%，在 BB Squeeze 有效排序中屬「高流動 ETF(1.5-2%)」
- 參數參考 EEM-005 Att2 框架，按 CIBR 波動度 (1.53% vs EEM 1.17%) 縮放
- TP/SL 按波動比 1.31x 調整：EEM 3.0% → CIBR 4.0%
- SMA(50) 趨勢確認（跨資產驗證甜蜜點）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBRBBSqueezeConfig(ExperimentConfig):
    """CIBR-003 BB 擠壓突破參數"""

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


def create_default_config() -> CIBRBBSqueezeConfig:
    return CIBRBBSqueezeConfig(
        name="cibr_003_bb_squeeze_breakout",
        experiment_id="CIBR-003",
        display_name="CIBR BB Squeeze Breakout",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.04,  # +4.0%（CIBR 1.53% vol，按 EEM 3.0% × 1.31x）
        stop_loss=-0.04,  # -4.0%（對稱，~2.6σ 呼吸空間）
        holding_days=20,
    )
