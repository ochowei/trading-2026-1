"""
XLU-012: Post-Capitulation Vol-Transition Mean Reversion Strategy

跨資產延伸 CIBR-012 / INDA-010 / EEM-014 的 2DD 區間過濾方向至 XLU 1.08% vol
利率敏感公用事業 ETF。XLU-011（min(A,B) 0.67）的 A/B 平衡未達標（cum 差 33%、
訊號比 1.75:1），本實驗以 2DD 雙向區間過濾測試 XLU 失敗結構與 CIBR / INDA 的
對齊性。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.xlu_012_vol_transition_mr.config import (
    XLU012Config,
    create_default_config,
)
from trading.experiments.xlu_012_vol_transition_mr.signal_detector import (
    XLU012SignalDetector,
)


class XLU012Strategy(ExecutionModelStrategy):
    """XLU Post-Capitulation Vol-Transition MR (XLU-012)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return XLU012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, XLU012Config):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.1%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.1%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 比率過濾: ATR({config.atr_short_period})"
                f" / ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            if config.drop_2d_floor >= 0.50:
                print("  2 日急跌下限 (Floor): 停用")
            else:
                print(f"  2 日急跌下限 (Floor): <= {config.drop_2d_floor:.1%}")
            if config.drop_2d_cap <= -0.50:
                print("  2 日急跌上限 (Cap): 停用")
            else:
                print(f"  2 日急跌上限 (Cap): >= {config.drop_2d_cap:.1%}")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
