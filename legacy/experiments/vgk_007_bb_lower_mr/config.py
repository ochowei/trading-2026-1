"""
VGK-007: BB Lower Band Mean Reversion (Hybrid Entry)

移植 EWJ-003 Att3 的混合進場模式到 VGK。VGK 日波動 1.12%，與 EWJ 1.15% 幾乎相同，
皆為非美已開發市場 ETF。目的：改善 VGK-004 Att1 的 A/B 累積差距（37.5% 相對）。

VGK-004 Att1: 固定回檔 3-7% + WR + ClosePos + ATR>1.15 → Part A 0.45 / Part B 1.07
  - A/B 累積報酬差距 10.32pp（37.5% 相對），Part B 2024-2025 缺乏深回檔訊號。
VGK-003 Att2: 固定回檔≥3%（無上限） + 同上品質過濾 → Part A 0.42 / Part B 1.07
  - A/B 累積差 0.49pp（平衡優秀），但 Sharpe 稍低。

假設：BB 下軌是統計自適應門檻，Part A 高波動時 BB 下軌深，Part B 低波動時 BB 下軌淺，
自動縮放與資產當期波動一致。搭配固定 -7% 回檔上限隔離極端崩盤，應能同時
改善 Sharpe 並保持 A/B 平衡。

Att1★: BB(20,2.0) + 回檔上限 7% + WR + ClosePos + ATR>1.15 + cooldown 7 + TP+3.5%/SL-4.0%/20d
  直接移植 EWJ-003 Att3 架構（相同波動度 1.12-1.15%）。
  → Part A 0.53 (WR 77.8%, 9訊號, +14.05%) / Part B 0.78 (WR 85.7%, 7訊號, +15.31%)
  → min(A,B) 0.53（vs VGK-003 Att2 的 0.42，+26%；vs VGK-004 Att1 的 0.45，+18%）
  → A/B 累積差 1.26pp（8.2% 相對），訊號比 1.29:1，皆遠優於 VGK-004 Att1 的 37.5%
  → 成功關鍵：BB 下軌是統計自適應門檻，Part B 低波動期門檻自動變淺，捕捉有效訊號

Att2: BB(20,1.5) 放寬下軌 → Part A 0.70 / Part B 0.50
  - Part A 更佳但 A/B 累積差距擴大至 34.8%（>30% 門檻），失敗原因：Part A 多出 2023
    歐洲銀行業危機/2022 QT 高報酬訊號，Part B 低波動期放寬 BB 反引入品質較差訊號
Att3: BB(20,1.8) 中間值 → Part A 0.62 / Part B 0.41
  - 介於 Att1/Att2 之間但兩端都不如，A/B 累積差 41.3% 失敗
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK007Config(ExperimentConfig):
    """VGK-007 BB 下軌均值回歸參數"""

    # BB 參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（10日高點回檔上限，過濾 COVID 等極端事件）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07  # 回檔上限 7%（~6σ for 1.12% vol, lesson #13）

    # 品質過濾（同 VGK-003/004 驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    cooldown_days: int = 7


def create_default_config() -> VGK007Config:
    return VGK007Config(
        name="vgk_007_bb_lower_mr",
        experiment_id="VGK-007",
        display_name="VGK BB Lower Band Mean Reversion",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（VGK TP 硬上限）
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
