"""
CIBR-014: Multi-Period Capitulation-Strength Filter MR Strategy
（Att2：1d return cap + ATR ratio BAND）

在 CIBR-008（前任最佳，min(A,B) 0.39）框架上新增雙維度過濾：
- Return 維度：1d cap >= -3.0%（過濾 2020-02-24 COVID 級單日急跌）
- Vol-regime 維度：ATR(5)/ATR(20) BAND ∈ [1.15, 1.40]（過濾 2021-02-26
  in-crash 加速級訊號，ATR ratio 1.5065）

設計理念：
- CIBR-012 Att3 採 2DD cap 對邊界 jitter 敏感，更新資料後 Part A 退化為 zero-var
- CIBR-014 Att1（1d cap + 3d cap）DIA-012 跨資產移植 → 3d cap 對 CIBR 數據集
  完全非綁定（所有訊號 3d > -5.42%），無法區分 2021-02-26 SL 與 TPs
- Trade-level ATR(5)/ATR(20) 分析發現 2021-02-26 = 1.5065，遠高於其他 7 訊號
  範圍 1.16~1.31。新增 ATR ratio CEILING <= 1.40 精準過濾此 SL 而保留所有 TP
- 「ATR ratio > 1.15 即足夠」傳統認知被推翻：過高 ATR ratio（>1.40）反而標誌
  in-crash 加速階段（vs 1.15-1.40 為 panic 過後 settling 階段）

跨資產延伸（lesson #19 family + lesson #22 vol-regime cross-product）：
- DIA-012 (1.0% vol): 1d cap -2.0% + 3d cap -7%（return-only 雙維度）
- SPY-009 (1.0% vol): 1d floor -0.5% + 3d cap -8%
- INDA-011 (0.97% vol): 1d floor + 3d cap
- CIBR-014 Att2 (1.53% vol): **1d cap + ATR ratio BAND** — repo 首次
  return-based 維度與 vol-regime 維度結合作為 MR 進場過濾，發現「ATR ratio 過高
  反而標誌 in-crash」的對稱失敗模式（lesson #15 邊界擴展）
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
                f"  ATR ratio BAND: ATR({config.atr_fast})/ATR({config.atr_slow})"
                f" ∈ ({config.atr_ratio_threshold}, {config.atr_ratio_ceiling}]"
                "（FLOOR 過濾慢磨下跌、CEILING 過濾 in-crash 加速）"
            )
            print(
                f"  1 日急跌上限: >= {config.oneday_return_cap:.1%}"
                "（CIBR-014 第一維度：排除單日 news/policy 延續性下跌）"
            )
            print(f"  冷卻天數 (Cooldown): {config.cooldown_days} 天")
            print("  追蹤停損 (Trailing Stop): 無 (Disabled)")
        super()._print_strategy_params(config)
