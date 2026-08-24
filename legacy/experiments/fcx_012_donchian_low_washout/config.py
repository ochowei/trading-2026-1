"""
FCX Donchian Lower Washout + Intraday Reversal MR 配置 (FCX-012)

動機：FCX-004 Att2（BB Squeeze Breakout，min(A,B) 0.41）與 FCX-001
（grandfathered 三重極端超賣，Sharpe 0.43/0.74 但無成交模型）為 FCX
當前執行模型最佳。FCX-001 的 Part A/B 累計報酬差距 72%（90.41% vs
25.34%）超出「<30%」目標，FCX-004 的 Part B 訊號僅 4（breakout 頻率低）。

已窮盡方向：MR (FCX-001/002/003/008/009/011)、Breakout (FCX-004/007)、
Momentum (FCX-005/006)、Gap-Down (FCX-010)。共 11 次實驗。

本實驗探索 **repo 首次「Donchian Lower Washout + 日內反轉」組合**作為
MR 主進場訊號：

1. Donchian 20 日低點作為非參數化的「真實洗盤」觸發器（binary，不受
   pullback % 閾值影響），與 FCX-002 的 pullback %% 基於 close 計算不同
2. 進場要求「今日或昨日確實觸及 20 日新低」，過濾離新低較遠但因 pullback %
   符合門檻的訊號
3. 保留日內反轉結構（ClosePos >= 40%）與波動率放大（ATR(5)/ATR(20) >= 1.10）
   做為品質過濾
4. 60 日回撤範圍約束於 [-30%, -10%]——排除結構性熊市（> -30%）與
   淺漂移（< -10%），避免 FCX-001 的 Part A/B 累計報酬 72% gap 再現

Donchian Lower 與其他 FCX 進場方式的差異：
- FCX-001：SMA50 deviation + DD 60d + RSI10（3 個連續閾值）
- FCX-002：pullback 10d + WR + reversal candle（close-based pullback）
- FCX-007：Donchian **HIGH** 突破（趨勢跟蹤，與本實驗方向相反）
- FCX-010：隔夜 Gap-Down + 日內反轉（only overnight）
- FCX-011：BB 下軌 + pullback cap（統計自適應 BB）
- FCX-012：**Donchian LOW** 觸及 + 日內反轉（price-at-recent-low，非統計量）

直覺：FCX 作為銅礦個股，commodity panic 常以「連續下跌 + 某日觸及新低 +
盤中買盤湧入」模式結束。Donchian Low 觸及比統計 BB 下軌更為 binary：
BB 在高波動期帶寬持續擴大，BB 下軌可被頻繁觸及但不代表真實底部；
Donchian 新低是 unambiguous washout 事件。此設計針對 FCX 之 event-driven
commodity panic 結構（2016 信貸、2020 COVID、2022 銅價暴跌）。

波動度縮放參考：FCX ~3% 日波動
- 60 日回撤範圍 [-30%, -10%]：FCX-001 用 ≤-18%，FCX-009 用 [-9%,-18%]
- ClosePos >= 40%：與 FCX-009 Att1/FCX-011 一致
- ATR(5)/ATR(20) >= 1.10：FCX-008 驗證 1.05 退化 Part A，FCX-011 用 1.15
  稍嚴，1.10 為中間值
- TP +9% / SL -11%：尊重 FCX MR SL -12% 下限（lesson #43），TP 介於
  FCX-001 (+10%) 與 FCX-004 (+8%) 之間
- 冷卻 15 天：與 FCX-001 一致，避免同一下跌週期多次進場

========================================================================
三次迭代記錄（2026-04-23，成交模型 0.15% slippage，隔日開盤市價進場）：
========================================================================

**Att1：基線 Donchian Low Washout + Intraday Reversal（失敗）**
  - Close 距 20 日低點 <= 2.5% + (今日或昨日 Low = 20d Low) + ClosePos >= 40%
    + ATR(5)/ATR(20) >= 1.10 + 60d DD ∈ [-30%, -10%]
  - TP +9% / SL -11% / 20d / cd 15
  Part A: 8 訊號 WR 50% cum -8.16% Sharpe **-0.06**
    - 2019-08-05 SL -11.13%（貿易戰升溫日，washout-day acceleration）
    - 2021-06-16 Expiry -12.36%（6 月銅價頂部後 ~30% 下跌中段）
    - 2021-08-19 TP +9% / 2021-09-20 TP +9%
    - 2022-09-23 TP +9%（Fed 升息恐慌 + 中國放緩）
    - 2023-04-25 SL -11.13%（3 月高點後 drift）
    - 2023-09-25 Expiry -6% / 2023-10-23 TP +9%
  Part B: 6 訊號 WR 50% cum -0.93% Sharpe **0.02**
    - 2024-01-17 Expiry +1.54% / 2024-07-19 SL -11.13%（夏季銅價暴跌）
    - 2024-11-12 Expiry -4.90% / 2024-12-13 Expiry -2.83%
    - 2025-03-04 TP +9% / 2025-09-26 TP +9%
  min(A,B) **-0.06**（vs FCX-004 的 0.41，大幅不如）
  失敗分析：兩筆 Part A -11% SL（2019-08-05、2023-04-25）為 continuation-
    decline 陷阱——Donchian Low 觸及但後續續跌。Part B 三筆到期報酬微幅
    （2024-01/11/12），顯示 washout 訊號在 side-way 環境缺乏觸發動能。

**Att2：疊加 require_higher_low_today=True（Day-After Capitulation，失敗）**
  - 其餘同 Att1；新增條件：今日 Low > 昨日 Low
    （搭配 washout_lookback=2 → 昨日 Low = 新低、今日不再探底）
  Part A: 1 訊號（2021-06-16 Expiry -12.36% Sharpe 0.00 零方差）
  Part B: 2 訊號（2024-01-18 Expiry +0.30% / 2025-09-26 TP +9% Sharpe 1.07）
  min(A,B) **-0.60**（Part A 單筆虧損 Sharpe 無法計算，以單筆報酬近似）
  失敗分析：Day-After 條件過度過濾——「washout-day + 今日不再探底」在 FCX
    高波動個股上極稀疏，Part A/B 共 3 訊號無統計意義。**驗證 lesson #20b
    Day-After Capitulation 失敗家族於 FCX 3% vol 單一商品個股**（繼 URA
    2.34%/TLT 1% 利率驅動後）。

**Att3：回退 Att2，改加 2DD cap >= -7%（CIBR-012 方向，失敗）**
  - 其餘同 Att1；新增條件：2 日收盤報酬 >= -7%（排除崩盤加速中進場）
  Part A: 7 訊號 WR 42.9% cum -15.74% Sharpe **-0.20**（**WORSE than Att1**）
    - 2DD cap 僅移除 1 筆 TP（未移除 SL），WR 從 50% 降至 42.9%
  Part B: 6 訊號 WR 50% cum -0.93% Sharpe **0.02**（不變——Part B 所有訊號
    2DD 均 > -7%，cap 對 Part B 結構性非綁定）
  min(A,B) **-0.20**
  失敗分析：CIBR-012 成功的 2DD cap -4% 方向在 FCX 上失效——FCX winners
    的 2DD 分布橫跨 -3% 至 -8%，輸家同樣橫跨，cap 無單向選擇力。呼應
    FCX-011 Att2（2DD cap -5% min 0.00，無選擇性）的發現。**擴展 lesson
    #52 至「2DD cap 在高波動單一商品個股無選擇力」**——與 CIBR
    1.53% vol tech ETF 成功結構相反。

========================================================================
**核心失敗根因**（跨資產貢獻）：
========================================================================

**Repo 第 1 次「Donchian Lower Washout + 日內反轉」組合作為 MR 主進場
試驗——三次迭代全部失敗**。

1. **Donchian Lower 觸及為「反轉候選」而非「反轉確認」**：
   在 FCX ~3% vol 上，commodity panic 常以多日連續 Donchian 新低為特徵
   （2019-08 trade war、2021-06 銅價頂部後、2022 夏秋升息、2024-07 銅價
   暴跌均有 3-5 連續新低日）。單日觸及 + 日內反轉不足以區分「尾段 washout」
   vs「中段 acceleration」。此結果與 FXI-009 Failed Breakdown Reversal
   三次迭代失敗（lesson #52）同源——binary 價格觸發器在「多段下跌」結構
   資產上缺乏區分力。

2. **Day-After Capitulation 對 FCX 同樣失效**（lesson #20b 延伸至 FCX
   3% vol 個股）：強反轉結構過嚴使訊號崩至 1-3 筆，無統計意義。URA 2.34%
   policy-driven、TLT 1% rate-driven、FCX 3% commodity-driven 三個資料點
   均確認：單日 price-action 反轉確認在「多階段下跌」資產上結構性失敗。

3. **2DD cap（CIBR-012 方向）在 FCX 無選擇力**：
   CIBR 成功的「淺 2DD = 減速、深 2DD = 加速」區分在 FCX 上不成立，
   FCX winners 與 losers 的 2DD 分布重疊。呼應 FCX-011 Att2 深 2DD cap -5%
   min 0.00 的非選擇性結果——FCX 高波動單一商品個股的多日持續下跌結構使
   任何單一 window（2DD/ATR/close-relative）的 cap/floor 方向均無選擇力。

FCX-004 (BB Squeeze Breakout, min 0.41) 仍為 FCX 執行模型最優。
FCX-001 (grandfathered extreme oversold, Sharpe 0.43/0.74 但 A/B gap 72%)
為全域最佳但非 execution-model 實驗。

FCX 第 12 種失敗策略類型（前 11 種：MR/Breakout/Momentum/Pair/Trend/
RS/Donchian-Upper/2DD-filter-combos/RSI-hook/Gap-Down/BB-lower-hybrid）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX012Config(ExperimentConfig):
    """FCX-012 Donchian Lower Washout + Intraday Reversal MR 參數"""

    # Donchian Lower 參數
    donchian_period: int = 20
    # Close 相對 20 日低點的最大距離（越接近新低越好）
    # 0.025 表示 Close 需在 20 日低點上方 2.5% 以內
    close_near_low_threshold: float = 0.025

    # 是否要求「今日或昨日 Low = 20 日低點」作為真實 washout 確認
    require_washout_day: bool = True
    # 「昨日 Low = 20 日低點」視窗（過去 N 個交易日內出現新低）
    washout_lookback_days: int = 2

    # Att2: 要求今日 Low 高於昨日 Low（Day-After 反轉結構）。
    # 設為 True 時搭配 washout_lookback_days=2 表示「昨日 Low = 新低，
    # 今日 Low 不再探底」——Key Reversal Day 模式。
    # Att2 結果：過度過濾（Part A 1 訊號、Part B 2 訊號），棄用。
    require_higher_low_today: bool = False

    # Att3: 2 日收盤報酬上限（cap）過濾——排除「in-crash acceleration」進場
    # 直覺：2DD 深（≤-7%）= 崩盤加速中；2DD 淺（>-7%）= 減速階段，MR 較穩定
    # 2DD -7% = 1.65σ for FCX ~3% vol (2-day)
    # 參考 CIBR-012 Att3 方向（CIBR -4% 2DD cap 成功，+26% Sharpe 改善）
    use_twoday_cap: bool = True
    twoday_return_cap: float = -0.07

    # 日內反轉
    close_pos_threshold: float = 0.40

    # 波動率放大（signal-day panic）
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10

    # 60 日回撤範圍（排除結構性熊市 / 淺漂移）
    drawdown_lookback: int = 60
    drawdown_upper: float = -0.10  # 回撤必須 <= -10%（深度不足則過淺）
    drawdown_lower: float = -0.30  # 回撤必須 >= -30%（過深則結構性崩潰）

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> FCX012Config:
    return FCX012Config(
        name="fcx_012_donchian_low_washout",
        experiment_id="FCX-012",
        display_name="FCX Donchian Lower Washout + Intraday Reversal MR",
        tickers=["FCX"],
        data_start="2015-01-01",
        profit_target=0.09,
        stop_loss=-0.11,
        holding_days=20,
    )
