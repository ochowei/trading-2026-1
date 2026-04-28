"""
CIBR-013: Higher-Low Structural Confirmation Mean Reversion Strategy (Att3)

核心創新：在 CIBR-008/012 BB Lower 框架上，以「多日 Higher-Low 結構」（今日 Low >
過去 N 日 Low 最小值）替代 CIBR-012 的「2DD cap」過濾「in-crash acceleration」
進場。Higher-Low 為多日 swing 維度的反轉品質確認，繞過單日 pattern（Key Reversal /
NR7 / Range Expansion）在事件驅動板塊的失敗根因。

Hypothesis：BB Lower 觸及 + 今日 Low 未破前 5 日低點 = bullish divergence at BB
lower（多日 swing 結構反轉確認），相較 CIBR-012 的 2DD cap（兩日累計報酬上限）
具備不同維度的選擇性。

迭代記錄：
- Att1：純 pullback+WR+ATR+Bullish bar+Higher-Low(3) — 過嚴 (Part A 2/0/-0.08)
- Att2：放寬 ATR + Higher-Low(5) — 仍過嚴 (Part A 3/-0.44)
- Att3：BB Lower 框架 + Higher-Low(5)（取代 CIBR-012 的 2DD cap）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_013_higher_low_confirmation_mr.config import (
    CIBR013Config,
    create_default_config,
)
from trading.experiments.cibr_013_higher_low_confirmation_mr.signal_detector import (
    CIBR013SignalDetector,
)


class CIBR013Strategy(ExecutionModelStrategy):
    """CIBR Higher-Low Structural Confirmation MR (CIBR-013)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR013SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR013Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 比率: ATR({config.atr_short_period})"
                f"/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  Higher-Low 結構: 今日 Low > min(Low[t-{config.higher_low_lookback}..t-1])")
            print(
                f"  Swing 深度: 過去 swing low <= 今日 Close * (1 - {config.swing_depth_min:.1%})"
            )
            if config.require_bullish_bar:
                print("  Bullish bar: 要求 Close > Open")
            print(f"  冷卻: {config.cooldown_days} 天")
        super()._print_strategy_params(config)
