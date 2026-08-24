"""
USO-027: Multi-Period Capitulation-Strength Filter MR

實驗動機 (Problem statement)：
- USO-025 Att3 為當前全域最優（min(A,B) 0.41）：USO-013 完整框架 +
  ^OVX 3d change <= +4 forward-looking implied vol DIRECTION gate。
  Part A 25 訊號 / WR 72.0% / Sharpe 0.41 / cum +32.48%（7 SLs 殘留）
  Part B 10 訊號 / WR 80.0% / Sharpe 0.64 / cum +16.85%
- Part A 殘留 7 個 SLs 集中於「multi-day persistent decline regime」：
  2019-09-25（Saudi attack 後續跌）、2020-01-22（pre-COVID）、
  2020-06-11（post-COVID 反彈失敗）、2021-03-23（3 月修正）、
  2021-08-09（Delta variant）、2022-06-17（Powell 鷹派）、
  2023-02-02（post-Fed energy weakness）
- USO-013 既有 2 日急跌 floor (<= -2.5%) 為「signal-day capitulation depth」；
  缺少「multi-day capitulation persistence」維度（5 日累計報酬上限），
  無法區分「單日急跌後反彈」（true MR）與「多日連續急跌」（continuation）

跨資產脈絡（lesson #19 family multi-period dimension combo）：
- URA-013 Att2 (4.4% vol, policy-driven) ★：5d return cap >= -9.0%
  作為 supplementary 過濾，min(A,B) 0.39→0.47（+21%）
- INDA-011 Att3 (0.97% vol, broad EM) ★：2DD floor + 3DD cap >= -3.0%
  作為 dual-dimension combo，min(A,B) 0.30→0.55（+83%）
- SIVR-018 Att3 (2.34% vol, silver) ★：ATR ceiling + 3d return floor
  雙維度 combo，min(A,B) 0.39→0.48
- DIA-012 Att2 (1.0% vol, broad equity)：1d cap + 3d cap dual-dimension
- GLD-014 Att2 (1.1% vol, gold)：2d floor + 1d floor dual-dimension
- 共同模式：lesson #19 family 多維度組合在已套用 single-dimension capitulation
  filter 後可進一步切除「多日累積疲弱」訊號，提升 Part A WR 與 Sharpe

USO 在此族群中為「首次商品 event-driven ETF + 多維度 capitulation depth combo」。
USO-013 框架已含 2 日 floor (-2.5%)；新增 5 日 return cap 作為 multi-day
persistence dimension：require 5 日累計報酬 >= 閾值（5d 不得太深），
排除「多日連續急跌持續性 decline regime」訊號。

USO 2.2% 日波動 → 5d 1σ ≈ ±5%，2σ ≈ ±10%。設計初值：
- Att1: 5d_return_min = -7.0%（~1.4σ，URA-013 -9%/4.4%vol = -2σ scaled equivalent
  for USO 2.2%vol = ~-4.5%；採稍寬 -7% 保守起點，避免過度切除 winners）
- Att2: 5d_return_min = -5.0%（tighter，sweet-spot 探索）
- Att3: 視結果調整甜蜜點（可能採 -6.0% 或加深至 -4.0%）

設計理念：
- 沿用 USO-025 Att3 完整框架（pullback 7-12% + RSI(2)<15 + 2d floor <= -2.5%
  + ^OVX 3d <= +4 + TP+3.0%/SL-3.25%/10d/cd10）
- 疊加 5 日報酬 cap 作為**獨立第五維度**（與 ^OVX DIRECTION 維度正交：
  ^OVX = 期權市場對未來 vol 的預期，5d return = 過去 5 日已實現價格軌跡）
- 出場、冷卻、進場其餘條件全部不變，僅新增 1 個過濾條件以隔離 5d cap
  邊際貢獻

跨資產貢獻：
- repo 第 5 次 lesson #19 multi-period dimension combo（繼 INDA-011 / DIA-012
  / GLD-014 / SIVR-018 後）
- repo 首次「2d floor + 5d cap 雙維度組合」於任何資產（單日急跌深度 +
  多日急跌持續性兩個正交維度）
- repo 首次將 lesson #19 multi-period 框架移植至 commodity event-driven ETF
- 若 SUCCESS → 擴展 lesson #19 family 適用邊界至 USO commodity 類別 +
  確認 multi-period combo 為 backward-looking 飽和後的下一維度

預期 Part A 過濾效應：
- 2021-08-09 Delta variant SL：當日 5d 報酬深度估計 ~-6%（持續 5 日下跌），
  -7% 閾值可能不過濾，-5% 會過濾
- 2020-06-11 post-COVID 反彈失敗 SL：5d 報酬可能正向（COVID 反彈中段），
  cap 過濾不到
- 2019-09-25 Saudi attack SL：當日為 +大幅波動後第二日，5d 可能小幅正
- 2022-06-17 Powell SL：5d 報酬深度估計 ~-5%（5 日連續下跌），閾值敏感
- 2023-02-02 SL：5d 估計 ~-4%（5 日連續走弱），-5% 才捕捉
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO027Config(ExperimentConfig):
    """USO-027 Multi-Period Capitulation-Strength Filter MR 參數"""

    # 進場 — 回檔（沿用 USO-013/USO-025）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07
    pullback_max: float = -0.12

    # 進場 — RSI(2) 短期超賣（沿用）
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 進場 — 2 日急跌 floor（沿用，signal-day capitulation depth）
    drop_2d_threshold: float = -0.025

    # ^OVX forward-looking implied vol regime gate（沿用 USO-025 Att3 sweet spot）
    ovx_ticker: str = "^OVX"
    use_ovx_direction_filter: bool = True
    ovx_direction_lookback: int = 3
    max_ovx_change: float = 4.0

    # USO-027 核心新增：5 日報酬 cap（multi-day persistence dimension）
    # 要求 5 日累計報酬 >= return_5d_min（不得太深 → 排除多日連續疲弱）
    use_return_5d_cap: bool = True
    return_5d_lookback: int = 5
    # Att1: -0.07（保守起點 ~1.4σ）→ FAIL min 0.37（過嚴，filter 偏向移除 winners）
    # Att3: -0.08（中間值）→ FAIL min 0.43（仍偏緊，移除 winner > losser）
    # Att2: -0.10 ★ SUCCESS（loosest，僅過濾極端持續下跌）→ min 0.50（+22% vs USO-025 0.41）
    return_5d_min: float = -0.10

    # 冷卻期（沿用）
    cooldown_days: int = 10


def create_default_config() -> USO027Config:
    return USO027Config(
        name="uso_027_multi_period_cap_mr",
        experiment_id="USO-027",
        display_name="USO Multi-Period Capitulation-Strength Filter MR",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.0325,
        holding_days=10,
    )
