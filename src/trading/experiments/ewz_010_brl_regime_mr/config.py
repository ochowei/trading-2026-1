"""
EWZ-010: EWZ–BRL Currency-Regime-Gated Vol-Transition MR

策略方向（country currency regime gate；predict→confirm 預測 documented-failure）：
- base = EWZ-009 Att1 全域最優（min(A,B) 1.50）：EWZ-007 Att3 六條件 MR 框架
  (BB(20,1.5) 下軌 + 10d 回檔上限 + WR(10) + ClosePos + ATR(5)/ATR(20)>1.10
  + 1d cap ≥ -5%, TP+5%/SL-4%/18d/cd10) + 第七條件 EWZ–EEM 10d rel 報酬
  CEILING ≤ +2.5%（已驗證移除 2020-01-31 SL）。
- 第八條件（EWZ-010 核心新增）：**EWZ–BRL 貨幣 regime gate**（GLD-016 UUP
  USD-regime / FXI-015 CNY-regime 形式）。目標：過濾 EWZ-009 Att1 唯一殘餘
  binding Part A SL 2019-03-25（-4.1% stop_loss，Brazil 退休金改革政局
  不確定中段的「sustained Brazil-specific weakness / up-day rebound after
  big drop」假 capitulation）。

跨資產脈絡（cross-asset divergence/currency regime gate family v4）：
- DRIVER-PURE 單因子反向 = SUCCESS：TSLA-017（TSLA−QQQ）/ TLT-014（TLT−SPY）
  / GLD-016（GLD−USD，純貨幣 USD-inverse）。
- DRIVER-IMPURE = documented-failure（family v4 driver-purity 前置條件）：
  · SIVR-019 industrial-metal-vs-USD
  · EWT-010 component-vs-parent（EWT 為 EEM 成分，正相關）
  · TSLA-018 high-vol-growth-stock-vs-USD（公司事件驅動 breakout SL）
  · FXI-015 policy-driven-EM-equity-vs-own-currency（CNY；殘餘 SL 為監管/
    地緣股市事件，與在地貨幣 regime 解耦且反向）
- **EWZ-010 = family v4 第 5 個 driver-impure subclass 候選：
  COMMODITY-DRIVEN SINGLE-COUNTRY EM EQUITY vs OWN-COUNTRY CURRENCY (BRL)**。
  EWZ 主驅動為大宗商品（Vale 鐵礦砂、Petrobras 原油）+ 巴西財政/政局，
  非 BRL 匯率本身——違反 family v4「資產主驅動須『即』該貨幣」前置條件
  （gold↔USD 為唯一 driver-pure 範例）。

================================================================================
強制 predict→confirm 預分析（先於建構，重現 EWZ-009 Att1 全 10+6 筆交易）
================================================================================
EWZ-009 Att1 Part A：10 筆，唯一 SL = 2019-03-25（-4.1%），其餘 9 筆全 +5% TP。
BRL=X = USD/BRL（+ve N 日報酬 = BRL 貶值 = 巴西 risk-off 直覺）。

  Date       | Type | EWZ_20d | BRL_20d | EWZ−BRL_rel20
  2019-03-25 | SL   | -6.79   | +4.26   | -11.05   ← 唯一殘餘 binding SL
  2019-05-14 | TP   | -4.06   | +2.84   |  -6.90
  2019-08-02 | TP   | -2.92   | +0.96   |  -3.88
  2019-11-13 | TP   | +0.09   | -0.26   |  +0.35
  2020-11-02 | TP   | -4.26   | +1.05   |  -5.32
  2021-01-22 | TP   | -4.26   | +4.50   |  -8.77
  2021-07-07 | TP   | -5.54   | +2.98   |  -8.51
  2021-10-21 | TP   | -11.24  | +5.84   | -17.07
  2022-09-28 | TP   | -6.12   | +6.98   | -13.10
  2023-10-04 | TP   | -5.04   | +4.02   |  -9.06

  Part B（6 筆全勝，filter 預期非綁定）BRL_20d ∈ [-0.26, +4.37]，
  EWZ−BRL_rel20 ∈ [-12.50, -3.45]（2024-11-29 BRL_20d +4.37 /
  rel20 -12.50；2024-06-10 rel20 -12.01）。

**預分析判定（NOT separable → 預測 documented-failure）**：
- BRL_20d：SL = +4.26 落於 9 winners [-0.26, +6.98] 正中央（介於 +4.02
  與 +4.50），4 個 winners BRL 更弱（+4.50/+5.84/+6.98/+4.02）——
  **完全交錯、無 ≥15pp robust plateau；方向結構性反轉鐵證 = 最強 winners
  2021-10-21/2022-09-28 發生於『最弱 BRL』regime**（BRL 貶值常伴隨
  commodity-EM risk-on 反彈，EWZ MR 正獲利於此）。
- BRL_10d：SL +2.43 落於 winners [+0.69, +6.18] 正中央，5 winners 更弱
  → 同樣交錯。
- EWZ−BRL_rel20：SL -11.05 落於 winners [-17.07, +0.35] 中段
  → CEILING/FLOOR 兩向皆不可分；EWZ 日波動 2.18% ≫ BRL=X 0.91~1.06%
  （~2x）使 rel ≈ EWZ 動量、零獨立 BRL 區分力（SIVR-019 Att2 / FXI-015
  Att3 同構）。
- Part B 全 6 winners 與 SL/winners 完全重疊；任何足以咬住 SL 的 CEILING
  必同殺 Part B winners（2024-11-29 BRL_20d +4.37）→ Part B 崩潰
  （FXI-015 Att2 / EWT-010 Att2 inverted-catastrophic 同構）。

迭代計畫（FXI-015 精確 isomorph，三次全預測 FAIL）：
- Att1（最終 default）：BRL 20d CEILING ≤ +4.0%（弱 BRL risk-off 直覺
  假設）。預測：SL(+4.26)>+4.0 被過濾，但同殺 4 winners
  (BRL_20d>+4.0) + 1 Part B winner → 非外科式、Sharpe 退化
  （TSLA-018 Att1 / SIVR-019 Att1 / FXI-015 Att1 同構）。
- Att2：BRL 20d CEILING ≤ +2.0%（收緊）。預測：catastrophic——僅 3 Part A
  winners 存活，Part B 6→1（5 winners BRL_20d>+2.0）崩潰
  （EWT-010 Att2 / FXI-015 Att2 inverted 同構）。
- Att3：EWZ−BRL relative-divergence FLOOR ≥ -12.0%（TLT-014 / GLD-016
  Att2 / FXI-015 Att3 形式）。預測：SL rel20 -11.05 ≥ -12.0 通過（gate
  對 SL 非綁定），反殺最深背離 winners 2021-10-21(-17.07)/
  2022-09-28(-13.10) + Part B 2024-06-10(-12.01)/2024-11-29(-12.50)
  → FAIL（vol-mismatch 零區分力，SIVR-019 Att2 / FXI-015 Att3 同構）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ010Config(ExperimentConfig):
    """EWZ-010 EWZ–BRL Currency-Regime-Gated Vol-Transition MR 參數

    base = EWZ-009 Att1 全域最優框架（EWZ-007 Att3 六條件 MR + EWZ–EEM 10d
    rel CEILING ≤ +2.5%），疊加 EWZ–BRL 貨幣 regime gate（GLD-016 /
    FXI-015 形式）。
    """

    # === EWZ-007 Att3 完整框架（沿用 EWZ-009 Att1）===
    bb_period: int = 20
    bb_std: float = 1.5
    pullback_lookback: int = 10
    pullback_cap: float = -0.10
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10
    capitulation_mode: str = "1d_cap"
    capitulation_threshold: float = -0.050
    cooldown_days: int = 10

    # === EWZ-009 Att1 已驗證第七條件：EWZ–EEM 10d rel CEILING ≤ +2.5% ===
    eem_ticker: str = "EEM"
    rel_lookback: int = 10
    max_rel_return: float = 0.025

    # === EWZ-010 核心新增第八條件：EWZ–BRL 貨幣 regime gate ===
    # BRL=X = USD/BRL（+ve N 日報酬 = BRL 貶值 = 巴西 risk-off）。
    # BRLUSD=X / USDBRL=X 均可，BRL=X 為標準代理（同 FXI-015 用 CNY=X）。
    brl_ticker: str = "BRL=X"
    brl_lookback: int = 20  # N 日報酬窗口
    # Att1（最終 default）：BRL 20d 報酬 CEILING ≤ +4.0%（弱 BRL risk-off
    #   直覺假設）。預分析：SL(+4.26)>+4.0 被過濾但同殺 4 winners
    #   (BRL_20d>+4.0) + 1 Part B winner → 預測 FAIL。
    # Att2：BRL 20d CEILING ≤ +2.0%（收緊）→ Part B 崩潰（5 winners
    #   BRL_20d>+2.0）→ 預測 catastrophic。
    # Att3：EWZ−BRL relative divergence FLOOR（Rel20 = EWZ20 − BRL20 ≥
    #   min_relative_return）。EWZ vol ≫ BRL vol → Rel ≈ EWZ 動量、零
    #   區分力 → 預測 FAIL。
    use_brl_ceiling: bool = True
    max_brl_return: float = 0.02  # Att2：BRL 20d CEILING ≤ +2.0%（收緊）
    use_brl_divergence: bool = False
    min_relative_return: float = -0.12  # Att3 值（停用時保留供參考）


def create_default_config() -> EWZ010Config:
    return EWZ010Config(
        name="ewz_010_brl_regime_mr",
        experiment_id="EWZ-010",
        display_name="EWZ–BRL Currency-Regime-Gated Vol-Transition MR",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（同 EWZ-009 Att1）
        stop_loss=-0.040,  # -4.0%（同 EWZ-009 Att1）
        holding_days=18,  # 18 天（同 EWZ-009 Att1）
    )
