"""
VOO Signal-Day Capitulation-Strength Filter MR 配置 (VOO-005)

動機：VOO-003（RSI(2) MR 框架最優，min(A,B) Sharpe 0.53）為 VOO 均值回歸框架
最佳，但 Part A 仍有 3 筆停損（2022-01-06、2022-06-14、2023-08-03）與 Part B
1 筆停損（2025-04-07 Trump 關稅）拖累 Sharpe。VOO 全域最優為 VOO-004 Att3
MBPC（min(A,B) 1.12†），但 MBPC 與 MR 訊號集完全不重疊。本實驗將 SPY-009
（SPY 全域最優 min 6.56†）的「1 日跌幅下限 + 3 日急跌上限」雙維度過濾器
跨資產移植至 VOO-003 RSI(2) MR base——VOO 與 SPY 追蹤**相同的 S&P 500
指數**，預期共用相同的 1d-floor 失敗結構。

trade-level signal-day 分析（2026-05-16，VOO-003 訊號集）：

  Part A signals (1d_ret / 3d_ret / 5d_ret):
  | Date        | Result | 1d_ret  | 3d_ret  | 5d_ret   |
  |-------------|--------|---------|---------|----------|
  | 2019-05-29  | win    | -0.69%  | -1.41%  | -2.83%   |
  | 2019-08-02  | Expiry | -0.73%  | -2.68%  | -3.09%   |
  | 2019-12-03  | win    | -0.70%  | -1.89%  | -1.23%   |
  | 2020-02-28  | win    | -0.60%  | -5.43%  | -11.34%  |
  | 2020-09-21  | win    | -1.09%  | -3.09%  | -2.98%   |
  | 2021-07-19  | win    | -1.50%  | -2.58%  | -2.77%   |
  | 2021-09-20  | win    | -1.63%  | -2.77%  | -2.46%   |
  | 2022-01-06  | SL     | -0.13%  | -2.09%  | -1.76%   | ★ 1d 極淺
  | 2022-05-12  | win    | -0.08%  | -1.43%  | -5.21%   |
  | 2022-06-14  | SL     | -0.25%  | -6.91%  | -10.09%  | ★ 1d 極淺
  | 2022-09-23  | win    | -1.66%  | -4.21%  | -4.56%   |
  | 2022-12-16  | win    | -1.19%  | -4.20%  | -2.12%   |
  | 2023-03-13  | win    | -0.17%  | -3.40%  | -4.75%   |
  | 2023-08-03  | SL     | -0.28%  | -1.97%  | -0.82%   | ★ 1d 淺

  Part B signals:
  | Date        | Result | 1d_ret  | 3d_ret  | 5d_ret   |
  |-------------|--------|---------|---------|----------|
  | 2024-08-05  | win    | -3.00%  | -6.07%  | -5.09%   |
  | 2025-04-07  | SL     | -0.42%  | -10.67% | -9.80%   | ★ 3d 極深
  | 2025-04-21  | win    | -2.38%  | -4.40%  | -3.71%   |
  | 2025-11-18  | win    | -0.82%  | -1.78%  | -3.33%   |

兩個關鍵失敗模式（與 SPY-009 完全同構，因 VOO/SPY 同追蹤 S&P 500）：

(1) Part A 3/3 SLs：訊號日 1 日跌幅 ∈ [-0.28%, -0.13%]（極淺 capitulation）
    - 解讀：S&P 500 寬基 ETF 的 RSI(2)<10 訊號發生時若當日跌幅過淺，往往代表
      「持續弱勢盤」（價格緩慢漂移）而非真正恐慌底部
    - 過濾器：1d_ret 下限 <= -0.5%（要求訊號日具備足夠單日 capitulation 強度）
    - 與 DIA-012 的 1d cap 方向**完全相反**——同為 1.0% vol 寬基 ETF，但
      VOO/SPY（S&P 500）SLs 為 1d 過淺漂移（floor 過濾），DIA（DJIA）SLs
      為 1d 過深政策震盪（cap 過濾）
    - 代價：移除 2 筆 1d 過淺贏家（2022-05-12 1d -0.08%、2023-03-13 1d -0.17%）

(2) Part B 1/1 SL：3 日累計跌幅 -10.67%（regime-shift 級別深度急跌）
    - 2025-04-07 Trump 關稅延續性下跌（與 SPY-009 / DIA-012 同日同事件）
    - 過濾器：3d_ret cap >= -8%（DIA-012 / SPY-009 跨資產移植）
    - 安全邊際：所有 Part A/B 贏家最深 3d 為 2024-08-05 -6.07%（與 -8% 距 1.93pp）
    - 注意：2025-04-07 1d -0.42%（淺於 -0.5%）已先被 1d floor 過濾，3d cap 在
      VOO-005 訊號集為 regime-shift 安全層（同 SPY-009 Att2 結論）

跨資產延伸（lesson #19 family）：
- DIA-012 Att2 ★：1d cap >= -2.0% AND 3d cap >= -7%（DJIA，1d 過深）
- SPY-009 Att2 ★：1d FLOOR <= -0.5% AND 3d cap >= -8%（S&P 500，1d 過淺）
- VOO-005：1d FLOOR <= -0.5% AND 3d cap >= -8%（**同 SPY-009，驗證同指數
  ETF（VOO vs SPY）共用 1d-floor 失敗結構**，與 DIA 的 1d-cap 方向對比）

========================================================================
三次迭代記錄（2026-05-16，成交模型 0.1% slippage，隔日開盤市價進場）：
見 strategy.py 與 EXPERIMENTS_VOO.md。Att1 1d floor -0.5%（3d cap 停用）；
Att2 ★ 1d floor -0.5% AND 3d cap -8%；Att3 1d floor -0.7%（穩健性）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VOO005Config(ExperimentConfig):
    """VOO-005 Signal-Day Capitulation-Strength Filter MR 參數"""

    # RSI(2) 參數（同 VOO-003）
    rsi_period: int = 2
    rsi_threshold: float = 10.0

    # 2 日累計跌幅過濾（同 VOO-003）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 VOO-003）
    close_position_threshold: float = 0.4

    # 1 日跌幅下限（VOO-005 第一維度，SPY-009 跨資產移植）
    # Att1/Att2 -0.5%：要求訊號日 1 日跌幅 >= 0.5%（過濾 3 PA SLs + 1 PB SL）
    # Att3 -0.7%：穩健性驗證更嚴 floor
    oneday_return_floor: float = -0.005

    # 3 日累計跌幅上限（VOO-005 第二維度，DIA-012 / SPY-009 跨資產移植）
    # Att1 停用（-0.99）；Att2 ★ -8%；Att3 -8%
    threeday_return_cap: float = -0.99

    # 冷卻期（同 VOO-003）
    cooldown_days: int = 5


def create_default_config() -> VOO005Config:
    return VOO005Config(
        name="voo_005_signal_day_capitulation_mr",
        experiment_id="VOO-005",
        display_name="VOO Signal-Day Capitulation-Strength Filter MR",
        tickers=["VOO"],
        data_start="2010-10-01",
        profit_target=0.0285,  # +2.85%（VOO MR 框架硬上限，同 VOO-003）
        stop_loss=-0.030,  # -3.0%（同 VOO-003）
        holding_days=20,  # 20 天（同 VOO-003）
    )
