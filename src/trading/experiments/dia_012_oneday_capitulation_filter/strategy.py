"""
DIA-012: Capitulation-Depth Filter Mean Reversion Strategy

在 DIA-005（min(A,B) Sharpe 0.47，DIA 全域最佳）框架上新增「1 日急跌上限 +
3 日急跌上限」雙維度過濾器，排除兩類延續性下跌：
- 1d ≤ -2%：news/policy-driven 單日深度急跌
- 3d ≤ -7%：regime-shift 級別 3 日深度急跌

設計理念：
- DIA 為低波動寬基 ETF（1.0% 日波動），深度急跌（單日或多日）通常反映新聞/
  政策驅動的延續性下跌而非 capitulation；溫和下跌伴隨 RSI(2)<10 更代表
  「正常 MR 機會」
- DIA-005 Part A 三筆 SL 中兩筆為深 1d 急跌（2020-10-26、2021-11-26），由
  1d cap 精準過濾
- DIA-005 Part B 唯一 SL（2025-04-07 Trump 關稅）為「shallow 1d + deep 3d」
  結構（隔夜消息延續），由 3d cap 精準過濾
- 兩類過濾正交：1d 維度過濾單日 news shock，3d 維度過濾跨夜 regime-shift

跨資產延伸（lesson #19 family）：
- CIBR-012：2DD cap（深 2 日急跌過濾，1.53% vol）
- EEM-014：2DD floor（淺 2 日漂移過濾，1.17% vol）
- INDA-010：2DD floor 加深（0.97% vol）
- DIA-012：**1d cap + 3d cap 雙維度**（repo 首次，1.0% vol 寬基 ETF）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.dia_012_oneday_capitulation_filter.config import (
    DIA012Config,
    create_default_config,
)
from trading.experiments.dia_012_oneday_capitulation_filter.signal_detector import (
    DIA012SignalDetector,
)


class DIA012Strategy(ExecutionModelStrategy):
    """DIA Capitulation-Depth Filter MR (DIA-012)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return DIA012SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, DIA012Config):
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
                f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}"
                "（DIA-012 第一維度：排除單日 news/policy-driven 延續性下跌）"
            )
            if config.threeday_return_cap > -0.50:
                print(
                    f"  3 日急跌上限: >= {config.threeday_return_cap:.1%}"
                    "（DIA-012 第二維度：排除 regime-shift 級別 3 日延續下跌）"
                )
            else:
                print("  3 日急跌上限: 停用（Att1 baseline）")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
