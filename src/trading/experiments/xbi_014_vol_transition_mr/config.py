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

========================================================================
三次迭代結果（2026-04-28，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1（失敗）：drop_2d_floor = -2.0%（INDA/VGK 標準門檻）
  Part A: 18 訊號 / WR 72.2% / Sharpe **0.24** / cum +16.64%
  Part B: 6 訊號 / WR 66.7% / Sharpe **0.16** / cum +3.37%
  min(A,B) **0.16**（-56% vs XBI-005 baseline 0.36）
  失敗分析：cooldown chain shift（lesson #19）將原 2024-03-14 TP（2DD -1.82%
  不滿足 -2.0% floor）釋放成 2024-03-15 SL，淨增 1 筆 Part B SL；Part A
  也損失 3 訊號中 2 為 TP。

Att2（失敗）：drop_2d_floor = -2.5%（向 USO 2.20% vol 門檻靠攏）
  Part A: 16 訊號 / WR 68.8% / Sharpe **0.16** / cum +8.90%
  Part B: 5 訊號 / WR 80.0% / Sharpe **0.52** / cum +8.90%
  min(A,B) **0.16**（同 Att1，未改善）
  失敗分析：Part A WR 從 baseline 76% → Att1 72.2% → Att2 68.8% **單調下降**，
  加深 floor 系統性移除 TPs 多於 SLs。Part A 殘餘 SL 2DD 分布為 -1.03 / -3.01 /
  -3.17 / -3.61 / -5.53，僅 1 筆（-1.03）可被 -1.5% floor 過濾；TPs 中 9/15
  筆 2DD > -2.5% 被誤殺。

Att3（最接近 baseline 但仍失敗）：drop_2d_floor = -1.0%（最輕度 ablation）
  Part A: 20 訊號 / WR 75.0% / Sharpe **0.32** / cum +24.96%
  Part B: 6 訊號 / WR 83.3% / Sharpe **0.64** / cum +12.71%
  min(A,B) **0.32**（-11% vs baseline 0.36）
  失敗分析：僅過濾 2021-01-05 TP（2DD -0.23%），三次最接近 baseline 但仍未
  超越；threshold sweep 完整失敗曲線確認方向錯誤。

Threshold sweep 完整失敗曲線：
  baseline（無 filter） 0.36 → -1.0% 0.32 → -2.0% 0.16 → -2.5% 0.16
  單調退化，**確認 2DD floor 加深方向對 XBI 完全無效**。

========================================================================
失敗根因分析：
========================================================================

1. **XBI 2DD 分布 NO unidirectional selectivity**：
   - Part A SLs 範圍 -1.03% ~ -5.53%
   - Part A TPs 範圍 -0.23% ~ -6.86%
   - 重疊整個範圍，任何 2DD 閾值都會誤殺 TPs 而保留 SLs

2. **生技 FDA event-driven 雙峰結構**：
   XBI winners 同時涵蓋 shallow 2DD（短期反彈）與 deep 2DD（acute
   capitulation）兩極，與 INDA/EEM/VGK/USO/IBIT 的「shallow 2DD = drift」
   單峰失敗結構結構不同。

3. **Cooldown chain shift（lesson #19）**：
   Att1 -2.0% 過濾後 2024-03-15 從冷卻期釋放成新訊號（SL）。

========================================================================
跨資產貢獻（lesson 更新）：
========================================================================

- Repo 第 6 次「2DD floor 加深方向」失敗驗證，**首次 US 板塊 ETF 測試**
- 整合規則：Post-Capitulation Vol-Transition MR 有效條件需同時滿足
  (a) vol ∈ [0.97%, 3.17%] AND
  (b) winners 2DD 分布**單峰**（broad ETF / 商品 / 加密 ETF）
- 事件驅動板塊 ETF（XBI FDA、CIBR 政策—但 cap 方向有效）winners 2DD
  雙峰分布使任何單向 filter 失效
- XBI 第 11 個失敗策略類型；XBI-005 確認為全域最優（14 次實驗、44+ 次嘗試）

最終配置（Att3，最接近 baseline 但仍失敗）：drop_2d_floor = -0.010
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
