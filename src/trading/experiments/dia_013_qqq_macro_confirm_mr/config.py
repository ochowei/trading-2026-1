"""
DIA QQQ Macro-Confirmation Gate MR 配置 (DIA-013)

策略方向（Strategy Direction）：
    在 DIA-012 Att2（Capitulation-Depth Filter MR，min(A,B)† 1.31，DIA 全域
    最佳）基礎上，疊加 **QQQ 10 日報酬作為跨資產宏觀確認閘門**（直接移植
    IWM-015 Att1 ★ SUCCESS，min(A,B) 2.80），要求 NASDAQ-100（broad-market
    risk-off 代理）已進入 confirmed correction 才放行 DIA capitulation 訊號。

    repo 中較少使用的方向：cross-asset macro-context confirmation（非 pair
    trading / 非 RS 動量）。IWM-015 已證明此閘門對小型股 idiosyncratic
    capitulation 高效（IWM Russell 2000 個股事件加總雜訊 → QQQ 確認過濾孤立
    小型股急殺）。DIA-013 為「QQQ macro-confirmation gate 是否能由小型股
    idiosyncratic ETF（IWM）推廣至大型股寬基指數 ETF（DIA）」的邊界測試。

================================================================================
基準：DIA-012 Att2（已執行驗證，2026-04-24 全域最優，2026-05-17 live 重跑確認）
  Part A: 12 訊號 91.7% WR Sharpe **1.31** cum +32.47%（殘存 1 筆 SL）
  Part B: 3 訊號 100% WR std=0 Sharpe 0.00（採 EWJ-003 慣例以 Part A 為 min）
  Part C: 2 訊號 50% WR Sharpe -0.09
  min(A,B)†: **1.31**
  唯一殘存 Part A 綁定 SL = 2022-01-18（2022 Fed 升息開端 value-vs-growth
  輪動，DIA 淺幅磨跌：1d -1.47% / 2d -2.03%（最淺）/ 3d -2.51% / 5d -1.92%）

================================================================================
TRADE-LEVEL 預分析（2026-05-17，pre-analysis gate FIRST，依 winning playbook）

  DIA-012 Att2 全 15 筆訊號的 signal-day 跨資產維度（yfinance auto_adjust）：

  PART A（綁定；SL = 2022-01-18）
  | Date       | Res | QQQ10d | QQQ5d | Rel10d(DIA-QQQ) | VIXlvl | MOVE3dΔ |
  |------------|-----|--------|-------|-----------------|--------|---------|
  | 2020-09-21 | TP  |  -5.67 | -2.78 |          +2.23  |  27.8  |   -3.8  |
  | 2021-09-20 | TP  |  -4.05 | -2.72 |          +0.09  |  25.7  |   +5.7  |
  | 2022-09-23 | TP  | -10.12 | -4.60 |          +2.17  |  29.9  |   +2.6  |
  | 2020-01-27 | TP  |  -0.15 | -2.36 |          -0.80  |  18.2  |  +15.4  |
  | 2022-01-18 | SL  |  -7.75 | -2.52 |          +4.51  |  22.8  |  +10.1  | ★殘存SL
  | 2021-12-20 | TP  |  -1.30 | -2.83 |          +0.48  |  22.9  |   +3.0  |
  | 2020-02-28 | TP  | -12.04 |-10.63 |          -1.38  |  40.1  |  +22.3  |
  | 2019-12-03 | TP  |  -0.82 | -1.38 |          -0.88  |  16.0  |   +7.0  |
  | 2022-12-16 | TP  |  -6.26 | -2.76 |          +1.90  |  22.6  |  -21.4  |
  | 2019-05-29 | TP  |  -2.50 | -3.19 |          +0.97  |  17.9  |   +2.1  |
  | 2023-05-04 | EXP |  -0.03 | -1.30 |          -1.87  |  20.1  |  +12.5  |
  | 2022-06-14 | TP  | -10.50 |-10.96 |          +2.66  |  32.7  |  +38.8  |

  PART B（3/3 TP，std=0，非綁定）
  | 2024-05-30 | TP  |  -0.30 | -0.91 |          -4.02  |  14.5  |   +7.5  |
  | 2024-08-02 | TP  |  -5.57 | -3.07 |          +4.13  |  23.4  |  +11.8  |
  | 2025-08-01 | TP  |  -1.31 | -2.21 |          -0.39  |  20.4  |   -1.2  |

  分離性判讀：
  - **QQQ 10d（IWM-015 macro-confirmation 維度）：SL 2022-01-18 = -7.75%**，
    完全 interleaved 於 winners（-12.04 / -10.50 / -10.12 / -6.26 更深；
    -5.67 / -4.05 / -2.50 / -1.30 / -0.82 / -0.15 / -0.03 較淺）。IWM-015 閘門
    `QQQ_10d <= -1.5%`（要求 QQQ 已 broad correction）會 **放行 SL**
    （-7.75 ≤ -1.5：2022-01 Fed 科技股崩跌使 QQQ 深跌，閘門「確認」此 SL 為
    broad risk-off 並保留），反而 **過濾掉 4 筆淺跌 winners**
    （2020-01-27 -0.15 / 2021-12-20 -1.30 / 2019-12-03 -0.82 /
    2023-05-04 EXP -0.03，均 > -1.5%）→ 方向性反轉。
  - Rel10d（DIA−QQQ divergence）：SL +4.51 為 Part A 唯一最大值，但 Part B
    winner 2024-08-02 = +4.13（僅差 0.38pp）→ knife-edge 單點 notch，不符
    robust ≥2pt plateau（CIBR-016 Att2 / INDA-013 Att3 REJECT 先例）；且
    DIA−QQQ 為 positive-ρ value/growth style spread，非 driver-pure
    single-factor inverse → cross-asset divergence regime gate family v4
    failure class（SIVR-019/EWT-010 規則），非有效 family target。
  - ^VIX level/3d、^MOVE 3dΔ：SL 與 winners 全 interleaved（^MOVE +10.1
    低於 COVID winners +22.3 與 2022-06-14 +38.8）→ 不可分離（lesson #24
    condition-(c) idiosyncratic isomorph）。

  **預測：DOCUMENTED-FAILURE。** DIA 為大型股寬基指數 ETF，其 RSI(2)
  capitulation dips 與 QQQ 高度同向（ρ_DIA,QQQ ≈ 0.85-0.9），dips 本身即
  broad-market dips；殘存 SL 2022-01-18 正是 QQQ 深跌期事件（value-vs-growth
  輪動的 Fed-onset 淺磨）。IWM-015 閘門依賴 base asset 帶有「非 broad」的
  idiosyncratic dip 雜訊（小型股）才有區分力；大型股寬基 DIA 無此雜訊可濾，
  閘門非區分性 / 反轉（lesson #36 + macro-confirmation family 邊界）。

================================================================================
三次迭代記錄（2026-05-17，成交模型 0.1% slippage，隔日開盤市價進場）
  共同 base = DIA-012 Att2（RSI(2)<10 + 2DD≥1.5% + ClosePos≥40% +
  1d cap≥-2.0% + 3d cap≥-7%，TP+3.0%/SL-3.5%/25d，cooldown 5d）
  新機制 = QQQ 10d 報酬 <= macro_max_return（IWM-015 macro-confirmation gate）

  [Att1] macro_max_return = -0.015（IWM-015 Att1 ★ canonical 直接移植）
  [Att2] macro_max_return = -0.005（放寬確認門檻，方向/穩健性探針）
  [Att3] macro_max_return = -0.030（IWM-015 documented over-filter 點，嚴格端）
  （結果與失敗分析見各 commit message 與 EXPERIMENTS_DIA.md）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA013Config(ExperimentConfig):
    """DIA-013 QQQ Macro-Confirmation Gate MR 參數"""

    # ── DIA-012 Att2 base 進場參數（未動）──
    rsi_period: int = 2
    rsi_threshold: float = 10.0
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%
    close_position_threshold: float = 0.4
    oneday_return_cap: float = -0.020  # 1 日急跌上限 >= -2.0%
    threeday_return_cap: float = -0.07  # 3 日急跌上限 >= -7%
    cooldown_days: int = 5

    # ── DIA-013 新增：QQQ 跨資產宏觀確認閘門（移植 IWM-015）──
    macro_ticker: str = "QQQ"
    macro_lookback: int = 10
    # Att1 -0.015（IWM-015 canonical，documented primary）/ Att2 -0.005 / Att3 -0.030
    # 三次迭代全 FAIL（documented-failure）；config 保留 Att1 canonical 值供文件對照
    macro_max_return: float = -0.015


def create_default_config() -> DIA013Config:
    return DIA013Config(
        name="dia_013_qqq_macro_confirm_mr",
        experiment_id="DIA-013",
        display_name="DIA QQQ Macro-Confirmation Gate MR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 DIA-012）
        stop_loss=-0.035,  # -3.5%（同 DIA-012）
        holding_days=25,  # 25 天（同 DIA-012）
    )
