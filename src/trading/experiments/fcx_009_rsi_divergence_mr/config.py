"""
FCX RSI Bullish Hook Divergence + Pullback+WR Mean Reversion 配置 (FCX-009)

跨資產泛化測試：SIVR-015 Att1 驗證的 RSI(14) bullish hook divergence 模式
（pattern 20b）移植到 FCX。FCX 日波動 ~2.8-3.0% 落在 hook divergence
有效波動區間（2-3%）內，pullback 回看 10 日亦符合 ≤10 日限制。

進場框架建立於 FCX-002 的 pullback + WR (10 日)，但移除 ClosePos 過濾
（FCX 已驗證 ClosePos 反效果，lesson #34），並加入：
1. Pullback 上限 -18%（約 6σ，lesson #13 極端崩盤隔離）
2. RSI(14) bullish hook：RSI 自過去 5 日最低點回升 ≥ 3 點，且該最低點 ≤ 35
   （SIVR-015 Att1 驗證參數）

假設：FCX-002 的 Part A 2022 熊市 4 連停損主要因 RSI 仍在下探中觸發訊號；
bullish hook 過濾器可選擇性移除這些持續下跌訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXRSIDivergenceMRConfig(ExperimentConfig):
    """FCX RSI Bullish Hook Divergence + Pullback+WR 均值回歸參數"""

    pullback_lookback: int = 10
    pullback_threshold: float = -0.09  # 回檔 ≥ 9%（FCX-002 基線）
    pullback_cap: float = -0.18  # 回檔 ≤ 18%（約 6σ 崩盤隔離）

    wr_period: int = 10
    wr_threshold: float = -80.0

    rsi_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 5.0  # Att2: 加嚴 hook delta (SIVR-015 用 3.0, FCX 高波動嘗試更嚴)
    rsi_hook_max_min: float = 35.0

    cooldown_days: int = 10


def create_default_config() -> FCXRSIDivergenceMRConfig:
    return FCXRSIDivergenceMRConfig(
        name="fcx_009_rsi_divergence_mr",
        experiment_id="FCX-009",
        display_name="FCX RSI Bullish Hook Divergence + Pullback+WR MR",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.10,
        holding_days=20,
    )
