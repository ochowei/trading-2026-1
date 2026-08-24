"""
FCX Post-Capitulation Vol-Transition 均值回歸配置 (FCX-011)

動機：VGK-008 Att2（2026-04-22）跨資產假設：

  「2DD floor/cap 方向可能擴展至 (a) 更多已開發寬基 ETF 與 (b) 非傳統板塊
  ETF (CIBR 驗證 cap 方向)。**高波動單一個股（single stock）為待驗證之
  開放邊界**。」

BB 下軌 + 回檔上限混合進場模式已在中低波動（1.12%~1.75%）寬基/板塊 ETF
驗證成功：
- VGK 1.12% vol：min(A,B) 0.49 (VGK-007) / 2.60 (VGK-008 Att2 加 2DD floor)
- INDA 0.97% vol：min(A,B) 0.20 (INDA-008) / 0.30 (INDA-010 Att3 加 2DD floor)
- EWT 1.41% vol：0.57 (EWT-008)
- EEM 1.17% vol：0.34 (EEM-012) / 0.56 (EEM-014 Att2 加 2DD floor)
- EWZ 1.75% vol：0.69 (EWZ-006)
- CIBR 1.53% vol：0.39 (CIBR-008) / 0.49 (CIBR-012 Att3 加 2DD cap)

**XBI-010 驗證上限為日波動 1.75%**（XBI 2.0% vol 失敗）。本實驗為
**repo 第 1 次 BB 下軌 + 回檔上限混合進場模式於高波動單一個股試驗**
（FCX ~3% vol），探索混合模式邊界是否因「單一個股 vs ETF」類別差異
而延伸。

假設：FCX 為銅礦龍頭單一個股（Freeport-McMoRan），具股權資本化動態
（非純商品宏觀重新定價）——2016 信貸壓力、2020 COVID、2022 銅價暴跌
均呈現經典急跌反彈結構。若成立，BB 下軌 + 回檔上限混合進場應能捕捉
FCX 的「慢漂移 vs 真恐慌」區分。

FCX 參數按波動度縮放（~2.7x VGK vol）：
- 回檔上限：VGK -7% → FCX -15%
- 2DD 門檻：VGK 2.0% → FCX 5%（1.18σ @ 1-day vol, 0.83σ @ 2-day vol）
- TP/SL：遵循 FCX 硬上限（MR SL -12%，混合模式典型 SL -7%）

========================================================================
三次迭代記錄（2026-04-22，成交模型 0.15% slippage，隔日開盤市價進場）：
========================================================================

**Att1：基線混合進場（無 2DD 過濾）**
  - BB(20, 2.0) + PB cap -15% + WR <= -80 + ClosePos >= 40% + ATR > 1.15
  - TP +6% / SL -7% / 20d / cd 10
  Part A: 3 訊號 WR 66.7% cum +4.34% Sharpe **0.26**
    - 2020-01-22 TP +6% / 2021-06-16 TP +6% / 2023-03-13 SL -7.14%
  Part B: 5 訊號 WR 40.0% cum -7.86% Sharpe **-0.23**
    - 2024-01-17 TP / 2024-07-19 SL / 2024-11-12 expiry -4.90% /
      2024-12-13 SL / 2025-03-04 TP
  min(A,B) **-0.23**（vs FCX-004 min 0.41，崩壞）
  失敗分析：Part B 兩筆快速 SL（1-day / 3-day）顯示進場日後續跌加速，
    混合模式對 FCX 高波動單一個股缺乏辨識力。XBI-010 已驗證 1.75% vol
    上限；FCX ~3% vol 超出甚多，結果符合預期。

**Att2：2DD cap >= -5%（CIBR-012 方向，排除加速崩盤）**
  - 其餘參數同 Att1
  Part A: 2 訊號 WR 50.0% cum -1.57% Sharpe **-0.09**
    - 過濾 2021-06-16 TP +6%（2DD < -5% 深跌，錯殺贏家）
    - 保留 2020-01-22 TP + 2023-03-13 SL（不對稱）
  Part B: 2 訊號 WR 50.0% cum -1.57% Sharpe **-0.09**
    - 過濾 2024-07-19 SL、2024-12-13 SL（正確方向）
    - 但同時過濾 2025-03-04 TP（錯殺贏家）
  min(A,B) **-0.09**（vs FCX-004 0.41，仍大幅崩壞）
  失敗分析：FCX 高波動下，深 2DD（-5% 以下）同時包含贏家（2021-06-16
    深跌反彈）與輸家（2024-07-19 加速崩盤），cap 方向無選擇性。

**Att3：2DD floor <= -5%（VGK/INDA/EEM 方向，排除淺漂移）**
  - 其餘參數同 Att1
  Part A: 1 訊號 WR 100% cum +6.00% Sharpe **0.00**（零方差）
    - 僅保留 2021-06-16 TP（深 2DD 贏家）
    - 過濾 2020-01-22 TP（淺 2DD）+ 2023-03-13 SL（淺 2DD）
  Part B: 4 訊號 WR 50.0% cum -0.78% Sharpe ~0.00
    - 保留 2024-01-17 TP / 2024-07-19 SL / 2024-11-12 expiry / 2025-03-04 TP
    - 過濾 2024-12-13 SL
  min(A,B) **0.00**（零方差，樣本過薄）
  失敗分析：-5% floor 濾掉 Part A 2/3 訊號，訊號密度崩至 0.2/yr；
    Part B 過濾效果有限（1 筆 SL）。FCX 贏家訊號的 2DD 分布橫跨深淺，
    floor 方向過濾贏家多於輸家。

========================================================================
**核心失敗根因**（跨資產貢獻）：
========================================================================

**Repo 第 1 次「BB 下軌 + 回檔上限混合進場模式」於高波動單一個股
（FCX ~3% vol）試驗——三次迭代全部失敗**。

結論：XBI-010 已建立之 1.75% vol 上限**延伸至單一個股類別**。
混合模式不適用於：
- 高波動 ETF（XBI 2.0%）已驗證
- **高波動單一個股（FCX ~3%）現正確認**

FCX 失敗結構分析：
1. BB 下軌觸及頻率高（高波動使 BB 帶寬大，觸及不罕見），但 Part B
   SLs 均於 1-3 日快速出場（加速崩盤 signal-day 過濾不足）
2. 2DD cap / floor 兩方向皆不適用——FCX 贏家的 2DD 分布橫跨 -3% ~
   -8%，與輸家重疊，無單向選擇力（與 CIBR SLs 集中深 2DD、VGK SLs
   集中淺 2DD 之結構不同）
3. FCX 單一個股事件驅動特性（銅價衝擊、公司信用、中國需求）使
   「統計自適應 BB 下軌」無法捕捉獨特事件結構

**整合跨資產規則（擴展 lesson #52）**：
混合進場模式 (BB 下軌 + 回檔上限 + WR + ClosePos + ATR) 適用邊界：
- ✓ 低中波動寬基/板塊/單一國家 ETF（1.12% ~ 1.75% vol）
- ✗ 高波動 ETF（XBI 2.0%，XBI-010 驗證）
- ✗ **高波動單一個股（FCX ~3%，FCX-011 確認）**
- ✗ 政策驅動單一國家 EM ETF（FXI 驗證）
- ✗ 極低波動商品/利率 ETF（GLD/TLT 等，不同失敗結構）

FCX-004 (BB Squeeze Breakout, min 0.41) 仍為 FCX 執行模型最優。
FCX-001 (grandfathered extreme oversold, Sharpe 0.43/0.41) 為全域
最佳但非 execution-model 實驗。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX011Config(ExperimentConfig):
    """FCX-011 Post-Capitulation Vol-Transition MR 參數"""

    # BB 參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離：FCX ~3% vol，10 日高點回檔上限 -15%
    pullback_lookback: int = 10
    pullback_cap: float = -0.15

    # 品質過濾
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.40

    # ATR 當日過濾
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 2 日收盤報酬過濾
    # Att1：use_twoday_filter=False（基線，min -0.23）
    # Att2：direction="cap", threshold=-0.05（min -0.09，贏家過濾過嚴）
    # Att3：direction="floor", threshold=-0.05（min 0.00，訊號過稀疏）
    # 最終配置保留 Att3（floor 方向，作為 docstring 記錄完整三迭代 picture）
    use_twoday_filter: bool = True
    twoday_direction: str = "floor"
    twoday_threshold: float = -0.05

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FCX011Config:
    return FCX011Config(
        name="fcx_011_vol_transition_mr",
        experiment_id="FCX-011",
        display_name="FCX Post-Capitulation Vol-Transition MR",
        tickers=["FCX"],
        data_start="2015-01-01",
        profit_target=0.06,
        stop_loss=-0.07,
        holding_days=20,
    )
