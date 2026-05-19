"""
TSLA-020: TSLA-USD(UUP) Direction Regime-Gated BB Squeeze Breakout 策略

人類 artifact 提示方向（empty remote `tsla_018_dxy_direction_breakout`）：
USD/DXY direction regime gate。本實驗在 TSLA-017 Att3 全域最優框架上
疊加 GLD-016 Att1 已證明之 USD(UUP) 20d regime gate family 形式。
predict→confirm pre-analysis（先做）預測 documented-failure：綁定
Part B SL 2024-09-23 於 USD（及所有正交）維度與 TP winners 完全
interleaved，TSLA 非 USD-driver-pure（事件驅動 SLs）。含成交模型。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.tsla_020_usd_regime_breakout.config import (
    TSLA020Config,
    create_default_config,
)
from trading.experiments.tsla_020_usd_regime_breakout.signal_detector import (
    TSLA020USDRegimeBreakoutDetector,
)


class TSLA020USDRegimeBreakoutStrategy(ExecutionModelStrategy):
    """TSLA-020: TSLA-QQQ divergence + USD(UUP) regime gate + BB Squeeze breakout"""

    slippage_pct: float = 0.0015

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return TSLA020USDRegimeBreakoutDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, TSLA020Config):
            print(f"  BB 參數 (Bollinger Bands): BB({config.bb_period}, {config.bb_std})")
            print(
                f"  擠壓條件 (Squeeze): {config.bb_squeeze_percentile_window}日"
                f" {config.bb_squeeze_percentile:.0%} 百分位，"
                f"{config.bb_squeeze_recent_days}日內"
            )
            print(f"  趨勢確認 (Trend): Close > SMA({config.sma_trend_period})")
            print(
                f"  趨勢 regime: SMA({config.sma_regime_short})"
                f" ≥ {config.sma_regime_ratio_min}"
                f" × SMA({config.sma_regime_long})"
            )
            print(
                f"  TSLA-{config.benchmark_ticker} 背離 regime: "
                f"{config.divergence_lookback}d 報酬差 ≥ {config.min_relative_return:+.2%}"
            )
            if config.use_usd_ceiling:
                print(
                    f"  USD regime CEILING: {config.usd_benchmark}"
                    f" {config.usd_lookback}d return ≤ {config.max_usd_return:+.2%}"
                )
            if config.use_usd_divergence_floor:
                print(
                    f"  USD 相對背離 FLOOR: TSLA−{config.usd_benchmark}"
                    f" {config.usd_lookback}d ≥ {config.min_tsla_minus_usd:+.2%}"
                )
            print(f"  冷卻期 (Cooldown): {config.cooldown_days} 交易日")
        super()._print_strategy_params(config)
