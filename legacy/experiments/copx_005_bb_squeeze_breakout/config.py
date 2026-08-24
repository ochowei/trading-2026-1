"""
COPX-005: Bollinger Band Squeeze Breakout 配置
COPX BB Squeeze Breakout Configuration

假說：COPX 為銅礦 ETF，銅價趨勢驅動下波動收縮後的突破往往產生爆發性上漲。
基於 TSLA-005/NVDA-003/FCX-004 成功經驗（日波動 2-4%），移植至 COPX（日波動 ~2.25%）。
COPX-001~004 均為均值回歸策略，本實驗首次嘗試突破方向。

結果：突破策略在 COPX 上 OOS 完全失敗。Part A 合理但 Part B 結構性虧損。
COPX-003 均值回歸（Sharpe 0.39/0.35）仍為全域最優。

嘗試記錄：
- Att1: TP+6%/SL-5%/30th pct → Part A Sharpe 0.29, Part B -0.17 (3/6 停損)
- Att2: TP+7%/SL-6%/30th pct → Part A Sharpe 0.30, Part B -0.17 (寬 SL 無幫助)
- Att3: TP+7%/SL-6%/20th pct → Part A Sharpe 0.33, Part B 0.01 (略改善，仍遠不及 COPX-003)

失敗原因：COPX 2024-2025 處於盤整/回落期，突破訊號多為假突破。
ETF 波動 2.25% 可能處於突破策略有效範圍的下邊界（FCX 2-4%、TSLA 3-4%、NVDA 3.26% 均 >2.25%）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPXBBSqueezeConfig(ExperimentConfig):
    """COPX BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.20
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 12


def create_default_config() -> COPXBBSqueezeConfig:
    """建立預設配置"""
    return COPXBBSqueezeConfig(
        name="copx_005_bb_squeeze_breakout",
        experiment_id="COPX-005",
        display_name="COPX BB Squeeze Breakout",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.07,
        stop_loss=-0.06,
        holding_days=20,
    )
