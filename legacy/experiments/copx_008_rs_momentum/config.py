"""
COPX-008: Copper Sector RS Momentum / Donchian Breakout 配置

三次嘗試：
- Att1: RS(20d) >= 5%, pullback 3-8% from 5d high, SMA(50),
        TP+5.0%/SL-5.0%/20d/cd10
        → Part A Sharpe -0.07 / Part B -0.05, WR 46%/46%, 累計 -12%/-4%
        TP+5.0% 太寬，WR 不足以覆蓋對稱 TP/SL
- Att2: RS(10d) >= 4%, pullback 3-8%, SMA(50),
        TP+3.5%/SL-4.5%/20d/cd10（使用 COPX 已驗證出場參數）
        → Part A Sharpe -0.09 / Part B -0.19, WR 53%/44%, 累計 -8%/-7%
        RS 方向根本無效：銅礦 ETF 相對大盤超額表現不具預測力
- Att3: Donchian 20日突破 + SMA(50) 趨勢確認,
        TP+3.5%/SL-4.5%/20d/cd12（完全不同策略方向，趨勢跟蹤取代動量回調）
        → Part A Sharpe 0.17 / Part B 0.16, WR 64%/65%, 累計 +23%/+10%
        A/B 平衡極佳（gap 0.01），但 min(A,B) 0.16 遠低於 COPX-007 的 0.45 ★

結論：RS 動量在銅礦 ETF 完全無效，Donchian 突破可行但劣於均值回歸。
COPX-007 仍為全域最優。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX008Config(ExperimentConfig):
    """COPX-008 Donchian 突破策略參數"""

    # Donchian 通道參數
    donchian_period: int = 20  # N 日新高突破

    # 趨勢確認
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 12


def create_default_config() -> COPX008Config:
    return COPX008Config(
        name="copx_008_rs_momentum",
        experiment_id="COPX-008",
        display_name="COPX Donchian Breakout (Att3)",
        tickers=["COPX"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%（COPX 已驗證甜蜜點）
        stop_loss=-0.045,  # -4.5%（COPX 已驗證甜蜜點）
        holding_days=20,
    )
