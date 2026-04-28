"""
FCX-011: Post-Capitulation Vol-Transition Mean Reversion Strategy

**Repo 第 1 次 BB 下軌 + 回檔上限混合進場模式於高波動單一個股試驗**。
測試 XBI-010 已建立之 1.75% vol 上限是否可延伸至單一個股類別。

FCX (Freeport-McMoRan) 為銅礦龍頭單一個股，日波動 ~3%，其急跌結構
（2016 信貸、2020 COVID、2022 銅價暴跌）呈現股權資本化特性，與
商品 ETF 的宏觀重新定價（GLD-013 驗證失敗）不同。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.fcx_011_vol_transition_mr.config import (
    FCX011Config,
    create_default_config,
)
from trading.experiments.fcx_011_vol_transition_mr.signal_detector import (
    FCX011SignalDetector,
)


class FCX011Strategy(ExecutionModelStrategy):
    """FCX Post-Capitulation Vol-Transition MR (FCX-011)"""

    slippage_pct: float = 0.0015  # 0.15%（FCX 高波動個股標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return FCX011SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, FCX011Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（高波動個股崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            if config.use_twoday_filter:
                op = "<=" if config.twoday_direction == "floor" else ">="
                label = (
                    "floor (排除淺漂移)"
                    if config.twoday_direction == "floor"
                    else "cap (排除加速崩盤)"
                )
                print(f"  2 日收盤報酬 {label}: {op} {config.twoday_threshold:.1%}")
            else:
                print("  2 日收盤報酬過濾: 停用 (baseline)")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
        super()._print_strategy_params(config)
