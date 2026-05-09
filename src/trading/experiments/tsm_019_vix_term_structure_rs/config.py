"""
TSM-019: VIX Term-Structure (^VIX3M / ^VIX) Regime Gate on RS Momentum Pullback 配置

策略方向：在 TSM-011 RS 動量回調框架（含 5d return ceiling +10.5%）上加入
**^VIX3M / ^VIX 比率（VIX term structure）** 作為 forward-looking implied vol
derivative regime gate。

跨資產背景（lesson #24 family v9 候選 — repo 首次 VIX term structure 維度）：
- 既有 lesson #24 family 維度均為 implied vol LEVEL（^VIX、^MOVE、^GVZ、^OVX）
  或 DIRECTION（X 日變化），尚未驗證 term structure（^VIX3M vs ^VIX）。
- VIX3M 為 3 個月隱含波動率，VIX 為 30 天隱含波動率；
  VIX3M / VIX > 1 = contango（complacency mid-cycle）；
  VIX3M / VIX < 1 = backwardation（active panic peak）。
- TSM 為半導體 ADR 個股，受全球 risk-on/off 與半導體景氣雙驅動，
  term structure 為 macro stress 的 forward-looking 維度，
  與既有 ^VIX (LEVEL) / ^MOVE (LEVEL/DIRECTION) 正交。

設計動機：
- TSM-011 Att3 Part B Sharpe 0.83 為 binding constraint，已試 6 次 macro filter
  （TSM-013/014/015/016/017/018，Cross-asset divergence、earnings exclusion、
  ATR BAND、BB-width gate）皆失敗。
- TSM Part B 兩個殘餘 SLs（2024-07-16 / 2024-10-30）VIX3M/VIX 比率分別為
  1.130 / 1.020，前者深 contango，後者 near-flat；winners 跨整個比率範圍。
- VIX3M/VIX 為 forward-looking term structure 維度，與既有 spot VIX direction
  / level 正交，可能捕捉 Part A 與 Part B SLs 共有的「complacency mid-cycle」
  失敗結構。

迭代計畫（最多三次）：
  Att1（max_vix_term_ratio=1.15 CEILING，lenient）：
    過濾 deep contango（>1.15）訊號，TSM Part A SL 1.106/1.110 / Part B SL
    1.020/1.130 多在 1.10-1.13 範圍，CEILING 1.15 設定為 lenient threshold
    主要過濾過度 complacency（>1.15）的 winners 與 losers，淨效應視訊號分布。
  Att2（min_vix_term_ratio=1.05 FLOOR，alternative direction）：
    試「require near-contango」假設——backwardation/flat 訊號
    （ratio <= 1.05）為「mid-panic」可能延續。
  Att3（CEILING <= 1.10 + FLOOR >= 1.05 BAND，dual gate）：
    限制在「mild contango」範圍 [1.05, 1.10]，排除 deep contango
    + backwardation 雙極端。

執行模型：保留 TSM-011 Att3 全部進場（RS >= 5%、5d 回檔 3-7%、
Close > SMA(50)、5d return <= +10.5%）+ 出場（TP +8%/SL -7%/25 天）
+ cooldown 10 天 + slippage 0.1%。
"""

from dataclasses import dataclass

from trading.experiments.tsm_011_signal_day_filter.config import (
    TSMSignalDayFilterConfig,
)


@dataclass
class TSM019Config(TSMSignalDayFilterConfig):
    """TSM-019 VIX Term-Structure Regime Gate 策略專屬參數

    沿用 TSMSignalDayFilterConfig 的 RS / pullback / SMA / 5d ceiling / cooldown
    參數（TSM-011 Att3 sweet spot）。新增 VIX term structure ticker 與閾值。
    """

    # VIX term structure tickers
    vix_ticker: str = "^VIX"
    vix3m_ticker: str = "^VIX3M"

    # CEILING：VIX3M / VIX <= max_vix_term_ratio（999 視為停用）
    max_vix_term_ratio: float = 1.15  # Att1：CEILING <= 1.15 lenient

    # FLOOR：VIX3M / VIX >= min_vix_term_ratio（0 視為停用）
    min_vix_term_ratio: float = 0.0  # Att1：FLOOR 停用


def create_default_config() -> TSM019Config:
    return TSM019Config(
        name="tsm_019_vix_term_structure_rs",
        experiment_id="TSM-019",
        display_name="TSM VIX Term-Structure Regime Gate on RS Momentum",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
        # 沿用 TSM-011 Att3 sweet spot：5d ceiling +10.5%, 1d ceiling 停用
        ret_1d_max=999.0,
        ret_5d_max=0.105,
    )
