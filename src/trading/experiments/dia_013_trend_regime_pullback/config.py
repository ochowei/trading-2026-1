"""
DIA-013: Strict-Bull-Regime Trend Pullback Continuation

策略方向：趨勢跟蹤（trend following）— repo 中 DIA 較少使用的方向。

實驗動機 (Problem statement)：
- DIA 當前全域最優 DIA-012 Att2（capitulation-MR）採 Part B std=0 慣例：
  Part A 12 訊號 / Sharpe 1.31 / cum +32.47%，Part B **僅 3 訊號** /
  100% WR / std=0 / cum +9.27%。A/B 累積差 71%、訊號差 75%，嚴重違反
  平衡目標（gap < 30% / siggap < 50%）。根因：MR（買急跌）在 2024-2025
  乾淨多頭 Part B 嚴重訊號飢渴。
- 既有趨勢跟蹤 DIA-007（golden-cross + Low 觸 SMA50 反彈）呈**相反**
  失衡：Part B Sharpe **1.07**（強）但 Part A 僅 **0.29**（弱）。
  Part A 弱因 2020 COVID 崩盤 + 2022 熊市期間「SMA50 跌破反彈」假訊號
  （falling knife）——彼時 SMA50>SMA200 短暫成立但 secular 趨勢已破。

策略假設：
- DIA（道瓊 30 藍籌寬基）長期乾淨上升，趨勢跟蹤 continuation 在兩段
  上升期皆觸發 → 結構性修復 MR 的 Part B 訊號飢渴。
- 加上**嚴格 secular 多頭 regime 閘門**（Close > SMA(200) 且 SMA(50) >
  SMA(200) 且 SMA(200) 20 日斜率向上）可切除 2020/2022 falling-knife
  假訊號（彼時 Close < SMA200 或 SMA200 走平/下彎），提升 Part A
  Sharpe 同時保留 DIA-007 已驗證的 Part B 強勢。
- 進場加入 close-up 轉折確認（今日收高於昨日），避免在仍下墜中接刀。
- 此為趨勢跟蹤而非 MR，lesson #5「趨勢濾波器 + MR = 災難」不適用。

進場條件（全部滿足，訊號日 T，執行模型於 T+1 開盤進場）：
1. Secular 多頭 regime：Close > SMA(200) 且 SMA(50) > SMA(200) 且
   SMA(200) 較 20 日前上升
2. 上升中溫和回檔：Close 自 10 日高點回檔 ∈ [-6%, -1.5%]
3. 回檔轉折確認：今日 Close > 昨日 Close
4. 冷卻期 10 個交易日

出場（執行模型，滑價 0.1%）：
- 沿用 DIA 已驗證甜蜜點 TP +3.0% / SL -3.5% / 最長持倉 25 天
  （DIA-005/007/012 一致），先隔離進場 regime 濾波的邊際貢獻。
- DIA ~1.0-1.2% 日波動，lesson #2：低波動可用 trailing 但本實驗先用
  固定 TP/SL 以隔離變數。

迭代規劃（最多 3 次）：
- Att1：上述基線
- Att2：依結果調整（regime 嚴格度 / 回檔帶 / SMA200 斜率視窗 / 出場）
- Att3：甜蜜點收斂

跨資產貢獻：
- repo 首次於 DIA 建立「嚴格 secular 多頭 regime + 趨勢回檔 continuation」
  框架；若 SUCCESS → 驗證趨勢跟蹤可解寬基指數 capitulation-MR 的
  Part B 訊號飢渴結構性失衡。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA013Config(ExperimentConfig):
    """DIA-013 Strict-Bull-Regime Trend Pullback Continuation 參數"""

    # Secular 多頭 regime
    sma_fast_period: int = 50
    sma_slow_period: int = 200
    sma_slow_slope_lookback: int = 20
    require_sma_slow_rising: bool = True
    require_close_above_slow: bool = True

    # 回檔模式
    # Att1: 10 日高點回檔帶（過多低品質訊號，Part A Sharpe 0.14）
    # Att2: 改為「Low 觸及/跌破 SMA(50) 支撐」(dia_007 風格，support-anchored，
    #       更少更高品質) + 嚴格 regime + 轉折確認
    pullback_mode: str = "sma50_support"  # "high_pullback" | "sma50_support"
    pullback_lookback: int = 10
    pullback_min: float = -0.06
    pullback_max: float = -0.015
    # sma50_support 模式：Low <= SMA(50) * (1 + proximity_pct)
    sma50_proximity_pct: float = 0.01

    # 回檔轉折確認
    require_close_up: bool = True

    # Att3：波動率 regime 閘門（lesson #23 風格）— 僅在「平靜上升」regime
    # 交易，切除 2020 COVID 崩盤 / 2022 熊市的高波動環境（趨勢跟蹤於此死亡）
    use_vol_regime_gate: bool = True
    atr_period: int = 14
    max_atr_pct: float = 0.015  # ATR(14)/Close <= 1.5%（DIA 平靜 ~1%，崩盤 >2.5%）

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> DIA013Config:
    return DIA013Config(
        name="dia_013_trend_regime_pullback",
        experiment_id="DIA-013",
        display_name="DIA Strict-Bull-Regime Trend Pullback Continuation",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=25,
    )
