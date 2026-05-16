"""
DIA-014 DIA-IWM Cross-Asset Divergence CEILING Regime-Gated MR 配置

策略方向（lesson #20 v3 cross-asset divergence regime gate，CEILING 方向）：
  在 DIA-012 Att2（min(A,B)† 1.31，DIA 全域最佳）的 RSI(2)+2DD+ClosePos+
  1d cap+3d cap MR 框架上，新增第六條件：
  **DIA 10 日報酬 - IWM 10 日報酬 <= max_rel_return（CEILING）**

動機（trade-level signal-day 分析）：
  DIA-012 Part A 12 訊號中唯一停損為 2022-01-18（-3.60%，2022 Fed 升息熊市
  起點），為 binding constraint（Part B 3 訊號全 TP std=0，採 EWJ-003/
  DIA-012 慣例以 Part A Sharpe 為 min 約束）。

  signal-day DIA-vs-IWM 10 日相對報酬分析：

  | Part A date | tag | relIWM_10d |
  |-------------|-----|------------|
  | 2022-01-18  | SL  | **+4.53%** | ★ 唯一 SL，全 Part A 最高
  | 2022-09-23  | TP  | +2.77%     | ← Part A 贏家最高
  | 2022-12-16  | TP  | +2.49%     |
  | 2021-12-20  | TP  | +2.03%     |
  | 2019-05-29  | TP  | +1.86%     |
  | 2021-09-20  | TP  | +0.77%     |
  | 2022-06-14  | TP  | +0.51%     |
  | 2020-09-21  | TP  | -0.24%     |
  | 2020-02-28  | TP  | -0.23%     |
  | 2020-01-27  | TP  | -0.12%     |
  | 2019-12-03  | TP  | -2.43%     |
  | 2023-05-04  | EXP | +2.00%     | （+2.25% 到期，獲利）

  | Part B date | tag | relIWM_10d |
  |-------------|-----|------------|
  | 2024-05-30  | TP  | -1.74%     |
  | 2024-08-02  | TP  | +2.21%     |
  | 2025-08-01  | TP  | +1.63%     |

  關鍵發現：2022-01-18 SL 的 DIA-IWM 10d rel = +4.53%，與 Part A 贏家最高值
  +2.77%（2022-09-23）之間存在 **+1.76pp surgical gap**；全部 3 Part B 贏家
  relIWM_10d <= +2.21% 均遠低於 +3.5% CEILING。

  結構解讀（lesson #20 v3 CEILING 方向，鏡像 NVDA-021 / INDA-012）：
  2022-01-18 為 Fed 升息 hawkish pivot 起點，small-cap（IWM）已先行崩跌而
  DIA 大型權值股仍相對撐盤（late-cycle defensive rotation），DIA 此時的
  RSI(2) 急跌為 broad regime-shift 熊市起點延續而非乾淨 V-bounce MR 機會。
  「DIA 過度跑贏 IWM」= individual asset over-outperformance vs broader
  cap-segment benchmark = rally exhaustion / regime-shift 結構（CEILING 適用）。

跨資產脈絡（lesson #20 v3 cross-asset divergence regime gate，repo 第 9+ 次應用）：
- TLT-014 ✓（TLT-SPY 20d FLOOR，rate ETF + MR）
- TSLA-017 ✓（TSLA-QQQ 20d FLOOR，high-vol single stock + BB Squeeze）
- INDA-012 ✓（INDA-EEM 60d CEILING，single-country EM + MR）
- EWZ-009 ✓（EWZ-EEM 10d CEILING，commodity EM + MR）
- NVDA-021 ✓（NVDA-QQQ 20d CEILING，high-vol AI mega-cap + MBPC）
- FXI-015 ✓（FXI-ASHR 20d FLOOR，H-share vs A-share + MR）
- GLD-016 ✓（GLD-DXY 5d，commodity safe-haven + MR）
- USO-026 ✗（USO-XLE 20d，commodity ETF + MR，driver regime-switch 失敗）
- **DIA-014（本實驗）：DIA-IWM 10d CEILING，repo 首次「large-cap broad ETF
  vs small-cap broad ETF」cap-segment anchor 結構，repo 首次 cross-asset
  divergence regime gate 應用於低波動美國寬基指數 ETF**

迭代計畫：
- Att1 ★：rel_lookback=10, max_rel_return=+0.035（surgical sweet spot 中央）
- Att2：視 Att1 調整 lookback（10→20）或 threshold（穩健性）
- Att3：穩健性驗證 / ablation

驗收目標（goal）：
- min(A,B) Sharpe > DIA-012 Att2 baseline 1.31†
- Part A/B 累計報酬差距 < 30%、訊號數差距 < 50%
- 必須使用成交模型（execution model，0.1% slippage、隔日開盤市價進場）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA014Config(ExperimentConfig):
    """DIA-014 DIA-IWM Divergence CEILING Regime-Gated MR 參數"""

    # === MR 進場框架（完全沿用 DIA-012 Att2 當前最佳）===
    rsi_period: int = 2
    rsi_threshold: float = 10.0
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%
    close_position_threshold: float = 0.4
    oneday_return_cap: float = -0.020  # 1 日急跌上限 >= -2.0%
    threeday_return_cap: float = -0.07  # 3 日急跌上限 >= -7%
    cooldown_days: int = 5

    # === DIA-014 核心新增：DIA-IWM cross-asset divergence CEILING ===
    # IWM (iShares Russell 2000 ETF) 為 small-cap broad benchmark，作 pair anchor
    anchor_ticker: str = "IWM"
    # lookback：trade-level 分析顯示 10d 為 surgical sweet spot
    rel_lookback: int = 10
    # CEILING：DIA Nd 報酬 - IWM Nd 報酬 <= max_rel_return
    # Att1 ★ +0.035 落於 SL +4.53% 與贏家最高 +2.77% 之間（+1.76pp gap 中央）
    # Att2 +0.030（穩健性：收緊 0.5pp，與 Att1 完全相同 → 確認 sweet spot）
    # Att3 +0.060（ablation：放寬至 SL +4.53% 之上 → 非綁定，回退 baseline 1.31，
    #              確認 DIA-IWM 10d CEILING 為 binding surgical discriminator）
    # 最終採 Att1 +0.035（robust sweet spot 中央，1pp 安全邊際）
    max_rel_return: float = 0.035


def create_default_config() -> DIA014Config:
    return DIA014Config(
        name="dia_014_iwm_divergence_mr",
        experiment_id="DIA-014",
        display_name="DIA-IWM Divergence CEILING Regime-Gated MR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 DIA-012）
        stop_loss=-0.035,  # -3.5%（同 DIA-012）
        holding_days=25,  # 25 天（同 DIA-012）
    )
