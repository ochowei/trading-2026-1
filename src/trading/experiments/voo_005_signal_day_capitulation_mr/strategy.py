"""
VOO-005: Signal-Day Capitulation-Strength Filter Mean Reversion Strategy

在 VOO-003（RSI(2) MR 框架最優 min(A,B) Sharpe 0.53）框架上新增「1 日跌幅
下限 + 3 日急跌上限」雙維度過濾器。SPY-009（SPY 全域最優 min 6.56†）跨資產
移植——VOO 與 SPY 追蹤**相同的 S&P 500 指數**。

設計理念：
- VOO/SPY（S&P 500）與 DIA（DJIA）雖均為 1.0% vol 寬基 ETF 且使用相同 RSI(2)
  進場框架，但 SLs 在 1d 維度的失敗結構完全相反——VOO/SPY SLs 為 1d 過淺的
  弱勢漂移（floor 過濾），DIA SLs 為 1d 過深的政策震盪（cap 過濾）
- VOO-003 3/3 Part A SLs 訊號日 1d ∈ [-0.28%, -0.13%]，與多數贏家可區分
  （贏家 1d 多深於 -0.6%；僅 2022-05-12 -0.08%、2023-03-13 -0.17% 為淺贏家）
- VOO-003 唯一 Part B SL（2025-04-07 Trump 關稅）為 3d -10.67% regime-shift，
  與 SPY-009 / DIA-012 同日同事件
- 1d floor 與 3d cap 兩維度正交：1d 維度過濾「弱勢漂移弱訊號」，3d 維度過濾
  「跨夜 regime-shift 強訊號」

跨資產延伸（lesson #19 family）：
- CIBR-012：2DD cap（深 2 日急跌過濾，1.53% vol）
- EEM-014：2DD floor（淺 2 日漂移過濾，1.17% vol）
- DIA-012：**1d cap + 3d cap** 雙維度（DJIA，1.0% vol，1d 過深）
- SPY-009：**1d floor + 3d cap** 雙維度（S&P 500，1.0% vol，1d 過淺）
- VOO-005：**1d floor + 3d cap** 雙維度（**同 SPY-009**，驗證**同指數 ETF
  共用失敗結構**——VOO 與 SPY 同追蹤 S&P 500，與 DIA（DJIA）方向對比，
  擴展 lesson #19「同 vol ≠ 同失敗模式；同指數 = 同失敗模式」子規則）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.voo_005_signal_day_capitulation_mr.config import (
    VOO005Config,
    create_default_config,
)
from trading.experiments.voo_005_signal_day_capitulation_mr.signal_detector import (
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
                print("  3 日急跌上限: 停用（Att1 baseline）")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
