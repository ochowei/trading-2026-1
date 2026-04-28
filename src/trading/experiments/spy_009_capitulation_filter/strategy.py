"""
SPY-009: Signal-Day Capitulation-Strength Filter Mean Reversion Strategy

在 SPY-005（min(A,B) Sharpe 0.53，SPY 全域最佳）框架上新增「1 日跌幅下限 +
3 日急跌上限」雙維度過濾器。**repo 首次將「1 日跌幅下限」作為主品質過濾器**
試驗（DIA-012 為 1d cap 上限，方向完全相反）。

設計理念：
- SPY 與 DIA 雖均為 1.0% vol 寬基 ETF 且使用相同 RSI(2) 進場框架，但 SLs 在
  1d 維度的失敗結構完全相反——SPY SLs 為 1d 過淺的弱勢漂移（floor 過濾），
  DIA SLs 為 1d 過深的政策震盪（cap 過濾）
- SPY-005 4/4 Part A SLs 訊號日 1d <= -0.30%，與贏家可區分（贏家最淺
  2023-03-13 -0.14%、2020-02-28 -0.42%）
- SPY-005 唯一 Part B SL（2025-04-07 Trump 關稅）為 3d -10.65% regime-shift，
  與 DIA-005 同日同事件
- 1d floor 與 3d cap 兩維度正交：1d 維度過濾「弱勢漂移弱訊號」，3d 維度過濾
  「跨夜 regime-shift 強訊號」

跨資產延伸（lesson #19 family）：
- CIBR-012：2DD cap（深 2 日急跌過濾，1.53% vol）
- EEM-014：2DD floor（淺 2 日漂移過濾，1.17% vol）
- INDA-010：2DD floor 加深（0.97% vol）
- DIA-012：**1d cap + 3d cap** 雙維度（repo 首次 1d/3d 雙維度，1.0% vol）
- SPY-009：**1d floor + 3d cap** 雙維度（**repo 首次 1d floor 方向**，1.0% vol）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.spy_009_capitulation_filter.config import (
    SPY009Config,
    create_default_config,
)
from trading.experiments.spy_009_capitulation_filter.signal_detector import (
    SPY009SignalDetector,
)


class SPY009Strategy(ExecutionModelStrategy):
    """SPY Signal-Day Capitulation-Strength Filter MR (SPY-009)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return SPY009SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, SPY009Config):
            print(f"  RSI 期數: {config.rsi_period}")
            print(f"  RSI 門檻: < {config.rsi_threshold}")
            print(
                f"  2 日跌幅門檻: >= {abs(config.decline_threshold):.1%}"
                f" ({config.decline_lookback} 日)"
            )
            print(
                f"  收盤位置 (Close Position): >= {config.close_position_threshold:.0%}"
                " of day range"
            )
            print(
                f"  1 日跌幅下限: <= {config.oneday_return_floor:.1%}"
                "（SPY-009 第一維度：要求訊號日具備足夠 1d capitulation）"
            )
            if config.threeday_return_cap > -0.50:
                print(
                    f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}"
                    "（SPY-009 第二維度：排除 regime-shift 級別 3 日延續下跌）"
                )
            else:
                print("  3 日急跌上限: 停用（Att1 baseline）")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
