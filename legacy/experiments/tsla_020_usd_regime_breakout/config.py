"""
TSLA TSLA-USD (UUP) Direction Regime-Gated BB Squeeze Breakout (TSLA-020)

實驗動機 (Motivation)：
- TSLA-017 Att3 為當前全域最優（min(A,B) 0.96，Part A Sharpe 1.17 /
  Part B Sharpe 0.96）。約束部位為 **Part B**（Sharpe 0.96，5 訊號
  4W/1SL），唯一殘餘綁定 SL = **2024-09-23**（進場 2024-09-24 254.46 →
  出場 2024-10-10 236.29，-7.14% 停損；2024 年 10/10-10/11「We, Robot」
  robotaxi 發表會令市場失望、TSLA 兩日重挫 ~9% 的事件驅動假突破）。
- TSLA AI_CONTEXT 明列未來「跨維度」突破方向尚含 ^VXN / DXY direction /
  ^VIX BANDS；空的 remote artifact `tsla_018_dxy_direction_breakout`
  為人類 PM 指定的下一方向提示（USD/DXY 方向 regime gate）。
- 沿用分支歧異守則：最高 REAL local module = tsla_017 → 本實驗 #018，
  使用自有 module 名稱 `tsla_020_usd_regime_breakout`。

嘗試方向（人類 artifact 提示方向；GLD-016 Att1 已證明之 cross-asset
divergence regime gate **family** 形式之 USD 移植）：
**在 TSLA-017 Att3 框架上疊加 USD（UUP）20 日動能 regime gate**
（GLD-016 Att1 UUP 20d CEILING 直接 family 形式；TSLA 為 risk-on 成長股，
結構性 USD-inverse 假設：強勢 USD = risk-off / 流動性收緊 → 高 beta 成長股
突破易為假突破）。

================================================================================
預先分析（predict→confirm，**先做** — 與既往 3 SUCCESS + 10 documented-failure
方法論一致）
================================================================================
重現 TSLA-017 Att3 全部 15 筆交易，量測 signal-day 多個正交維度，
檢驗綁定 Part B SL（2024-09-23）能否與 TP winners 分離：

  維度          | B_SL 2024-09-23 | Part B winners 區間 | 全部 winners 區間
  --------------|-----------------|---------------------|-------------------
  ^VXN level    |  19.5           | [15.1, 22.3]        | [14.0, 30.8]
  ^VXN 3d       |  -3.2           | [-4.2, -0.1]        | [-5.5, 0.0]
  ^VXN 5d       |  -3.0           | [-4.3, -0.2]        | [-4.3, 0.1]
  ^VXN 10d      |  -4.4           | [-6.3, 0.7]         | [-6.3, 0.7]
  ^VIX level    |  15.9           | [12.6, 18.4]        | [12.1, 30.4]
  ^VIX 3d       |  -2.3           | [-5.2, -0.4]        | [-6.6, 0.7]
  **DXY 20d%**  |  **+0.20**      | **[-0.31, +2.01]**  | **[-3.11, +2.01]**
  TSLA-SPY 20d% |  +11.82         | [+6.70, +29.04]     | [+5.86, +29.04]
  TSLA-QQQ 20d% |  +12.70         | [+6.43, +28.57]     | [+4.82, +28.57]
  TSLA 60d%     |  +26.6          | [-10.6, +69.4]      | [-10.8, +125.0]
  TSLA 120d%    |  +50.0          | [-17.6, +107.7]     | [-31.0, +170.9]
  RV20 (日%)    |  3.65           | [2.32, 4.15]        | [1.59, 5.35]

★ **結論：綁定 Part B SL（2024-09-23）在所有測試正交維度上皆完全
  落在 Part B winners 區間內（INSIDE，完全 interleaved）——無任何
  separable 維度、無 ≥15pp robust plateau。**
  - USD（DXY 20d）維度：SL = +0.20%，winners 區間 [-0.31, +2.01]。
    TSLA 兩筆最佳 Part B winners（2024-12-06 Trump/Musk 選後 melt-up
    DXY20d **+1.40**；2025-05-12 關稅緩解反彈 DXY20d **+2.01**）皆發生於
    **比 SL 更強的 USD regime** → USD CEILING **方向反轉**（會過濾
    真 winners 而非 SL），與 SIVR-019 同構（best winners 出現於
    strong-USD regime）。
  - TSLA 不是 USD-driver-pure：其 drawdown 為公司事件驅動
    （2024-09 We-Robot robotaxi 發表會失望、交付數據、Musk 言論），
    與 USD regime 解耦——違反 cross-asset divergence regime gate
    family v4 的 DRIVER-PURE 先決條件（SIVR-019/EWT-010 driver-impurity
    class）。
  - 長期 prior-return（T60d/T120d）：SL +26.6%/+50.0% 深陷 winners
    區間內；最佳 winner 2024-12-06 T60d **+69.4%** / T120d **+107.7%**
    （run-up 遠高於 SL）仍為 +10% TP → 證實 FCX-016 lesson #36d：
    對 BREAKOUT 框架，高 prior-return 為「momentum-continuation
    生產性 regime」而非 trap；URA-014 post-parabola CEILING 在此
    **方向反轉**。

**預測：documented-failure**（與 memory 對 TSLA-017「likely
documented-failure」之判斷一致；predict→confirm 軌跡 3 SUCCESS +
10 documented-failure 全部正確預測）。本實驗以 3 次迭代 **confirm**
此預測並記錄跨資產規則。

================================================================================
迭代紀錄（三次迭代，2026-05-17）— 預測 documented-failure，**全部 confirm**
================================================================================
Baseline = TSLA-017 Att3：Part A 10/80%/Sharpe 1.17 / Part B 5/80%/
Sharpe 0.96 / min(A,B) **0.96**。

Att1 (use_usd_ceiling, max_usd_return = 0.00；GLD-016 Att1 UUP CEILING
  family 形式直接移植)：**FAIL — 方向反轉，confirm 預測**
  Part A 8/62.5%/Sharpe **0.54**（-54%；chain-shift 新增 2019-07-15 SL）
  Part B 2/50.0%/Sharpe **0.17** cum +2.15%（-82%）
  min(A,B) **0.17**（-82% vs baseline 0.96）。
  - 綁定 Part B SL（2024-09-23，shift 後 2024-09-24，UUP20d≈+0.20%）
    **未被移除**；CEILING ≤0.0 反而誤殺全部高-USD Part B winners
    （2024-06-26 +1.38 / 2024-12-06 +1.40 / 2025-05-12 +2.01，皆 +10%
    TP），Part B 5→2、winners 4→1。完全 **方向反轉**（SIVR-019 同構：
    best winners 出現於 strong-USD regime）。

Att2 (max_usd_return = +0.015，CEILING 放寬至 +1.5%，robustness probe)：
  **FAIL — non-binding on SL，confirm 預測（SIVR-019 Att1 同構）**
  Part A 10/80.0%/Sharpe **1.17**（與 baseline 完全相同，非綁定）
  Part B 4/75.0%/Sharpe **0.77** cum +23.60%（-20%）
  min(A,B) **0.77**（-20% vs baseline 0.96）。
  - SL 2024-09-23（+0.20 ≤ +1.5）**通過未過濾**，gate 對 SL 非綁定；
    仍誤殺最高-USD winner 2025-05-12（+2.01 > +1.5），Part B 5→4。

Att3 (use_usd_divergence_floor, min_tsla_minus_usd = 0.0；TLT-014 /
  GLD-016 Att2 相對背離 FLOOR 形式)：**FAIL — 完全非綁定，confirm 預測
  （SIVR-019 Att2 同構）**
  Part A 10/80.0%/Sharpe **1.17**（與 baseline 完全相同）
  Part B 5/80.0%/Sharpe **0.96**（與 baseline 完全相同）
  min(A,B) **0.96**（0% 改善，TIE）。
  - TSLA 20d 報酬遠高於 UUP 20d 報酬（TSLA vol ≫ USD vol），
    TSLA−USD ≥ 0 對每筆訊號（含 SL）皆成立 → FLOOR 零區分力，
    SL 未被孤立。

最終配置：Att3（committed default，least-harmful baseline-tie）。
**結論：3 次迭代全部 FAIL/TIE，confirm predict→confirm 預測。
TSLA-017 Att3（min(A,B) 0.96）仍為 TSLA 全域最優；TSLA-020 REJECT。**

================================================================================
跨資產貢獻（新規則 — cross_asset_lessons 禁忌 #36e）
================================================================================
**cross-asset divergence regime gate family v4 driver-purity 先決條件
之第 3 個 documented-failure subclass：HIGH-VOL SINGLE GROWTH STOCK
vs USD（繼 SIVR-019 metal-vs-USD、EWT-010 component-vs-parent）。**
- TSLA 為 risk-on 高 beta 成長股，直覺上「強勢 USD = risk-off」應與
  TSLA 反向；但 TSLA 的 breakout-SL 為**公司事件驅動**（2024-09
  We-Robot robotaxi 發表會失望、交付數據、Musk 言論），與 USD
  regime **解耦**——非 DRIVER-PURE。
- 結構性反轉證據：TSLA 兩筆最佳 Part B winners（2024-12-06 Trump/
  Musk 選後 melt-up DXY20d +1.40；2025-05-12 關稅緩解 +2.01）皆於
  **strong-USD regime**，綁定 SL 則為 flat-USD（+0.20）→ USD CEILING
  方向反轉（誤殺 winners，SIVR-019 silver 同構）；相對背離 FLOOR
  因 TSLA vol ≫ USD vol 而恆非綁定。
- TSLA 殘餘 Part B SL 2024-09-23 加入 **idiosyncratic-non-separable
  single-residual-SL family**（NVDA-018 ^VXN / TSM-012 / EWJ-006 /
  INDA-013 / DIA-013 同構）：高波動單一個股之事件驅動假突破於
  ^VXN/^VIX/DXY/TSLA-SPY/TSLA-QQQ/T60d/T120d/RV20 **全部正交維度**
  與 winners 完全 interleaved。
- 結論：**不要將 USD/DXY direction regime gate 移植至高波動單一
  成長股**（TSLA/NVDA-class）；USD 適用性為 GOLD-SPECIFIC（貨幣
  純度），成長股 drawdown 為公司事件驅動非 USD-regime-separable。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA020Config(ExperimentConfig):
    """TSLA-020 TSLA-USD(UUP) Direction Regime-Gated BB Squeeze Breakout 參數

    Base = TSLA-017 Att3（BB Squeeze + buffered SMA regime + TSLA-QQQ 20d
    divergence ≥ -0.5%），疊加 USD（UUP）20d regime gate。
    預測 documented-failure（predict→confirm，pre-analysis 先做）。
    """

    # === BB Squeeze Breakout 基礎（同 TSLA-017 Att3 / TSLA-015 Att3）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === Same-Asset Multi-Week Trend Regime（同 TSLA-017 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.99

    # === TSLA-QQQ Cross-Asset Divergence Regime Gate（沿用 TSLA-017 Att3）===
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    min_relative_return: float = -0.005

    # === USD (UUP) Direction Regime Gate（TSLA-020 核心新增）===
    # usd_benchmark：UUP（Invesco DB USD Index Bullish；GLD-016/SIVR-019 同款）
    # usd_lookback：20 日（與 GLD-016 Att1 一致）
    # use_usd_ceiling=True：保留訊號需 UUP 20d return <= max_usd_return
    #   （絕對 USD 動能 CEILING，GLD-016 Att1 已證明之 family 形式）
    # use_usd_divergence_floor=True：保留訊號需 (TSLA 20d − UUP 20d)
    #   >= min_tsla_minus_usd（相對背離 FLOOR，TLT-014/GLD-016 Att2 形式）
    usd_benchmark: str = "UUP"
    usd_lookback: int = 20
    use_usd_ceiling: bool = False
    max_usd_return: float = 0.015  # Att1=0.00 / Att2=0.015 (ceiling 已測畢)
    use_usd_divergence_floor: bool = True
    min_tsla_minus_usd: float = 0.0  # Att3：相對背離 FLOOR（GLD-016 Att2 形式）


def create_default_config() -> TSLA020Config:
    return TSLA020Config(
        name="tsla_020_usd_regime_breakout",
        experiment_id="TSLA-020",
        display_name="TSLA TSLA-USD(UUP) Direction Regime-Gated BB Squeeze Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
