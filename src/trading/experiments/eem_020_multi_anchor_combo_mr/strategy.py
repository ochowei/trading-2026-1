"""
EEM-020: Multi-Anchor (^VIX CAP + EEM-FXI CEILING) Combined Filter on Vol-Transition MR

在 EEM-014 Att2 框架（min(A,B) 0.56）之上**異質維度 AND chain 組合**：
  (a) ^VIX 收盤 <= vix_max_level（implied vol LEVEL CAP）
  (b) EEM 10d 報酬 - FXI 10d 報酬 <= max_rel_return（cross-asset divergence CEILING）

設計依據：EEM-019 揭示 Part A/B SLs 在 EEM-FXI divergence 維度結構性反向，
單一 threshold 無法雙 Part 同步改善；本實驗以**第二異質維度（VIX）**分工解決：
  - Part A 殘餘 SL 2021-07-08 DiDi → CEILING binding（FXI 重挫深於 EEM）
  - Part B 殘餘 SL 2025-11-19 美中貿易 → CAP binding（VIX 23.66 高 panic）

預期效果（待驗證）：
- 過濾 2021-07-08 + 2025-11-19 雙 SLs 同時保留多數 winners
- Part A Sharpe 0.73 → 1.0+，Part B Sharpe 0.56 → 1.0+

風險：雙重 AND chain 易過嚴 → 訊號數崩壞 + 統計顯著性損失。
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.eem_020_multi_anchor_combo_mr.config import (
    EEM020Config,
    create_default_config,
)
from trading.experiments.eem_020_multi_anchor_combo_mr.signal_detector import (
    EEM020MultiAnchorComboDetector,
)


class EEM020Strategy(ExecutionModelStrategy):
    """EEM-020: Multi-Anchor (^VIX CAP + EEM-FXI CEILING) Combined Filter on Vol-Transition MR"""

    slippage_pct: float = 0.001

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return EEM020MultiAnchorComboDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, EEM020Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(f"  回檔上限: {config.pullback_lookback}日高點回檔 >= {config.pullback_cap:.0%}")
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_position_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_short_period})/ATR({config.atr_long_period})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  2 日急跌下限: <= {config.twoday_return_floor:.1%}")
            print(f"  ^VIX LEVEL CAP: VIX_Close <= {config.vix_max_level:.1f}")
            print(
                f"  EEM-{config.fxi_ticker} CEILING: {config.rel_lookback}日報酬差"
                f" <= {config.max_rel_return:+.2%}"
            )
            print(f"  冷卻天數: {config.cooldown_days} 天")
        super()._print_strategy_params(config)
