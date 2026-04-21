"""
INDA-010: Post-Capitulation Vol-Transition Mean Reversion Strategy (Att3 Final)

跨資產延伸 EEM-014 Att2 至 INDA 單一國家 EM ETF：在 INDA-005 Att3 pullback+WR
+ATR 框架上，將 2DD floor 自 -1.0% 加深至 -2.0%，過濾 shallow-2DD 失敗模式。

設計理念（Att3 最終結論）：
- INDA-005 Att3 原 2DD floor <= -1.0% 對 shallow-2DD 失敗訊號不具選擇力
- INDA-010 Att3 加深至 <= -2.0%，同時過濾：
  (a) pre-crash early-in-decline 訊號（如 2019-07-31 貿易戰 SL）
  (b) post-peak slow-melt drift 訊號（如 2025-02-18 後峰下跌 SL）
  (c) shallow 2DD near-zero expiry（如 2024-01-23 expiry, 2025-01-13 expiry）
- 結果：min(A,B) 0.23→0.30（+30%），A/B cum 差 3.22pp→0.10pp（幾乎消除）

失敗迭代記錄：
- Att1：2DD cap >= -3.0%（CIBR 方向）— min 0.08
- Att2：2DD cap >= -4.0%（放寬 CIBR 方向）— min 0.17
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.inda_010_vol_transition_mr.config import (
    INDA010Config,
    create_default_config,
)
from trading.experiments.inda_010_vol_transition_mr.signal_detector import (
    INDA010SignalDetector,
)


class INDA010Strategy(ExecutionModelStrategy):
    """INDA Post-Capitulation Vol-Transition MR (INDA-010)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return INDA010SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, INDA010Config):
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
            print(
                f"  2 日急跌下限: <= {config.drop_2d_floor:.1%}"
                "（Att3 加深 capitulation 深度要求，EEM-014 方向）"
            )
            if config.drop_2d_cap > -0.50:
                print("  2 日急跌上限: 停用（Att1/Att2 CIBR 方向失敗）")
            else:
                print(
                    f"  2 日急跌上限: >= {config.drop_2d_cap:.1%}"
                    "（排除 in-crash acceleration 進場）"
                )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
