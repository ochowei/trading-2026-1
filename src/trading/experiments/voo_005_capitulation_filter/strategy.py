"""
VOO-005: Signal-Day Capitulation-Strength Filter Mean Reversion Strategy

在 VOO-001/002/003 baseline RSI(2)+2DD+ClosePos 框架上新增 SPY-009 已驗證的
「1 日跌幅下限 + 3 日急跌上限」雙維度過濾器，repo 首次跨資產移植 SPY-009 至
VOO（Vanguard S&P 500 ETF）。

設計理念（與 SPY-009 一致）：
- VOO 與 SPY 同追蹤 S&P 500，價格相關性 > 0.999，failure 結構應一致
- 1 日 floor 過濾「弱勢漂移弱訊號」（SPY-005 4/4 Part A SLs 訊號日 1d 過淺）
- 3 日 cap 過濾「跨夜 regime-shift 強訊號」（2025-04-07 Trump 關稅延續性下跌）
- 兩維度正交，與 DIA-012 1d cap + 3d cap 共同擴展 lesson #19 family

跨資產延伸（lesson #19 family）：
- DIA-012：1d cap + 3d cap（DJIA 30 stocks，1.0% vol）
- SPY-009：1d floor + 3d cap（S&P 500 SPDR ETF，1.0% vol）
- VOO-005（本實驗）：1d floor + 3d cap（S&P 500 Vanguard ETF，1.0% vol）

Acceptance criteria：
- ✓ Sharpe 必須 > VOO-004 Att3 baseline 1.12†
- ✓ A/B 年化 cum gap < 30%
- ✓ A/B 年化訊號比 < 50%
- ✓ 成交模型完整（next_open_market 進場、limit_order_day TP、stop_market_gtc SL）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.voo_005_capitulation_filter.config import (
    VOO005Config,
    create_default_config,
)
from trading.experiments.voo_005_capitulation_filter.signal_detector import (
    VOO005SignalDetector,
)


class VOO005Strategy(ExecutionModelStrategy):
    """VOO Signal-Day Capitulation-Strength Filter MR (VOO-005)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return VOO005SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, VOO005Config):
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
                "（VOO-005 第一維度：要求訊號日具備足夠 1d capitulation）"
            )
            if config.threeday_return_cap > -0.50:
                print(
                    f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}"
                    "（VOO-005 第二維度：排除 regime-shift 級別 3 日延續下跌）"
                )
            else:
                print("  3 日急跌上限: 停用")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
