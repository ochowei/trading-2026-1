"""
CIBR 波動率自適應均值回歸配置 (CIBR Volatility-Adaptive Mean Reversion Config)

基於 CIBR-001（回檔+WR），新增：
- ATR(5)/ATR(20) > 1.15 波動率急升過濾（區分恐慌拋售 vs 慢磨下跌）
- ClosePos >= 40% 日內反轉確認（收盤位置高於日內低點 40% 以上）

跨資產證據：XLU-011(1.0% vol, ATR>1.15 → +272%)、IWM-011(1.5-2%, ATR>1.1 → +67.7%)
CIBR 日波動 1.53% 介於兩者之間，ATR 門檻選 1.15（接近 XLU/EWJ 甜蜜點）。
ClosePos 在日波動 ≤ 2.0% 有效（GLD 1.1%、IWM 1.5-2%、XBI 2.0% 均驗證）。

Att1: 回檔>=5% + ATR>1.15 + ClosePos>=40% → Part A 0.18/Part B 0.79
Att2: +12% 回檔上限 → 移除好訊號（2022-05-10 +3.50%），Sharpe 0.18→0.12，撤回
Att3: 回檔門檻降至 4%（= 2.6σ，與 GLD/EWJ 的 sigma 比例一致）→ Final
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBRVolAdaptiveMRConfig(ExperimentConfig):
    """CIBR 波動率自適應均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.04  # 回檔 >=4%（2.6σ，與 GLD/EWJ sigma 比例一致）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80 (超賣)
    close_pos_threshold: float = 0.40  # 收盤位置 >= 40%（日內反轉確認）
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15  # ATR(5)/ATR(20) > 1.15
    cooldown_days: int = 8


def create_default_config() -> CIBRVolAdaptiveMRConfig:
    return CIBRVolAdaptiveMRConfig(
        name="cibr_002_vol_adaptive_mr",
        experiment_id="CIBR-002",
        display_name="CIBR Volatility-Adaptive Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=18,  # 18 天
    )
