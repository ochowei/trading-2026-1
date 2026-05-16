"""
SOXL Signal-Day Capitulation-Strength CAP MR 配置 (SOXL-013)

動機：SOXL-012 Att3（BB-width regime gate）為 SOXL 全域最優 min(A,B)† 1.39，
但其 BB-width 閘門將 Part B 壓縮為 2 訊號零方差結構，A/B 累計差 52%（>30%）。
SOXL-006 capitulation MR base（回撤 [-40%,-25%] + RSI(5)<20 + 2DD≤-8%，
TP+18%/SL-12%/25d）min(A,B) 0.47（Part A 綁定）。本實驗將 lesson #19 family
「signal-day 急跌過濾」跨資產移植至 SOXL-006——但**方向經 trade-level
預分析校正為 3 日報酬 CAP（過濾 regime-shift 級別深跌），而非原假設的 1d
FLOOR**。

trade-level signal-day 預分析（2026-05-16，SOXL-006 訊號集，成交模型回測）：

  Part A signals (binding, Sharpe 0.47) — 1d / 2d / 3d / 5d 報酬：
  | Date        | Result | 1d      | 2d      | 3d       | 5d       |
  |-------------|--------|---------|---------|----------|----------|
  | 2019-05-13  | SL     | -14.12% | -13.86% | -16.93%  | -24.84%  |
  | 2019-08-05  | win    | -13.07% | -17.14% | -22.11%  | -30.11%  |
  | 2020-02-25  | SL     |  -9.18% | -22.14% | -29.13%  | -27.04%  | ★ 3d 極深
  | 2020-10-28  | win    |  -9.95% | -10.88% | -16.58%  | -17.51%  |
  | 2021-05-12  | win    | -12.39% | -11.90% | -23.83%  | -18.58%  | ← 最深贏家 3d
  | 2022-01-20  | SL     |  -9.50% | -17.85% | -28.68%  | -28.79%  | ★ 3d 極深
  | 2023-04-25  | win    |  -9.77% | -11.17% | -13.16%  | -16.35%  |
  | 2023-08-11  | Exp-L  |  -7.32% |  -8.45% | -13.57%  | -15.03%  |
  | 2023-09-21  | win    |  -5.74% | -10.34% | -12.45%  | -19.40%  |
  | 2023-10-25  | win    | -12.15% |  -8.66% | -10.04%  | -18.11%  |

  Part B signals (Sharpe 0.79)：
  | Date        | Result | 1d      | 2d      | 3d       | 5d       |
  |-------------|--------|---------|---------|----------|----------|
  | 2024-04-18  | win    |  -5.80% | -13.89% | -12.24%  | -23.78%  |
  | 2024-07-19  | SL     |  -9.02% |  -8.83% | -28.02%  | -26.49%  | ★ 3d 極深
  | 2024-09-06  | win    | -12.74% | -14.32% | -13.67%  | -28.27%  |
  | 2024-11-15  | win    |  -9.93% | -10.21% | -15.82%  | -24.71%  |
  | 2025-12-17  | Exp-W  | -11.06% | -12.55% | -13.67%  | -27.47%  |

核心預分析結論（方向校正）：

(1) **1d FLOOR 方向失敗（原假設被否決）**：Part A 最淺 1d 為贏家
    （2023-09-21 -5.74%），最深 1d 為輸家（2019-05-13 -14.12%），1d 維度
    winners/losers 完全交錯——SPY-009/VOO-005 的 1d-floor 結構**不適用於
    SOXL**（與 NVDA-017 heterogeneous SL 失敗家族同類）。

(2) **3d CAP 方向成功（單一可分失敗模式）**：3 筆深跌 SL
    （Part A 2020-02-25 -29.13% / 2022-01-20 -28.68%，Part B 2024-07-19
    -28.02%）皆 3d <= -28%，而**所有 winners**（Part A/B）3d >= -23.83%
    （最深贏家 2021-05-12）。-23.83% 與 -28.02% 之間 ~4pp 乾淨間隙
    → 失敗模式為「regime-shift 級別 3 日深跌持續下殺」（COVID 2020-02、
    2022 升息熊市、2024-07 半導體拋售），可被單一 3d cap 外科式切除。

(3) **殘餘 2 筆 Part A non-winner 不可進一步單維分離**：2019-05-13
    （sharp 1d crash，1d -14.12% 為全體最深但贏家 2019-08-05 1d -13.07%
    僅差 1pp）與 2023-08-11（shallow drift expiry，各維度最淺但贏家
    2023-09-21 1d 更淺）為異質結構——SOXL 結構性殘餘上限，符合
    SOXL-012「Part A SLs/Ws 高度重疊，單向 filter 必同時失 winners」記載。

(4) **閾值由 SL 分布決定而非 vol 線性縮放**：SPY-009/VOO-005 3d cap
    -8% @ ~1.1% vol；純 vol 縮放（~5.5x）→ -44%，但 SOXL 實際深跌 SL
    群落於 -28%、最深贏家 -23.83%，故甜蜜點為 ~-25%（lesson #19 +
    SOXL-012 BB-width 一致：閾值取決於 SLs/Ws 分布結構，不可線性對 vol 縮放）。

跨資產延伸（lesson #19 family）：
- DIA-012 Att2 ★：1d cap >= -2.0% AND 3d cap >= -7%（DJIA，1.0% vol，1d 過深）
- SPY-009 / VOO-005 Att2 ★：1d FLOOR <= -0.5% AND 3d cap >= -8%
  （S&P 500，1.0% vol，1d 過淺）
- SOXL-013：**3d cap only**（3x 槓桿半導體，~6% vol，深 3d regime-shift）
  —— repo 首次於 leveraged 3x 板塊 ETF 驗證 lesson #19，並首次記錄
  「1d-floor 方向跨資產失敗 / 3d-cap 方向成功」之方向校正案例。

========================================================================
三次迭代記錄（2026-05-16，成交模型 0.1% slippage，隔日開盤市價進場）：
見 EXPERIMENTS_SOXL.md。Att1 3d cap -25%；Att2 robustness（-27% / -23%）；
Att3 sweet-spot 定案 / ablation。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SOXL013Config(ExperimentConfig):
    """SOXL-013 Signal-Day Capitulation-Strength CAP MR 參數"""

    # SOXL-006 capitulation MR base 參數（同 SOXL-006）
    drawdown_lookback: int = 20
    drawdown_threshold: float = -0.25  # 回撤下限 -25%
    drawdown_cap: float = -0.40  # 回撤上限 -40%（過濾極端崩盤）
    rsi_period: int = 5  # lesson #27：SOXL 必須 RSI(5)，不可 RSI(2)
    rsi_threshold: float = 20.0
    drop_2d_threshold: float = -0.08  # 2 日跌幅 ≤ -8%

    # SOXL-013 新增：3 日報酬 CAP（lesson #19 family，方向經預分析校正）
    # 訊號日 3 日累計報酬必須 >= cap（不可深於上限 = 排除 regime-shift 深跌）
    # Att1/Att3 ★ -0.25；Att2 robustness -0.27 / -0.23
    threeday_return_cap: float = -0.25

    # 訊號冷卻（同 SOXL-006）
    cooldown_days: int = 7

    # 成交模型參數
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> SOXL013Config:
    """建立預設 SOXL-013 配置（Att3 ★ 定案：3d cap -25%）"""
    return SOXL013Config(
        name="soxl_013_signal_day_capitulation_cap",
        experiment_id="SOXL-013",
        display_name="SOXL Signal-Day Capitulation-Strength CAP MR",
        tickers=["SOXL"],
        data_start="2019-01-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,  # +18%（SOXL 硬上限，lesson #41）
        stop_loss=-0.12,  # -12%（SOXL 硬上限，lesson #41）
        holding_days=25,
    )
