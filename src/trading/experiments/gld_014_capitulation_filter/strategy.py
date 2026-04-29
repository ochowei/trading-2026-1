"""
GLD-014: Signal-Day Capitulation-Strength Filter Mean Reversion Strategy

在 GLD-012 Att3（min(A,B) Sharpe 0.48，GLD 全域最佳）框架上新增「2 日累計跌幅
下限」過濾器，移除「淺幅漂移」型失敗訊號。

設計理念：
- GLD-012 Part A 9 筆失敗交易中，4 筆訊號日 2d_ret > -0.5%（淺幅漂移）
- 商品 ETF（GLD）在 macro 驅動下跌中常產生「停滯回檔但無 capitulation 動能」
  訊號（如 2019-09-11 +0.61% / 2020-11-11 -0.10% / 2023-08-14 -0.30% 2d）
- 2d floor 要求訊號日具備足夠單兩日 capitulation 強度，過濾這類訊號
- Part B 12/13 winners 之 2d <= -1.27%，2d floor <= -0.5% 僅誤殺 1 筆
  （2024-06-04 2d -0.01%）

跨資產延伸（lesson #19 family）：
- USO-013：2d floor 加深，2.20% vol 商品 ETF（OIL macro 驅動）
- EEM-014：2d floor <= -0.5%，1.17% vol broad EM ETF
- INDA-010：2d floor <= -2.0%，0.97% vol single-country EM ETF
- VGK-008：2d floor <= -2.0%，1.12% vol European broad ETF
- EWJ-005：1d floor <= -0.5%，1.15% vol developed Asia ETF
- EWT-009：2d floor <= -1.5%，1.41% vol semiconductor EM ETF
- IBIT-009：2d floor <= -3.0%，3.17% vol crypto ETF
- **GLD-014（本實驗）：1.12% vol commodity ETF，repo 第 7 次「2d floor」嘗試
  + 第一個 macro-driven 商品 ETF 試驗**

對照失敗案例（GLD-013）：
- GLD-013 在 BB(20,2) 下軌 + ATR + 回檔上限框架疊加 2d floor，三次失敗
- 失敗根因：BB 下軌進場後 SL 分布跨所有 2DD 深度（macro repricing）
- 本實驗回到 GLD-012 框架（pullback + WR + ClosePos），2d floor 應有更精準
  的「淺漂移」過濾力（對應 4 筆 Part A 失敗訊號集中於 2d > -0.5%）
"""

from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.execution_strategy import ExecutionModelStrategy
from trading.experiments.gld_014_capitulation_filter.config import (
    GLD014Config,
    create_default_config,
)
from trading.experiments.gld_014_capitulation_filter.signal_detector import (
    GLD014SignalDetector,
)


class GLD014Strategy(ExecutionModelStrategy):
    """GLD Signal-Day Capitulation-Strength Filter MR (GLD-014)"""

    slippage_pct: float = 0.001  # 0.1%（ETF 標準滑價）

    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return GLD014SignalDetector(create_default_config())

    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, GLD014Config):
            print(
                f"  回檔條件 (Pullback): {config.pullback_lookback} 日高點回檔"
                f" ≥ {abs(config.pullback_threshold):.1%}"
            )
            print(f"  Williams %R: WR({config.wr_period}) ≤ {config.wr_threshold}")
            print(
                f"  收盤位置 (Close Position): ≥ {config.close_position_threshold:.0%} of day range"
            )
            print(
                f"  2 日跌幅下限 (2d Floor): <= {config.twoday_return_floor:.1%}"
                "（GLD-014 capitulation strength）"
            )
            if config.oneday_return_floor > -0.50:
                print(
                    f"  1 日跌幅下限 (1d Floor): <= {config.oneday_return_floor:.1%}"
                    "（GLD-014 Att2 cooldown-shift safety）"
                )
            else:
                print("  1 日跌幅下限: 停用（Att1 baseline）")
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
