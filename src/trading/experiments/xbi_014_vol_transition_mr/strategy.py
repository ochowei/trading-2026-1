"""
XBI-014: Post-Capitulation Vol-Transition Mean Reversion Strategy

跨資產延伸 VGK-008 Att2 / INDA-010 Att3 / EEM-014 Att2 / USO-013 / IBIT-009
Att1 的「2DD floor 加深」模板至 XBI 生技板塊 ETF：在 XBI-005 pullback+WR
+ClosePos 框架上，新增 2 日報酬下限 drop_2d_floor 過濾「shallow 2DD = slow-
melt drift」失敗訊號。

XBI 2.0% 日波動位於該模板已驗證 vol 區間 [0.97%, 3.17%] 內，是 repo 首次將
此模板移植至 US 生技板塊 ETF。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xbi_014_vol_transition_mr.config import (
    XBI014Config,
    create_default_config,
)
from trading.experiments.xbi_014_vol_transition_mr.signal_detector import (
    XBI014SignalDetector,
)


class XBI014Strategy(ExecutionModelStrategy):
    """XBI Post-Capitulation Vol-Transition MR (XBI-014)"""

    slippage_pct: float = 0.001  # 0.1% (ETF 標準滑價)

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XBI014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XBI014Config):
            print(
                f"  回檔範圍 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" {abs(config.pullback_threshold):.0%}-{abs(config.pullback_upper):.0%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  反轉K線: ClosePos >= {config.close_position_threshold:.0%}")
            print(
                f"  2 日急跌下限: <= {config.drop_2d_floor:.1%}"
                "（XBI-014 核心新增，post-capitulation 過濾）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
