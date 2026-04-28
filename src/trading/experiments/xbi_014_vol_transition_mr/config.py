"""
XBI Post-Capitulation Vol-Transition 均值回歸配置 (XBI-014)

動機：XBI-005（全域最佳，Part A Sharpe 0.36 / Part B 0.65）已被 13 次實驗確認
為 XBI 結構最優，但 Part A 5/21 SL 仍壓制 Sharpe 至 0.36。XBI-013 Gap-Down /
XBI-012 Capitulation+Accel / XBI-011 RSI Hook / XBI-010 BB-lower hybrid 均
失敗，剩餘可探索方向有限。

核心假設（cross-asset port from VGK-008 Att2 / INDA-010 Att3 / EEM-014 Att2 /
USO-013 / IBIT-009 Att1）：「2DD floor 加深」可過濾 Part A 殘餘 SL 中的
shallow-2DD「slow-melt drift」失敗訊號，保留深 2DD 真 capitulation 反彈。

Post-Capitulation Vol-Transition MR 模板的 vol 適用範圍：
- INDA 0.97% vol → 2DD floor <= -2.0%
- VGK  1.12% vol → 2DD floor <= -2.0%（懸崖式）
- EEM  1.17% vol → 2DD floor <= -0.5%
- USO  2.20% vol → 2DD floor <= -2.5%
- IBIT 3.17% vol → 2DD floor <= -3.0%

XBI 日波動 ~2.0% 落於 USO（2.20%）與 EEM/INDA/VGK（~1%）之間。XBI 為 US 板塊
ETF 而非 broad ETF，與 USO（commodity ETF）結構較接近，故初始嘗試門檻
-2.0% ~ -3.0%。

XBI-005 殘餘失敗訊號：
- Part A SL（5 筆）：
  - 2021-02-19 SL -5.09%（Feb 修正期間）
  - 2021-05-06 SL -5.10%（XBI 1H 2021 bear 中段）
  - 2022-01-06 SL -5.10%（rate-hike 恐慌起點）
  - 2022-04-19 SL -5.10%（mid-2022 bear continuation）
  - 2023-09-21 SL -5.10%（2023 Q3 weakness）
- Part B SL（1 筆）：
  - 2025-03-31 SL -5.09%（Trump tariff selloff，深 2DD 加速）

預期：2DD floor 過濾 Part A shallow-2DD slow-melt SLs，保留 Part B Trump
tariff acute SL（已是品質訊號的對立面）並改善 Part A Sharpe。

========================================================================
迭代設計（每次迭代後更新本檔案註解，實際結果待回測確認）：
========================================================================

Att1（基線測試）：XBI-005 全條件 + 2DD floor <= -2.0%
  - 直覺：與 INDA/VGK 同門檻；XBI 2.0% vol 約 0.7σ 2DD 深度
  - 預期：過濾 slow-drift 進場，保留 acute capitulation

Att2（待 Att1 結果決定）：依 Att1 是否需要加深 / 放寬 / 改用其他方向

Att3（待 Att1/Att2 結果決定）：sweet spot 確認或備案方向
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI014Config(ExperimentConfig):
    """XBI-014 Post-Capitulation Vol-Transition MR 參數"""

    # 進場 — 回檔（同 XBI-005）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 >= 8%
    pullback_upper: float = -0.20  # 回檔上限 20%

    # 進場 — Williams %R（同 XBI-005）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（同 XBI-005）
    close_position_threshold: float = 0.35

    # 進場 — 2 日急跌下限（XBI-014 核心創新）
    # 2 日報酬 <= drop_2d_floor 才進場，過濾「shallow 2DD = slow-melt drift」
    # 進場品質：要求近 2 日已有明顯急跌，符合 post-capitulation 結構
    # Att1: -2.0% 失敗（min 0.16）；Att2: -2.5% 失敗（min 0.16，Part A WR 單調下降）
    # Att3: 最輕度 floor -1.0% 作為最終 ablation，建立完整 threshold sweep 失敗曲線
    drop_2d_floor: float = -0.010  # Att3: -1.0%（最輕度 ablation）

    # 冷卻期（同 XBI-005）
    cooldown_days: int = 10


def create_default_config() -> XBI014Config:
    return XBI014Config(
        name="xbi_014_vol_transition_mr",
        experiment_id="XBI-014",
        display_name="XBI Post-Capitulation Vol-Transition MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 XBI-005）
        stop_loss=-0.050,  # -5.0%（同 XBI-005）
        holding_days=15,  # 15 天（同 XBI-005）
    )
