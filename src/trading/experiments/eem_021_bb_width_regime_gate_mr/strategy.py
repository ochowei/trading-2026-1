"""
EEM-021: BB-Width Regime Gate on Vol-Transition MR

在 EEM-014 Att2 框架（min(A,B) 0.56）之上疊加 BB(20,2) 寬度 / Close 比率作為
volatility regime classifier：

  訊號通過條件：BB_Width_Ratio < max_bb_width_ratio
  （CAP 方向，排除 vol expansion regime；可改 FLOOR 方向作 Att3 反向測試）

設計依據（lesson #23 cross-asset extension）：
- 既有成功：TLT-007（0.05）/ TQQQ-018（0.48）/ SOXL-012（0.43）皆為「單一極端
  vol regime episode」資產
- EEM-021 為 repo 第 4 次跨資產試驗、首次 broad EM ETF 驗證
- EEM 1.17% vol 預期閾值 ~ 0.05-0.12 區間

預期效果（待驗證）：
- 過濾 EEM-014 Att2 殘餘 2021-07-08 + 2025-11-19 SLs（若位於 vol expansion regime）
- Part A Sharpe 0.73 → 1.0+，Part B Sharpe 0.56 → 1.0+

風險：BB-width 與 ATR(5)/ATR(20)>1.10 部分重疊（皆衡量 vol expansion），可能冗餘 →
無新選擇力；多 regime 結構可能使閾值無甜蜜點（同 EEM-018 BANDS 結構失敗）。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_021_bb_width_regime_gate_mr.config import (
    EEM021Config,
    create_default_config,
)
from trading.experiments.eem_021_bb_width_regime_gate_mr.signal_detector import (
    EEM021BBWidthRegimeDetector,
)


class EEM021Strategy(ExecutionModelStrategy):
    """EEM-021: BB-Width Regime Gate on Vol-Transition MR"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM021BBWidthRegimeDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM021Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(f"  回檔上限: {config.pullback_lookback}日高點回檔 >= {config.pullback_cap:.0%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日急跌下限: <= {config.twoday_return_floor:.1%}")
            if config.use_bb_width_floor:
                print(
                    f"  BB-Width Regime Gate: BB_Width_Ratio > {config.bb_width_floor:.3f}（FLOOR）"
                )
            else:
                print(
                    f"  BB-Width Regime Gate: BB_Width_Ratio < {config.max_bb_width_ratio:.3f}（CAP）"
                )
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)
