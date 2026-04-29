"""
IWM-012: BB Lower Band + Pullback Cap Hybrid Mean Reversion Strategy

cross-asset port from CIBR-008 / EWJ-003 / VGK-007 / EWT-008 / EWZ-006 /
EEM-012 successful BB-lower hybrid pattern。Repo 首次將此模式應用至小型股
寬基 ETF（IWM）。

設計理念：
- BB(20, 2.0) 下軌觸及 = 統計自適應深度進場（隨波動率自動縮放）
- 10日高點回檔上限 = 絕對崩盤隔離（過濾 BB 在持續崩盤中外擴失去選擇性的問題）
- WR(10) <= -80 + ClosePos >= 40% = 超賣 + 日內反轉確認
- ATR(5)/ATR(20) > 1.10 = 波動率飆升過濾（IWM-011 Att2 已驗證甜蜜點）

混合進場模式有效 vol 邊界 [1.12%, 1.75%]：
- VGK 1.12% (min 0.53)、EEM 1.17% (min 0.34)、EWT 1.41% (min 0.57†)、
  CIBR 1.53% (min 0.39，CIBR-012 進一步至 0.49)、EWZ 1.75% (min 0.69，BB 1.5σ)
- IWM 1.5-2% vol 為邊界中段，CIBR 1.53% 已驗證有效

跨資產延伸（lesson #16 / #52 family）：
- 小型股寬基 ETF（IWM）首次測試
- 與美寬基（SPY/DIA）使用 RSI(2) 框架不同，IWM 1.5-2% vol 較高，可能更適合
  BB-lower 統計自適應進場
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.iwm_012_bb_lower_pullback_cap.config import (
    IWM012Config,
    create_default_config,
)
from trading.experiments.iwm_012_bb_lower_pullback_cap.signal_detector import (
    IWM012SignalDetector,
)


class IWM012Strategy(ExecutionModelStrategy):
    """IWM BB 下軌 + 回檔上限混合進場 (IWM-012)"""

    slippage_pct: float = 0.001  # 0.1%（高流動性 ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return IWM012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, IWM012Config):
            print(f"  Bollinger Bands: BB({config.bb_period}, {config.bb_std}) 下軌觸及")
            print(
                f"  回檔上限: {config.pullback_lookback}日高點回檔"
                f" >= {config.pullback_cap:.0%}（崩盤隔離）"
            )
            print(f"  Williams %R: WR({config.wr_period}) <= {config.wr_threshold}")
            print(f"  Close Position: >= {config.close_pos_threshold:.0%}")
            print(
                f"  ATR 過濾: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" > {config.atr_ratio_threshold}"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
