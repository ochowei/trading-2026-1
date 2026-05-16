"""
INDA Forward-Looking Implied-Vol Regime-Gated MR 配置 (INDA-013)

動機：INDA-011 Att3（min(A,B)† Sharpe 0.55，全域最優）已透過
「2DD floor <= -2.0% + 3DD cap >= -3.0%」雙維度 capitulation-strength
過濾，將 Part A 精煉至 5 訊號 / 80.0% WR / Sharpe 0.55，但仍殘餘
1 筆 Part A 停損：
  - 2022-09-16 SL -4.10%（Fed CPI shock，3DD 淺）

Part B 為結構性零方差（2 訊號 100% WR std=0），min(A,B)† 之約束來自
Part A Sharpe 0.55。欲突破必須在「不損失 Part A winners」的前提下
移除 2022-09-16 殘餘 SL。

INDA-012（DXY direction filter）三次迭代全部 FAIL，根因明確記錄為：
「2022-09-16 SL 為 Fed CPI shock，經利率 / 風險通道傳導，**非** USD
強度通道」。INDA-013 為該根因的合理下一步驗證：以 lesson #24 family
forward-looking implied-vol regime gate 直接量測「利率通道」（^MOVE，
債券市場隱含波動率）與「風險通道」（^VIX，股票市場隱含波動率）。

lesson #24 family 跨資產脈絡（forward-looking implied vol regime gate）：
- TLT-013 ^MOVE LEVEL cap（利率直接驅動）
- XLU-013 ^MOVE 3d change DIRECTION（利率間接驅動，+112%）
- GLD-015 ^GVZ 10d DIRECTION（黃金隱含波動率，+104%）
- XBI-017 ^VIX BANDS（U-shape regime，+578% Part A）
- INDA-013 為 lesson #24 family 首次應用於「單一國家 EM 股票 ETF」

不違反 lesson #5（MR + 趨勢方向濾波）：^MOVE / ^VIX 為 exogenous
macro regime（隱含波動率軌跡），非 INDA 自身價格趨勢濾波。
不違反 lesson #14（VIX 閾值過濾 MR）：採 N 日「change / direction」
（change-based），非「level」（level-based）；lesson #24 DIRECTION
變體即為規避 level-filter 問題而生。

========================================================================
強制 PRE-ANALYSIS GATE（predict→confirm，沿用 GLD-016 / VOO-005 /
EWJ-006 / EEM-016 / TSM-012 慣例）：
========================================================================
INDA-011 Att3 baseline 各訊號 signal-day 隱含波動率診斷（絕對點數）：

  日期         結果   MOVE_lvl  MOVE3d  MOVE5d  MOVE10d  VIX_lvl  VIX3d
  2020-10-29   WIN      61.3    +2.3    +1.6    +5.7     37.6    +5.1
  2020-12-21   WIN      46.7    -0.3    -2.6    -3.0     25.2    +2.7
  2021-12-06   WIN      87.9    +4.9    -1.5   +14.5     27.2    -3.9
  2022-06-16   WIN     138.1    -1.1   +32.8   +38.8     33.0    -1.1
  2022-09-16   SL      124.9    -3.9    +3.4    -1.6     26.3    -1.0  ← 殘餘 SL
  2024-06-04(B)WIN     100.1    +9.0   +10.4   +12.0     13.2    -1.3
  2024-11-13(B)WIN     102.1    -2.0   -28.3   -29.8     14.0    -0.9

可分性分析（2022-09-16 SL vs 6 winners）：
- ^MOVE LEVEL：SL 124.9 < winner 2022-06-16 = 138.1 → CAP 不可分
- ^MOVE 3d CEILING（XLU-013 rate-shock-jump 假設）：SL 3d = -3.9 為
  「最負」（債券隱含波動率 3 日內下降，非跳升）→ ceiling 無法隔離
  SL，**rate-shock-jump 假設被資料 REFUTED**
- ^MOVE 5d/10d：SL 位於 winners 分布中段（5d +3.4 在 -2.6~+32.8 中；
  10d -1.6 在 -29.8~+38.8 中）→ 不可分
- ^VIX 全維度（level 26.3 / 1d 0.0 / 3d -1.0 / 5d +3.5 / 10d +0.7）：
  全部位於 winners 分布正中央 → 風險通道亦無區分力
- 唯一名目分離器：^MOVE 3d **FLOOR**（SL 3d = -3.9 唯一最負；所有
  winners 3d >= -2.0；可分帶寬僅 1.9 點，n=7）→ post-hoc 單點切割，
  結構機制為事後逆向（「高 MOVE level + 3d 回落 = 假平靜陷阱」），
  依 EEM-016 / lesson #6 反例 9 嚴謹標準應 REJECT

**預測：DOCUMENTED-FAILURE**。INDA 殘餘 2022-09-16 SL 為印度 idiosyncratic
Fed-shock 日，其宏觀 context 簽名（DXY 已由 INDA-012 證實、^MOVE / ^VIX
由本實驗證實）與 winners 結構性交錯，無 forward-looking implied-vol
regime gate 具區分力。INDA 加入 TSM-012 / EWJ-006 / EEM-016「idiosyncratic
non-separable residual SL」家族。

========================================================================
三次迭代（成交模型 0.1% slippage，隔日開盤市價進場，悲觀認定）：
========================================================================
[RESULTS_PLACEHOLDER — 由 run-experiment 回填]

預設配置 = Att1（^MOVE 3d ceiling <= +5.0，XLU-013 直接類比，
結構性最佳辯護變體）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA013Config(ExperimentConfig):
    """INDA-013 Forward-Looking Implied-Vol Regime-Gated MR 參數"""

    # === INDA-011 Att3 base（multi-period capitulation-strength filter）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_cap: float = -0.07
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.4
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15
    drop_2d_floor: float = -0.02
    drop_3d_cap: float = -0.03
    cooldown_days: int = 7

    # === INDA-013 新增：forward-looking implied-vol regime gate ===
    # iv_ticker  : "^MOVE"（債券隱含波動率，利率通道）或
    #              "^VIX"（股票隱含波動率，風險通道）
    # iv_lookback: N 日變動回看（點數絕對差）；0 = 使用當日 level
    # iv_mode    : "ceiling"  → 通過條件 change <= iv_threshold（過濾跳升）
    #              "floor"    → 通過條件 change >= iv_threshold（過濾驟降）
    #              "level_cap"→ 通過條件 level  <= iv_threshold
    # 三次迭代閾值（全部 FAIL / REJECT，詳見模組 docstring）：
    #   Att1 (^MOVE, 3d, ceiling, +5.0): XLU-013 rate-shock-jump 類比
    #   Att2 (^VIX , 3d, ceiling, +3.0): 風險通道
    #   Att3 (^MOVE, 3d, floor , -2.5): 唯一名目分離器（post-hoc, REJECT）
    iv_ticker: str = "^VIX"
    iv_lookback: int = 3
    iv_mode: str = "ceiling"
    iv_threshold: float = 3.0


def create_default_config() -> INDA013Config:
    """建立預設配置（Att1：^MOVE 3d ceiling <= +5.0）"""
    return INDA013Config(
        name="inda_013_implied_vol_regime_mr",
        experiment_id="INDA-013",
        display_name="INDA Implied-Vol Regime-Gated MR (^MOVE/^VIX, lesson #24)",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=15,
    )
