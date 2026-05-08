"""
VOO Signal-Day Capitulation-Strength Filter MR 配置 (VOO-005)

動機：VOO-003（min(A,B) Sharpe 0.53）為 VOO 早期 MR 全域最佳，VOO-004 Att3
（MBPC，min(A,B)† 1.12 with Part B std=0）為當前最佳。SPY-009 Att2 在 SPY
（與 VOO 同追蹤 S&P 500）上達成 Part A Sharpe **6.56** / Part B 全勝（min† 6.56）
為 repo 已知寬基 ETF 最強 MR 結果，跨資產移植至 VOO 預期可同樣顯著超越
VOO-004 Att3 的 1.12†。

跨資產假設：
- VOO 與 SPY 皆追蹤 S&P 500，價格相關性 > 0.999，failure 結構應該一致
- SPY-009 1d floor + 3d cap 雙維度過濾在 SPY 結構性過濾全部 Part A SLs +
  Part B 唯一 SL（2025-04-07 Trump 關稅）
- 預期 VOO 同樣 1d 過淺漂移 SLs（2022 bear 期）+ 同日 Trump 關稅 SL 失敗結構

進場條件（同 SPY-009、同 VOO-001/002/003 baseline）：
1. RSI(2) < 10（極端超賣）
2. 2 日累計跌幅 >= 1.5%（幅度過濾）
3. 收盤位置 >= 40%（日內反轉確認）
4. **1 日跌幅下限 <= -0.5%**（VOO-005 第一維度，SPY-009 跨資產移植）
5. **3 日急跌上限 >= -8%**（VOO-005 第二維度，DIA-012 / SPY-009 跨資產移植）
6. 冷卻期 5 個交易日

出場參數（沿用 VOO MR 系列已驗證最佳，搭配 1d floor 後 TP 上限應可擴展）：
- TP +3.0% / SL -3.0% / 20 天（同 SPY-009，1d floor 過濾後 2022-05-12
  類型訊號被移除，TP 由 VOO-003 +2.85% 擴展至 +3.0% 不再翻轉）

跨資產延伸（lesson #19 family，repo 首次 SPY → VOO 跨資產移植）：
- DIA-012 Att2：1d cap >= -2.0% AND 3d cap >= -7%（DJIA 30 stocks，1.0% vol）
- SPY-009 Att2 ★：1d floor <= -0.5% AND 3d cap >= -8%（S&P 500 ETF，1.0% vol）
- VOO-005 Att1（本實驗）：1d floor <= -0.5% AND 3d cap >= -8%（S&P 500 ETF，
  Vanguard 版本，1.0% vol）— SPY-009 直接移植
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VOO005Config(ExperimentConfig):
    """VOO-005 Signal-Day Capitulation-Strength Filter MR 參數"""

    # RSI(2) 參數（同 VOO-001/002/003 baseline、同 SPY-009）
    rsi_period: int = 2
    rsi_threshold: float = 10.0

    # 2 日累計跌幅過濾（同 VOO-001/002/003 baseline、同 SPY-009）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 VOO-001/002/003 baseline、同 SPY-009）
    close_position_threshold: float = 0.4

    # 1 日跌幅下限（VOO-005 第一維度，SPY-009 跨資產移植）
    # Att1/Att2 -0.5%：要求訊號日 1 日跌幅 ≥ 0.5%（過濾弱勢漂移 SLs）
    oneday_return_floor: float = -0.005

    # 3 日累計跌幅上限（VOO-005 第二維度，DIA-012 / SPY-009 跨資產移植）
    # Att1/Att2 -8%：排除 regime-shift 級別 3 日延續下跌（如 2025-04-07 關稅）
    threeday_return_cap: float = -0.08

    # 冷卻期（同 SPY-009）
    cooldown_days: int = 5


def create_default_config() -> VOO005Config:
    return VOO005Config(
        name="voo_005_capitulation_filter",
        experiment_id="VOO-005",
        display_name="VOO Signal-Day Capitulation-Strength Filter MR",
        tickers=["VOO"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 SPY-009，1d floor 後可擴展自 VOO-003 +2.85%）
        stop_loss=-0.030,  # -3.0%（同 SPY-009）
        holding_days=20,  # 20 天（同 VOO-002/003、同 SPY-009）
    )
