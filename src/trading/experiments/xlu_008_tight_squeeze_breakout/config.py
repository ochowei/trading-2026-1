"""
XLU-008: Tight BB Squeeze Breakout 配置
XLU Tight BB Squeeze Breakout Configuration

Att1 (20th pct + cd15): 結果與 XLU-004 完全相同（Sharpe 0.18/0.26），因所有突破事件
   本身已處於 20th percentile 以下，冷卻期自然間隔 > 15 天，參數變更無效。

Att2: 加入成交量確認（突破日 Volume > 1.3x 20日均量），過濾低量假突破。
   恢復 25th pct + cd 7d（同 XLU-004 基線），僅增加成交量過濾器。
   結果：Part A 訊號 13→4、Sharpe 0.07，成交量過濾移除好訊號（確認 lesson #6）。

Att3: 使用更寬 BB(20,2.5)（XLU-004 用 BB(20,2)），更高突破門檻自然過濾弱突破。
   XLU-004 Att3 測試過 BB(20,2.5) 但搭配 TP+3.5%/SL-3.5%（失敗原因是出場參數），
   此次搭配已驗證的最佳出場 TP+3.0%/SL-4.0%，是未測試的新組合。

出場參數沿用 XLU 全域甜蜜點：TP +3.0% / SL -4.0% / 20天。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU008TightSqueezeConfig(ExperimentConfig):
    """XLU-008 Tight BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.5
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 7
    volume_confirmation: bool = False
    volume_ratio: float = 1.3
    volume_lookback: int = 20


def create_default_config() -> XLU008TightSqueezeConfig:
    """建立預設配置"""
    return XLU008TightSqueezeConfig(
        name="xlu_008_tight_squeeze_breakout",
        experiment_id="XLU-008",
        display_name="XLU Tight BB Squeeze Breakout",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.04,
        holding_days=20,
    )
