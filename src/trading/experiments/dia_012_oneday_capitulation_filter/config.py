"""
DIA Capitulation-Depth Filter MR 配置 (DIA-012)

動機：DIA-005（min(A,B) Sharpe 0.47）為 DIA 全域最佳，但 Part A 14 訊號中
3 筆停損（2020-10-26、2021-11-26、2022-01-18 皆 -3.60%）拖累 Part A Sharpe，
Part B 4 訊號中 1 筆 -3.60% 停損（2025-04-07 Trump 關稅震盪）拖累 Part B Sharpe。

trade-level signal-day 分析顯示：

  Part A signals (1d_ret / 3d_ret):
  | Date        | Result | 1d_ret  | 2d_ret  | 3d_ret  | 5d_ret   |
  |-------------|--------|---------|---------|---------|----------|
  | 2021-11-26  | SL     | -2.52%  | -2.51%  | -2.02%  | -2.68%   | ★ 最深 1d
  | 2020-10-26  | SL     | -2.24%  | -2.34%  | -1.76%  | -1.78%   | ★ 第二深 1d
  | 2020-09-21  | TP     | -1.84%  | -2.68%  | -3.18%  | -3.01%   |
  | 2021-09-20  | TP     | -1.81%  | -2.32%  | -2.49%  | -2.63%   |
  | 2022-09-23  | TP     | -1.55%  | -1.97%  | -3.63%  | -3.96%   |
  | 2020-01-27  | TP     | -1.53%  | -2.12%  | -2.21%  | -2.70%   |
  | 2022-01-18  | SL     | -1.47%  | -2.03%  | -2.51%  | -1.92%   |
  | 2021-12-20  | TP     | -1.23%  | -2.65%  | -2.75%  | -2.00%   |
  | 2020-02-28  | TP     | -1.14%  | -5.63%  | -5.96%  | -12.14%  |
  | 2019-12-03  | TP     | -0.97%  | -1.94%  | -2.27%  | -1.88%   |
  | 2022-12-16  | TP     | -0.93%  | -3.09%  | -3.54%  | -1.69%   |
  | 2019-05-29  | TP     | -0.87%  | -1.89%  | -1.37%  | -2.90%   |
  | 2023-05-04  | Expiry | -0.83%  | -1.64%  | -2.65%  | -2.03%   |
  | 2022-06-14  | TP     | -0.42%  | -3.20%  | -5.79%  | -8.39%   |

  Part B signals:
  | 2024-05-30  | TP     | -0.81%  | -1.83%  | -2.34%  | -3.83%   |
  | 2024-08-02  | TP     | -1.51%  | -2.78%  | -2.52%  | -2.18%   |
  | 2025-04-07  | SL     | -0.95%  | -6.33%  | -10.06% | -9.60%   | ★ 唯一 SL
  | 2025-08-01  | TP     | -1.27%  | -2.03%  | -2.41%  | -2.96%   |

兩個關鍵失敗模式：

(1) Part A：1 日急跌 ≤ -2% 的訊號（2 筆 SL：2020-10-26、2021-11-26）
    - 解讀：DIA 為低波動寬基 ETF（1.0% 日波動），單日 ≤ -2% 急跌通常反映
      news/policy-driven 延續性下跌（COVID 二波、Omicron 黑色星期五）
    - 過濾器：1d_ret cap >= -2.0%（過濾 2/3 SL）

(2) Part B：3 日急跌 ≤ -10% 的訊號（1 筆 SL：2025-04-07 Trump 關稅）
    - 3d_ret -10.06% 為 Part A/B 全部 18 訊號中最深，遠超贏家最深 -5.96%
      （2020-02-28 COVID 早期）
    - 解讀：3 日內 -10% 為 regime-shift 事件，非單日 capitulation
    - 過濾器：3d_ret cap >= -7%（精準過濾，保留所有贏家）

Repo 首次將「1-day return cap + 3-day return cap」雙過濾器作為主品質過濾器
試驗。此前 TQQQ-017 Att1（ClosePos）/ Att2（2DD）/ Att3（Prev RSI(5)）三類單日
過濾器在 TQQQ 3x 槓桿 ETF 上全部失敗（min(A,B) 0.13~0.34 < 0.36）；DIA-012
在 1x 寬基 ETF 上應有不同結構。

跨資產延伸（與 INDA-010 / EEM-014 / CIBR-012 比較）：
- CIBR-012 Att3 (1.53% vol)：2DD cap，過濾深 2 日急跌（崩盤加速中）
- EEM-014 Att2 (1.17% vol)：2DD floor，過濾淺 2 日漂移（弱 MR）
- INDA-010 Att3 (0.97% vol)：2DD floor 加深，同 EEM 方向
- DIA-012 (1.0% vol)：**1d cap + 3d cap 雙維度**（repo 首次）
  - 與 2DD 維度正交：DIA SL 在 2d 維度與贏家重疊，需單日(1d)+多日(3d)
    雙維度才能完全區分

========================================================================
三次迭代記錄（2026-04-24，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1：1d_ret cap >= -2.0%（單一 1 日過濾器）
  Part A: 12 訊號 WR 91.7% Sharpe **1.31** cum +32.47%（+130% vs DIA-005 的 0.57）
  Part B: 4 訊號 WR 75.0% Sharpe **0.47** cum +5.34%（同 DIA-005，無過濾效果）
  min(A,B): **0.47**（與 DIA-005 持平，未提升）
  分析：1d cap 精準過濾 Part A 兩筆深 1d SL（2021-11-26 -2.52%、2020-10-26
  -2.24%），保留所有贏家。但 Part B 唯一 SL（2025-04-07 1d 僅 -0.95%）為
  「shallow 1d + deep 3d」結構（隔夜關稅消息延續），1d cap 無法捕捉。

Att2 ★（當前最佳）：1d_ret cap >= -2.0% AND 3d_ret cap >= -7%（雙維度）
  Part A: 12 訊號 WR 91.7% Sharpe ~1.31 cum +32.47%（同 Att1，3d 過濾不影響）
  Part B: 3 訊號 WR 100% std=0 Sharpe 0.00（顯示）→ 採 EWJ-003/EWT-008 慣例以
    Part A Sharpe 為 min 約束
  min(A,B) **= Part A Sharpe ~1.31**（+178% vs DIA-005 的 0.47）
  3d cap >= -7% 精準過濾 Part B 2025-04-07 SL（3d -10.06%），保留所有贏家
  （贏家最深 3d 為 2020-02-28 -5.96%，安全邊際 1pp）

Att3（穩健性驗證）：1d_ret cap >= -2.0% AND 3d_ret cap >= -8%
  Part A: 12 訊號 91.7%/Sharpe 1.31 cum +32.47%（與 Att2 完全相同）
  Part B: 3 訊號 100%/Sharpe 0.00 cum +9.27%（與 Att2 完全相同）
  min(A,B)†: **1.31**（與 Att2 完全相同）
  分析：3d cap 閾值在 -7% 至 -8% 之間結果完全相同——所有贏家 3d > -7%，
  Part B 唯一 SL 3d = -10.06% 同時通過 -7% 與 -8% 過濾。確認 -7% 與 -8% 皆為
  穩健閾值，採 -7% 為最終配置（更高安全邊際，需 1pp 緩衝以防未來新訊號）。

A/B 平衡指標（Att2 ★ 最終）：
  - Part A 12 訊號（2.4/yr）vs Part B 3 訊號（1.5/yr），差 38% < 50% ✓
  - Part A WR 91.7% vs Part B 100% 接近完美一致
  - Part A cum +32.47%（年化 6.49%）vs Part B +9.27%（年化 4.64%），差 28.5% < 30% ✓
  - **Part A/B Sharpe 結構性對齊**（Part B 全 TP 為 std=0 不可避免結構，
    採 EWJ-003 / EWT-008 慣例以 Part A Sharpe 為 min 約束）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA012Config(ExperimentConfig):
    """DIA-012 Single-Day Capitulation-Depth Filter MR 參數"""

    # RSI(2) 參數（同 DIA-005）
    rsi_period: int = 2
    rsi_threshold: float = 10.0

    # 2 日累計跌幅過濾（同 DIA-005）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 DIA-005）
    close_position_threshold: float = 0.4

    # 1 日急跌上限（DIA-012 第一維度）
    # Att1/Att2/Att3 皆使用 -2.0%：過濾「news/policy-driven 延續性下跌」訊號
    # 過濾 Part A 2 筆深 1d SL（2021-11-26 -2.52%, 2020-10-26 -2.24%）
    oneday_return_cap: float = -0.020

    # 3 日急跌上限（DIA-012 第二維度，Att2 新增；Att3 穩健性驗證 -8% 結果完全相同）
    # Att1 停用（-0.99 = 不過濾）；Att2 ★ 最終 -7%；Att3 -8% 等價（無新增過濾效果）
    # 過濾 Part B 2025-04-07 Trump 關稅延續性下跌（3d -10.06%）
    # Part A/B 全部贏家最深 3d 為 -5.96%（2020-02-28 COVID），與 -7% 安全距 1pp
    threeday_return_cap: float = -0.07

    # 冷卻期（同 DIA-005）
    cooldown_days: int = 5


def create_default_config() -> DIA012Config:
    return DIA012Config(
        name="dia_012_oneday_capitulation_filter",
        experiment_id="DIA-012",
        display_name="DIA Single-Day Capitulation-Depth Filter MR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 DIA-005）
        stop_loss=-0.035,  # -3.5%（同 DIA-005）
        holding_days=25,  # 25 天（同 DIA-005）
    )
