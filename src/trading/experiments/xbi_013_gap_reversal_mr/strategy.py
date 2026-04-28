"""
XBI-013: Gap-Down Capitulation + Intraday Reversal Mean Reversion Strategy

跨資產延伸 IBIT-006 至 XBI 生技板塊 ETF：測試「事件驅動隔夜拋壓 + 日內反轉」
結構是否適用 US 板塊 ETF（首次）。XBI 2.0% vol、FDA/臨床/收購公告驅動，
與 BTC 24/7 不同但事件資訊完全公告結構可能滿足 IBIT-006 成功前提。

進場參數（Att1 baseline）：
- Gap <= -1.0%（縮放自 IBIT -1.5%，XBI 0.63x vol）
- Close > Open（日內反轉確認）
- 10日高點回檔 in [-5%, -15%]
- Williams %R(10) <= -80
- 冷卻 10 天

出場參數：
- TP +3.0%（縮放自 IBIT +4.5%）
- SL -3.0%（縮放自 IBIT -4.0%）
- 持倉 15 天
- 成交模型：隔日開盤市價進場，滑價 0.1%（ETF）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_013_gap_reversal_mr.config import (
    XBI013Config,
    create_default_config,
)
from trading.experiments.xbi_013_gap_reversal_mr.signal_detector import (
    XBI013SignalDetector,
)


class XBI013Strategy(ExecutionModelStrategy):
    """XBI Gap-Down Capitulation + Intraday Reversal MR (XBI-013)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI013Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  隔夜跳空 (Gap): Gap <= {config.gap_threshold:.1%}（深 gap 測試）")
            if config.require_up_bar:
                print("  日內反轉: Close > Open")
            if config.use_close_position:
                print(f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
