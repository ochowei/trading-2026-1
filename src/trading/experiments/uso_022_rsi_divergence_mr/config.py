"""
USO RSI(14) Bullish Hook Divergence + USO-013 均值回歸框架 (USO-022)

基於 USO-013（10日回檔 7-12% + RSI(2) < 15 + 2日報酬 ≤ -2.5%），
加入 RSI(14) bullish hook 過濾器，嘗試辨識「RSI 已自近期低點回升」的
capitulation 尾聲訊號，過濾 RSI 仍在下探中的持續下跌訊號。

Cross-asset 教訓 20b（SIVR-015 Att1 驗證）：
- 規則：RSI(14) 今日 − 過去 5 日最低點 ≥ 3 點，且 5 日最低 ≤ 35（oversold）
- 有效條件六項：中高波動（2-3%）、已驗證 pullback+WR 框架、回看 ≤10 日、
  Part A/B 皆活躍 MR regime、RSI 轉折=真實反轉結構、訊號日 RSI 分布集中於 ≤35

USO 形式上符合前四項：日波動 ~2.2%、10日回檔框架、USO-013 為已驗證框架、
Part A/B 皆為活躍的油價均值回歸 regime。第五、六項為本實驗驗證目標。

Hypothesis: USO-013 Part A WR 65.7%（12 stop-outs in 35 trades）裡有部分訊號
在 RSI(14) 仍下探中觸發（持續下跌末段），hook 過濾器可能選擇性移除這些訊號。

風險：USO-020 資料分析顯示停損 vs 達標交易在波動率/範圍上完全重疊（殘餘停損
為「隨機」）。hook 過濾器由 RSI 方向判斷，與波動率分析正交，可能仍有區分力。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USORSIDivergenceMRConfig(ExperimentConfig):
    """USO RSI(14) Bullish Hook Divergence + USO-013 均值回歸參數"""

    # Att3：改用 SIVR-015 pattern（pullback + WR + hook，無 RSI(2) 無 2DD）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥ 7%
    pullback_max: float = -0.12  # 回檔 ≤ 12%
    wr_period: int = 10
    wr_threshold: float = -80.0

    # RSI(14) bullish hook 過濾
    rsi14_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0

    cooldown_days: int = 10


def create_default_config() -> USORSIDivergenceMRConfig:
    return USORSIDivergenceMRConfig(
        name="uso_022_rsi_divergence_mr",
        experiment_id="USO-022",
        display_name="USO RSI(14) Bullish Hook Divergence + USO-013",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,  # +3.0%（USO contango 硬上限）
        stop_loss=-0.0325,  # -3.25%（USO-013 甜蜜點）
        holding_days=10,
    )
