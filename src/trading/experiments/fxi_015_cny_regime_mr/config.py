"""FXI–CNY (Yuan) Currency-Regime-Gated Mean Reversion (FXI-015)

實驗動機：
- FXI-014 Att2 為當前全域最優（min(A,B) Sharpe 1.01，Part A 1.01 / Part B
  1.61），14 次實驗、45+ 次嘗試。binding = Part A（min = Part A Sharpe）。
- 跨資產 divergence/currency regime gate family v4 已三度成功
  （TSLA-017 TSLA−QQQ、TLT-014 TLT−SPY、GLD-016 GLD−USD(UUP)），但
  driver-purity 前置條件下已有 3 個 documented-failure subclass：
  SIVR-019（metal-vs-USD，driver-impure）、EWT-010（component-vs-parent
  正相關）、TSLA-018（high-vol single growth stock vs USD，禁忌 #36e）。
- 本實驗測試「**country-specific** 貨幣 regime gate」是否能救政策驅動
  單一國家 EM 股票 ETF——直覺：弱人民幣 (CNY=X 上升) = 中國資本外流 /
  risk-off → FXI 走弱。base = FXI-014 Att2 全域最優框架 + 第 7 條件
  FXI–CNY 貨幣 regime gate（GLD-016 USD-regime 形式）。
- 空遠端 artifact `fxi_016_usdcnh_direction_mr` 獨立指向「FXI vs 離岸
  人民幣」方向；USDCNH=X / CNH=X 於 yfinance 無資料，改用在岸 **CNY=X
  (USD/CNY)** 為人民幣 regime proxy（與 CNH basis <1%，標準人民幣
  regime 代理），並以**獨立 module 名稱** `fxi_015_cny_regime_mr`
  避免 branch-divergence artifact 衝突（TSLA-018 / EWT-010 同慣例）。

強制 predict→confirm 預分析（先做，重現 FXI-014 Att2 全 21+5 筆交易，
CNY=X N 日 % change，+ve = 人民幣貶值 = China risk-off）：

  binding Part A 殘餘 3 SLs（FXI-014 Att2 唯一約束）：
  | Signal     | exit | ret%  | CNY10 | CNY20 | CNY30 | Rel20=FXI20−CNY20 |
  |------------|------|-------|-------|-------|-------|-------------------|
  | 2021-11-03 | SL   | -5.09 | +0.27 | -0.72 | -1.04 | +6.66  Didi/教培監管餘波
  | 2022-03-02 | SL   | -5.10 | -0.70 | -0.75 | -0.55 | -8.73  COVID 封城/俄烏
  | 2023-02-06 | SL   | -5.10 | -0.12 | -1.56 | -2.68 | -0.30  reopening 退潮

  → **3 筆 binding SL 全發生於人民幣「走強或持平」regime**
    （CNY20 ∈ [-1.56, -0.72]，CNY=X 下跌 = 人民幣升值），
    並非弱人民幣事件——其為**中國政策/監管股市事件衝擊**，與貨幣
    regime 解耦（且反向）。

  Part A 18 winners CNY20 ∈ [-2.24, +5.75]（含弱人民幣大贏家
  2022-05-10 +5.75 / 2022-09-29 +4.17）、CNY10 ∈ [-1.18, +3.42]、
  CNY30 ∈ [-2.46, +6.06]；Rel20 = FXI20−CNY20 ∈ [-18.27, +6.96]。

  **預分析判定（NOT separable，預測 documented-failure）**：
  - 3 筆 SL 的 CNY10/20/30 與 winners **完全交錯**，最近 winner
    2023-10-05(CNY20 -1.58) ≈ SL 2023-02-06(-1.56)、2023-12-05
    expiry-win(-2.24) 包夾之；2021-09-21/2021-12-17 winners(-0.41/
    -0.15) 與 SL 2021-11-03(-0.72) 交錯。**無單一 CEILING/FLOOR/BAND
    可隔離 3 SL 而不誤殺 ≥3 winners；無 ≥15pp robust plateau。**
  - 直覺「弱人民幣 = risk-off CEILING」**被反證**：SL 皆 firm-yuan，
    弱人民幣反而是 winners（2022-05-10/09-29 +5.50% TP）。
  - FXI vol ≫ CNY vol（~2.0% vs ~0.2%）→ Rel ≈ FXI 動量，divergence
    對 CNY 維度零獨立區分力（SIVR-019 Att2 / TSLA-018 Att3 同構）。

迭代計畫（三次迭代，predict→confirm 全部預測 CONFIRMED-FAIL）：
  Att1：CNY 20d 報酬 CEILING ≤ +1.0%（filter 弱人民幣 risk-off regime，
        直覺假設）→ 預測 SL 皆 firm-yuan 通過 ceiling（非綁定）→
        TIE 或誤殺弱人民幣 winners（TSLA-018 Att2 / SIVR-019 Att1 同構）
  Att2：CNY 20d CEILING ≤ +0.0%（收緊，僅允許人民幣持平/升值）→
        移除部分 SL 必同殺大量 firm-yuan winners → inverted/degrade
        （EWT-010 Att2 同構）
  Att3：FXI−CNY 相對 divergence FLOOR Rel20 ≥ min_relative_return
        （TLT-014/GLD-016 Att2/TSLA-018 Att3 精確類比）→ FXI vol≫CNY
        vol 使 Rel≈FXI、零區分力 → TIE（SIVR-019 Att2 同構）

預測：DOCUMENTED-FAILURE，延伸禁忌 #36e / family v4 driver-purity 前置
條件——**country-specific 貨幣 regime gate 亦不可移植至政策驅動單一
國家 EM 股票 ETF**（殘餘 binding SL 為監管/地緣股市事件，與貨幣 regime
結構性解耦且反向）。FXI 加入 EWJ-006/EEM-016/INDA-012/INDA-013/TSM-012/
TSLA-018「idiosyncratic non-separable single residual SL」family，為
**政策驅動 China 股票 vs 在地貨幣**新 driver subclass（區別於 EWT-010
component-vs-parent、SIVR-019 industrial-metal）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI015Config(ExperimentConfig):
    """FXI-015 FXI–CNY 貨幣 regime gate 參數

    base = FXI-014 Att2 全域最優框架（pullback 10d [-5%,-12%] + WR(10)≤-80
    + ClosePos≥40% + ATR(5)/ATR(20) BAND (1.05, 1.35] + cooldown 10），
    疊加 FXI–CNY 貨幣 regime gate（GLD-016 USD-regime 形式）。
    """

    # 進場框架（沿用 FXI-014 Att2 = FXI-005 + ATR BAND）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05
    pullback_cap: float = -0.12
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.4
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.05
    atr_ratio_ceiling: float = 1.35
    cooldown_days: int = 10

    # FXI–CNY 貨幣 regime gate（FXI-015 核心新增）
    # CNY=X = USD/CNY 在岸人民幣（+ve N 日報酬 = 人民幣貶值 = China
    #  risk-off）。USDCNH=X / CNH=X 於 yfinance 無資料，CNY 為標準代理。
    cny_ticker: str = "CNY=X"
    cny_lookback: int = 20  # N 日報酬窗口
    # Att1（最終 default）：CNY 20d 報酬 CEILING ≤ +1.0%（filter 弱人民幣
    #   risk-off regime，直覺假設）。預分析：3 筆 binding SL CNY20 ∈
    #   [-1.56,-0.72] 皆 firm-yuan、通過 ceiling（非綁定）→ 預測 TIE/degrade。
    # Att2：CNY 20d CEILING ≤ +0.0%（收緊）→ 移除 SL 必同殺 firm-yuan
    #   winners（2019-11-14 -0.99 / 2023-10-05 -1.58 / 2023-12-05 -2.24…）
    #   → inverted/degrade。
    # Att3：FXI−CNY relative divergence FLOOR（Rel20 = FXI20 − CNY20 ≥
    #   min_relative_return）。FXI vol ≫ CNY vol → Rel ≈ FXI 動量、零
    #   區分力 → TIE。
    use_cny_ceiling: bool = True
    max_cny_return: float = 0.0  # Att2：CNY 20d 報酬 ≤ +0.0%（收緊 CEILING）
    use_cny_divergence: bool = False
    min_relative_return: float = -0.99  # 停用時設極寬


def create_default_config() -> FXI015Config:
    return FXI015Config(
        name="fxi_015_cny_regime_mr",
        experiment_id="FXI-015",
        display_name="FXI–CNY Currency-Regime-Gated MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,  # +5.5%（同 FXI-014 Att2）
        stop_loss=-0.050,  # -5.0%（同 FXI-014 Att2）
        holding_days=20,  # 20 天（同 FXI-014 Att2）
    )
