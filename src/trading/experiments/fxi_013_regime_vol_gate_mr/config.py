"""
FXI Volatility-Regime-Gated Mean Reversion 配置 (FXI-013)

實驗動機：
- FXI-005 Att3 為當前最佳（Part A Sharpe 0.38 / Part B Sharpe 1.61 / min 0.38），
  但 A/B Sharpe 差距 1.23（極度不對稱）。Part A（2019-2023）WR 65.4%、
  Part B（2024-2025）WR 80%，原因在於 Part A 含 2019 貿易戰 + 2020 COVID
  + 2021 監管衝擊 + 2022 防疫政策 + 2023 弱勢復甦等五段結構性高波動 regime，
  均值回歸訊號大量觸發但品質低。
- FXI-007 (RS)、FXI-008 (Stoch)、FXI-009 (Failed Breakdown)、FXI-010 (Gap-Down)、
  FXI-011 (CRSI)、FXI-012 (Momentum Continuation) 共 6 次實驗 18 attempts
  均試圖改變進場機制皆失敗（lesson #52 整理）。核心問題不是進場機制，而是
  「政策驅動期 regime 無法以短期 price-action / oscillator 區分」。

嘗試方向（repo 首次應用於 FXI）：**波動率 regime 閘門（Volatility Regime Gate）**。
移植自 TLT-007 Att2 成功（2026-04-22 驗證 TLT min(A,B) 由 -0.20 轉正至 0.12）。
核心思想：
- FXI 2022 監管衝擊 + 2020 COVID 期間波動率飆升，BB(20, 2) 通道寬度相對價格
  常超過 10-12%（正常期通常 5-8%）
- 將 BB 寬度 / Close < 閾值 作為 regime 過濾器，可一次性排除整個高波動期間的
  訊號，保留政策穩定期的 MR 機會
- 這是 regime filter（市場狀態）而非 short-term trend filter（進場日趨勢），
  不違反 lesson #5（MR + 趨勢過濾 = 災難，主要指進場日短線趨勢）

與 lesson #5、#52 的區分：
- Lesson #5：均值回歸 + 進場日短線方向過濾（Close>SMA 類）會濾掉下跌中進場的好訊號
- Lesson #52：政策驅動 EM 的所有 short-term reversal 結構皆無效（BB 下軌、Stoch、
  failed breakdown、gap-down 等）
- 本實驗：BB width 為「整體波動率環境」分類器，不改變進場機制，僅在 crisis regime
  壓制訊號。此為 TLT-007 驗證的成功結構，測試是否泛化至政策驅動單一國家 EM ETF

設計理念（執行模型同 FXI-005）：
- 保留 FXI-005 Att3 完整進場條件（pullback 5-12% + WR(10)≤-80 + ClosePos≥40% +
  ATR(5)/ATR(20)>1.05）
- 加入 BB(20, 2) 寬度 / Close < 閾值的 calm regime 閘門（新增）
- 出場沿用 FXI-005 Att3 驗證的 TP+5.5% / SL-5.0% / 20 天 / cd10
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI013Config(ExperimentConfig):
    """FXI-013 Volatility-Regime-Gated Mean Reversion 參數

    迭代紀錄見 __init__.py 註記；最終配置由最佳 Attempt 決定。
    """

    # 回檔範圍進場（同 FXI-005）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # 回檔 >= 5%
    pullback_cap: float = -0.12  # 回檔 <= 12%（COVID / 監管期隔離）

    # Williams %R（同 FXI-005）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置（同 FXI-005）
    close_position_threshold: float = 0.4

    # ATR 波動率過濾（同 FXI-005）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # 波動率 regime 閘門（新增）：BB(bb_period, bb_std) 寬度 / Close < max_bb_width_ratio
    # FXI ~2.0% vol 為 TLT ~1.0% vol 的 2 倍，故預期需要較 TLT 寬鬆的門檻
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.10  # Att3 採中間值 10% 搭配動態 regime 百分位過濾

    # 動態 regime 百分位閘門（Att3 新增）：BB 寬度必須位於 252 日回看期的
    # 前 bb_width_pct_threshold 分位以下（即在相對安靜的 regime 中）。
    # 這讓門檻隨 regime 自動調整——crisis 期 median 升高時即使固定 10% 門檻也
    # 過關的訊號仍可能被過濾（因相對於 252 日仍屬高波動 regime）
    use_bb_width_percentile: bool = True
    bb_width_percentile_lookback: int = 252  # 1 交易年
    bb_width_percentile_threshold: float = 0.5  # 需在過去 252 日 BB 寬度的前 50% 分位內

    # 冷卻期（同 FXI-005）
    cooldown_days: int = 10


def create_default_config() -> FXI013Config:
    return FXI013Config(
        name="fxi_013_regime_vol_gate_mr",
        experiment_id="FXI-013",
        display_name="FXI Volatility-Regime-Gated MR",
        tickers=["FXI"],
        data_start="2010-01-01",  # 需要足夠歷史讓 BB(20) 與 SMA 暖機
        profit_target=0.055,  # +5.5%（同 FXI-005）
        stop_loss=-0.050,  # -5.0%（同 FXI-005）
        holding_days=20,
    )
