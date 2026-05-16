"""
DIA-015 ^VIX Forward-Looking Implied-Vol DIRECTION Regime-Gated MR 配置

策略方向（lesson #24 family — forward-looking implied volatility DIRECTION
regime gate，repo 首次應用於低波動美國寬基指數 ETF）：
  在 DIA-012 Att2（min(A,B)† 1.31）的 RSI(2)+2DD+ClosePos+1d cap+3d cap MR
  框架上，新增第六條件：**^VIX N 日點變化 <= max_vix_change（CEILING）**。

動機（lesson #24 跨資產移植假設）：
  lesson #24 forward-looking implied vol DIRECTION regime gate 已於 TLT-013/
  TLT-017（^MOVE）、XLU-013（^MOVE 3d change）、GLD-015（^GVZ）、USO-025/028
  （^OVX）成功——「vol regime trajectory（rising = duration/safety shock）」
  為 backward-looking 飽和後的下一維度。本實驗測試 ^VIX DIRECTION 是否能
  surgical 移除 DIA-012 殘餘 Part A SL 2022-01-18（Fed 升息熊市起點）。

trade-level signal-day ^VIX N 日點變化 pre-analysis（DIA-005 全 SL/TP 集）：

  | date       | tag | VIX  | chg3  | chg5  |
  |------------|-----|------|-------|-------|
  | 2020-10-26 | SL  | 32.5 | +3.81 | +3.28 |
  | 2021-11-26 | SL  | 28.6 | +9.45 | +11.03|
  | 2022-01-18 | SL  | 22.8 | +5.17 | +3.39 |
  | 2025-04-07 | SL  | 47.0 | +25.47| +24.70|
  | 2020-02-28 | TP  | 40.1 | +12.26| +23.03| ← 贏家 chg3/chg5 遠高於多數 SL
  | 2021-09-20 | TP  | 25.7 | +7.53 | +6.34 |
  | 2022-06-14 | TP  | 32.7 | +6.60 | +8.67 |
  | 2024-08-02 | TP  | 23.4 | +5.70 | +7.00 |

  **預期結構性失敗**：DIA RSI(2) capitulation MR 進場本質發生於 VIX-rising
  fear episodes，winners（V-bounce）與 losers（regime-shift 延續）在 ^VIX
  DIRECTION 維度完全重疊，無 surgical separator——任何 CEILING 移除 SL
  必同時移除多個 high-VIX-rise winners（2020-02-28 chg3 +12.26 / 2021-09-20
  +7.53 / 2022-06-14 +6.60），與 lesson #14（VIX 在熊市持續偏高）、lesson #36
  （極端超賣時市場同步，無區分力）一致。

  本實驗目的為**建立 lesson #24 family 失敗邊界**：forward-looking implied
  vol DIRECTION 於低波動美國寬基指數 capitulation MR 結構性失效（鏡像
  NVDA-018 為 lesson #24 family 首次失敗：高 vol 個股 + MBPC）。

跨資產脈絡（lesson #24 family）：
- TLT-013/TLT-017 ✓（^MOVE LEVEL/DIRECTION，rate ETF + MR）
- XLU-013 ✓（^MOVE 3d change DIRECTION，rate-indirect defensive ETF + MR）
- GLD-015 ✓（^GVZ，commodity safe-haven + MR）
- USO-025/028 ✓（^OVX DIRECTION，commodity event-driven + MR）
- NVDA-018 ✗（^VXN，high-vol AI 個股 + MBPC，lesson #24 首次失敗）
- **DIA-015（本實驗）：^VIX DIRECTION，低波動美國寬基指數 ETF + MR，
  預期 lesson #24 family 第 2 次失敗 + 首次於 broad equity index 類別**

迭代計畫：
- Att1：vix_lookback=3, max_vix_change=+4.0（CEILING，aggressive）
- Att2：vix_lookback=5, max_vix_change=+5.0（替代窗口）
- Att3：ablation / 確認結構性非可分

驗收目標（goal）：min(A,B) Sharpe > DIA-012 Att2 1.31†；A/B cum gap < 30%；
signal gap < 50%；必須使用成交模型（execution model）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA015Config(ExperimentConfig):
    """DIA-015 ^VIX DIRECTION Regime-Gated MR 參數"""

    # === MR 進場框架（完全沿用 DIA-012 Att2 當前進場基線）===
    rsi_period: int = 2
    rsi_threshold: float = 10.0
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%
    close_position_threshold: float = 0.4
    oneday_return_cap: float = -0.020  # 1 日急跌上限 >= -2.0%
    threeday_return_cap: float = -0.07  # 3 日急跌上限 >= -7%
    cooldown_days: int = 5

    # === DIA-015 核心新增：^VIX forward-looking implied vol DIRECTION CEILING ===
    vix_ticker: str = "^VIX"
    # lookback：N 日 ^VIX 點變化窗口
    vix_lookback: int = 3
    # CEILING：^VIX(t) - ^VIX(t-N) <= max_vix_change（點變化，仿 XLU-013 ^MOVE
    # 3d change <= +5.0 的 absolute-point DIRECTION 維度）
    # Att1 +4.0 / Att2 +5.0(5d) / Att3 ablation
    max_vix_change: float = 4.0


def create_default_config() -> DIA015Config:
    return DIA015Config(
        name="dia_015_vix_direction_mr",
        experiment_id="DIA-015",
        display_name="DIA ^VIX DIRECTION Regime-Gated MR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 DIA-012）
        stop_loss=-0.035,  # -3.5%（同 DIA-012）
        holding_days=25,  # 25 天（同 DIA-012）
    )
