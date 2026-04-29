"""
TSLA-014: Post-Capitulation Vol-Transition Mean Reversion Strategy

跨資產延伸 INDA-010 / EEM-014 / VGK-008 的「10 日 pullback + 2DD floor + ATR
ratio + WR」框架至 TSLA 高波動單一股票（3.72% 日波動）。所有參數縮放至 TSLA
規模，2DD floor 作為 capitulation 深度核心過濾。

設計理念：
- TSLA-001~004 既有均值回歸實驗均使用 60 日回撤框架（drawdown_lookback=60，
  threshold ≤ -20%），尚未測試 INDA-010 等成功的「10 日 pullback + 2DD floor」
  短期框架。
- USO-013（事件驅動 OPEC/地緣政治商品 ETF，2.2% vol，min(A,B) 0.26）證實 2DD
  floor 框架可用於事件驅動高波動資產，與 oscillator hook 失敗家族（lesson
  #20b）區分。
- TSLA 同為事件驅動（特斯拉新聞/交付/AI hype），預期此框架可改善 TSLA-009 Att2
  的 A/B 累計差距（59% > 30% 目標）。

迭代記錄：見 config.py docstring。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_014_vol_transition_mr.config import (
    TSLA014Config,
    create_default_config,
)
from trading.experiments.tsla_014_vol_transition_mr.signal_detector import (
    TSLA014SignalDetector,
)


class TSLA014Strategy(ExecutionModelStrategy):
    """TSLA Post-Capitulation Vol-Transition MR (TSLA-014)"""

    slippage_pct: float = 0.0015  # 0.15%（高波動單一股票滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA014Config):
            print(
                f"  回檔門檻 (Pullback): >= {abs(config.pullback_threshold):.0%}"
                f" ({config.pullback_lookback} 日)"
            )
            print(f"  回檔上限 (Cap): <= {abs(config.pullback_cap):.0%}")
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
            print(f"  2 日急跌下限: <= {config.drop_2d_floor:.1%}（capitulation 深度過濾）")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
