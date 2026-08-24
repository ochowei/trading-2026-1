"""
DIA-016 DIA-QQQ Cross-Asset Divergence CEILING Regime-Gated MR 配置

策略方向（lesson #20 v3 cross-asset divergence regime gate，CEILING 方向）：
  與 DIA-014（DIA-IWM cap-segment anchor，新全域最優 13.60†）平行，本實驗
  測試 **DIA-QQQ style/value-vs-growth divergence** 作為替代 anchor，建立
  lesson #20 v3 「低波動美國寬基指數 ETF」anchor 選擇規則（cap-segment IWM
  vs style QQQ）。在 DIA-012 Att2 MR 框架上新增第六條件：
  **DIA 10 日報酬 - QQQ 10 日報酬 <= max_rel_return（CEILING）**

trade-level signal-day DIA-QQQ 10 日相對報酬 pre-analysis：

  | Part A date | tag | relQQQ_10d |
  |-------------|-----|------------|
  | 2022-01-18  | SL  | **+4.51%** | ★ 唯一 SL，全 Part A 最高
  | 2022-06-14  | TP  | +2.66%     | ← Part A 贏家最高
  | 2020-09-21  | TP  | +2.23%     |
  | 2022-09-23  | TP  | +2.17%     |
  | 其餘 TP/EXP | —   | <= +1.90%  |

  | Part B date | tag | relQQQ_10d |
  |-------------|-----|------------|
  | 2024-05-30  | TP  | -4.02%     |
  | 2024-08-02  | TP  | **+4.13%** | ★ 高於 CEILING → 預期被誤過濾
  | 2025-08-01  | TP  | -0.39%     |

  **預期結構性對比（vs DIA-014 DIA-IWM）**：DIA-QQQ 10d CEILING ∈
  (+2.66%, +4.51%) 雖可 surgical 移除 Part A SL 2022-01-18，但 Part B
  2024-08-02 winner 之 relQQQ_10d=+4.13% 同樣高於 CEILING（2024-08 日圓
  套息平倉 broad capitulation，DIA 跑贏 QQQ 為合理 broad-cap 結構），將被
  誤過濾 → Part B 3→2 訊號（樣本縮減 + signal gap 惡化）。預期驗證
  **DIA-IWM（cap-segment）為優於 DIA-QQQ（style）之 anchor**：QQQ 之
  tech-growth beta 使「DIA 跑贏 QQQ」同時涵蓋 (a) 2022-01-18 規避型
  regime-shift（SL，應過濾）與 (b) 2024-08-02 broad-panic DIA-relative-
  resilience（winner，不應過濾），CEILING 無法區分；IWM（small-cap broad）
  與 DIA 同為 risk-on cyclical，divergence 結構更乾淨。

跨資產脈絡（lesson #20 v3 family，repo 第 10 次應用）：
- DIA-014 ✓（DIA-IWM 10d CEILING，cap-segment anchor，13.60†，新全域最優）
- **DIA-016（本實驗）：DIA-QQQ 10d CEILING，style anchor，預期 anchor
  選擇對比——Sharpe 可改善但 Part B 樣本縮減**

迭代計畫：
- Att1：rel_lookback=10, max_rel_return=+0.035（對齊 DIA-014 sweet spot）
- Att2：rel_lookback=20（DIA-QQQ 20d 替代窗口，pre-analysis 顯示 20d 無
  surgical gap，預期更差）
- Att3：穩健性 / ablation

驗收目標（goal）：min(A,B) Sharpe > DIA-012 Att2 1.31†；A/B cum gap < 30%；
signal gap < 50%；必須使用成交模型（execution model）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA016Config(ExperimentConfig):
    """DIA-016 DIA-QQQ Divergence CEILING Regime-Gated MR 參數"""

    # === MR 進場框架（完全沿用 DIA-012 Att2）===
    rsi_period: int = 2
    rsi_threshold: float = 10.0
    decline_lookback: int = 2
    decline_threshold: float = -0.015
    close_position_threshold: float = 0.4
    oneday_return_cap: float = -0.020
    threeday_return_cap: float = -0.07
    cooldown_days: int = 5

    # === DIA-016 核心新增：DIA-QQQ cross-asset divergence CEILING ===
    # QQQ (Invesco QQQ Trust, NASDAQ-100) 為 growth/tech style benchmark
    anchor_ticker: str = "QQQ"
    rel_lookback: int = 10
    # CEILING：DIA Nd 報酬 - QQQ Nd 報酬 <= max_rel_return
    # Att1 +0.035（對齊 DIA-014 sweet spot；落於 SL +4.51% 與 Part A 贏家
    # 最高 +2.66% 之間，但 Part B 2024-08-02 +4.13% 亦 > CEILING 預期被濾）
    max_rel_return: float = 0.035


def create_default_config() -> DIA016Config:
    return DIA016Config(
        name="dia_016_qqq_divergence_mr",
        experiment_id="DIA-016",
        display_name="DIA-QQQ Divergence CEILING Regime-Gated MR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=25,
    )
