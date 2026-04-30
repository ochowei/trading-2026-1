"""
CIBR-014: Multi-Period Capitulation-Strength Filter MR Strategy

在 CIBR-008（前任最佳，min(A,B) 0.39）框架上新增「1 日急跌上限 + 3 日急跌上限」
雙維度過濾器，排除兩類延續性下跌：
- 1d <= -3%：單日 news/policy-driven 急跌
- 3d <= -7%：跨夜 regime-shift 級別 3 日延續下跌

設計理念：
- CIBR-012 採 2DD cap 單維度過濾於 -4% 邊界，對 CIBR 1.53% vol 資料 jitter 敏感
- DIA-012 雙維度（1d -2.0% + 3d -7%）成功打破 1d / 3d 邊界穩定性問題
- CIBR vol ≈ 1.5x DIA → 1d cap 縮放至 -3.0%；3d cap 維持 -7%（CIBR 較大波動需較寬）
- 兩維度正交：1d 維度過濾單日急跌，3d 維度過濾跨夜延續性下跌

跨資產延伸（lesson #19 family Multi-Period 版本）：
- DIA-012 (1.0% vol)：1d cap -2.0% + 3d cap -7%
- SPY-009 (1.0% vol)：1d floor -0.5% + 3d cap -8%
- INDA-011 (0.97% vol)：1d floor + 3d cap
- CIBR-014 (1.53% vol)：1d cap -3.0% + 3d cap -7.0%（首次商業驅動板塊 ETF 雙維度試驗）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.cibr_014_multi_period_capitulation_mr.config import (
    CIBR014Config,
    create_default_config,
)
from trading.experiments.cibr_014_multi_period_capitulation_mr.signal_detector import (
    CIBR014SignalDetector,
)


class CIBR014Strategy(ExecutionModelStrategy):
    """CIBR Multi-Period Capitulation-Strength Filter MR (CIBR-014)"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return CIBR014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, CIBR014Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" <= {abs(config.pullback_cap):.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(
                f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}"
                "（CIBR-014 第一維度：排除單日 news/policy 延續性下跌）"
            )
            print(
                f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}"
                "（CIBR-014 第二維度：排除 regime-shift 級別 3 日延續下跌）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
