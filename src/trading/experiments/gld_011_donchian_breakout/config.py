"""
GLD-011: Donchian Channel Breakout 配置
GLD Donchian Channel Breakout Configuration

GLD 未嘗試過的策略：Donchian 通道突破（趨勢跟蹤）。
不同於 GLD-009 BB Squeeze（需要波動收縮後突破），
Donchian 突破捕捉的是價格創新高的趨勢啟動訊號。
黃金具有強趨勢特性（2018-2020、2023-2024 長趨勢），
Donchian 突破可能比 BB Squeeze 更適合捕捉這類趨勢。

嘗試記錄：
- Att1: Donchian(20) + SMA(50) + ATR(14) 低波動確認
  TP+3.5%/SL-3.0%/20d/cd10
  → Part A Sharpe 0.18 / Part B 0.34（WR 54.3%/64.7%，35/17 訊號）
  ATR 過濾未有效改善品質，Part A 太多假突破
- Att2: Donchian(30) + SMA(50)，移除 ATR 過濾
  TP+3.5%/SL-3.5%/25d/cd15
  → Part A Sharpe 0.08 / Part B 0.73（WR 56.2%/80.0%，32/15 訊號）
  Part B 極佳但 Part A 極差，A/B 嚴重失衡（趨勢策略在震盪期結構性失效）
- Att3: Donchian(50) + SMA(100)，更長回看窗口捕捉更顯著的突破
  TP+4.0%/SL-3.5%/25d/cd20
  → Part A Sharpe 0.29 / Part B 0.22（WR 66.7%/58.3%，21/12 訊號）
  最佳 A/B 平衡（gap 0.07）但 min(A,B)=0.22 仍遠低於 GLD-008 的 0.45

結論：Donchian 突破策略在 GLD 上 min(A,B) 最佳為 0.22（Att3），
遠低於 GLD-008 的 0.45。GLD 日波動 1.1% 限制突破幅度（同 GLD-009 結論），
且趨勢策略結構性受市場狀態依賴（震盪期 Part A 失效，趨勢期 Part B 優異）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD011Config(ExperimentConfig):
    """GLD Donchian Channel Breakout 策略專屬參數"""

    donchian_period: int = 50
    sma_trend_period: int = 100
    cooldown_days: int = 20


def create_default_config() -> GLD011Config:
    """建立預設配置"""
    return GLD011Config(
        name="gld_011_donchian_breakout",
        experiment_id="GLD-011",
        display_name="GLD Donchian Channel Breakout",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.040,
        stop_loss=-0.035,
        holding_days=25,
    )
