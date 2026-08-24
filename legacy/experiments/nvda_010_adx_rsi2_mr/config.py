"""
NVDA-010: ADX-Filtered RSI(2) Mean Reversion

動機（Motivation）：
    NVDA 全域最佳 NVDA-004 / NVDA-006 min(A,B) 皆為 0.47，瓶頸都在 Part A
    2019-2023 多 regime 期（2020 COVID / 2021 late-bull / 2022 bear /
    2023 summer chop）。NVDA-009 MBPC 在 Part B 純趨勢期 Sharpe 0.96 極佳，
    但 Part A 因 regime 混合僅 0.41。

    **本實驗探索 repo 中尚未使用的「ADX 趨勢強度閘門 + 短期超賣 MR」方向**。
    repo 中 ADX/DMI（Average Directional Index / Directional Movement
    Index）尚未作為主過濾器使用過——所有實驗皆以 SMA / BB / ATR ratio /
    pullback 作為 regime 過濾。ADX 直接衡量「方向性趨勢強度」，與 SMA
    （價格相對位置）、ATR（波動率）為互補資訊。

    假設（Hypothesis）：NVDA 在 ADX(14) >= 25 的「強趨勢」期間，淺回檔的
    短期超賣（RSI(2) < 15）為高勝率 MR 進場；在 ADX < 25 的「無趨勢/盤整」
    期間（如 2023 summer chop），RSI(2) MR 失效。+DI > -DI 進一步要求方向
    為多頭（避開 2022 bear market）。

策略方向：均值回歸（Mean Reversion）
    短期超賣 MR 進場，但僅限於強多頭趨勢的 regime 中。

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價
    - 滑價：0.15%
    - 悲觀認定：是

迭代歷程（Iteration Log）：

Att1（Baseline）—— ADX>=25 + +DI>-DI + RSI(2)<=15 + Pullback[-3%,-10%] + cd10
    結果：
        Part A: 3 訊號（0.6/yr）, WR 66.7%, 累計 +3.88%, Sharpe **0.26**
        Part B: 1 訊號, WR 0%, 累計 -6.14%, Sharpe **0.00**（zero-var SL）
        min(A,B): **0.00**
    失敗分析：
        - 多重綁定過嚴：ADX>=25 ∧ RSI(2)<=15 ∧ +DI>-DI ∧ 淺回檔
          僅 0.6 訊號/yr，統計樣本不足
        - 強趨勢中 RSI(2)<=15 罕見發生（持續下挫才會觸發，但下挫期間
          +DI<<-DI 必然違反方向過濾），交集結構性狹窄
        - Part B 2024-04-02 唯一訊號 -6.14% SL：規範 ADX regime 正確
          但 mid AI 修正並非超賣耗盡

Att2（Based on Att1）—— 放寬至 ADX>=20 + RSI(2)<=20 + Pullback[-2%,-12%] + cd8
    調整：
        - ADX 25 → 20
        - RSI(2) 15 → 20
        - Pullback [-3%,-10%] → [-2%,-12%]
        - cd 10 → 8
    結果：
        Part A: 8 訊號（1.6/yr）, WR 62.5%, 累計 +9.00%, Sharpe **0.22**
        Part B: 1 訊號, WR 0%, 累計 -6.14%, Sharpe **0.00**（zero-var SL）
        min(A,B): **0.00**（Part B 仍卡在 1 訊號）
    失敗分析：
        - Part A Sharpe 退化（0.26→0.22）—— 新增 5 中等品質訊號（3 TP +
          2 expiry）稀釋集中贏家
        - Part B 仍只 1 訊號：NVDA 2024-2025 深度修正（2024-08 -17%、
          2025-04 tariff -25%）違反 (a) -12% pullback 上限、(b) Close >
          SMA(50) 規範閘門（深跌跌破 50 日 MA）、或 (c) +DI>-DI（DMI
          快速崩盤期間翻轉至 bear）
        - 結構不匹配：Part B 的 MR 機會在於深層 capitulation 事件，
          違反「強趨勢中淺回檔」框架

Att3（Based on Att2）—— 移除 +DI>-DI + RSI(3)<=25 + Pullback to -15%
    調整：
        - require_bullish_dmi: True → False（讓 SMA(50) 處理方向）
        - RSI(2)<=20 → RSI(3)<=25（更平滑振盪器）
        - pullback_max -12% → -15%（捕捉 Part B AI 修正）
    結果：
        Part A: 8 訊號, WR **37.5%**（4 連續 SL！）, 累計 -13.24%, Sharpe **-0.27**
        Part B: 2 訊號, WR **0%**, 累計 -11.90%, Sharpe **0.00**（zero-var）
        min(A,B): **-0.27**（三次中最差）
    失敗分析：
        - cooldown chain shift（lesson #19）：移除 +DI>-DI 釋放原本被
          壓制的訊號（2020-02-24 pre-COVID drop / 2021-02-23 Feb 修正 /
          2021-12-06 post-COVID 反彈 / 2022-12-20 bear 反彈）—— 4 筆
          全部 SL。+DI>-DI 原本提供真實品質過濾，naively 移除後框架退化
        - Part B 2024-04-02（mid AI rally pullback）+ 2025-08-20（後期
          反彈）皆 SL —— 較寬 pullback 範圍捕捉的是 continuation-decline
          事件而非 capitulation reversal（平行 lesson #20b oscillator-hook
          失敗：bear-rally dead-cat bounce in mid-decline）
        - Part A WR 62.5%（Att2）→ 37.5%（Att3）確認 +DI>-DI 為真實
          品質過濾，無替代下移除使框架退化

**三次迭代全部失敗結論**（最佳 Att1 min 0.00、最差 Att3 min -0.27，全部
低於 NVDA-004 / NVDA-006 的 0.47）：

1. **ADX/DMI 作為主規範閘門對 NVDA 高波動個股 MR 結構性無效**：
   - ADX>=25 strong-trend regime 與 deep oversold（RSI(2)<=15）罕見共存：
     RSI(2)<=15 需持續下挫，但持續下挫使 +DI<<-DI 必然違反方向過濾
   - ADX>=20 weak-trend regime 過於包容——納入震盪 2023 summer，使 MR
     訊號隨機化
   - +DI>-DI 提供真實選擇性，但與 Close>SMA(50) 大部分時間冗餘；移除後
     觸發 cooldown-chain-shift

2. **Part B 2024-2025 NVDA AI 牛市的 MR 機會結構性與「淺回檔 MR」框架
   不匹配**：深度 AI 修正（-17%、-25%）違反 pullback 上限或 SMA 規範，
   而 framework 內可觸發訊號皆為 mid-decline 假反彈。

3. **repo 首次 ADX/DMI 主過濾器試驗失敗**——擴展 lesson #6（確認指標
   邊際效益遞減）至 ADX/DMI 類別；擴展 lesson #20b 邊界：trend-strength
   oscillators（ADX）加入 RSI/CCI/Stoch/MACD hook divergence 作為
   多 regime 高波動個股的無效進場主過濾器。

4. **NVDA 結構性 Sharpe 上限約 0.5**——2019-2023 多 regime 變異使單一
   參數集難以同時優化 Part A/B；NVDA-004（BB Squeeze）/ NVDA-006（RS）
   維持全域最優 0.47。

最終參數（保留 Att3 為三次最寬鬆變體，後續實驗應改變方向而非繼續精煉）：
    adx_period: 14
    adx_threshold: 20.0（Att1 25 過嚴 / Att3 20 過寬，皆失敗）
    require_bullish_dmi: False（Att1/Att2 True / Att3 False，皆失敗）
    rsi_period: 3（Att1/Att2 RSI(2) / Att3 RSI(3)，差異邊際）
    rsi_threshold: 25.0
    pullback_lookback: 5
    pullback_min: -0.02 / pullback_max: -0.15
    cooldown_days: 8
    出場：TP +6% / SL -6% / 15 天 / 滑價 0.15%
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA010Config(ExperimentConfig):
    """NVDA-010 ADX-Filtered RSI(2) Mean Reversion 參數"""

    # ADX / DMI 趨勢強度閘門（repo 首次使用）
    adx_period: int = 14
    adx_threshold: float = 20.0  # Att3: 維持 20
    require_bullish_dmi: bool = False  # Att3: 移除 +DI>-DI（讓 SMA(50) 處理方向）

    # 短期超賣觸發
    rsi_period: int = 3  # Att3: RSI(2) → RSI(3)（更平滑、Part B 訊號密度提升）
    rsi_threshold: float = 25.0  # Att3: RSI(3) <= 25（與 RSI(2)<=20 等效嚴度但分布更穩）

    # 中期趨勢過濾
    sma_trend_period: int = 50

    # 淺回檔範圍 (NVDA ~3.26% vol)
    pullback_lookback: int = 5
    pullback_min: float = -0.02  # 上限：至少回檔 2%
    pullback_max: float = -0.15  # Att3: -12% → -15%（捕捉 Part B 較深 AI 修正）

    # 多頭 K 棒確認
    bullish_close_required: bool = True

    # 冷卻期
    cooldown_days: int = 8


def create_default_config() -> NVDA010Config:
    return NVDA010Config(
        name="nvda_010_adx_rsi2_mr",
        experiment_id="NVDA-010",
        display_name="NVDA ADX-Filtered RSI(2) Mean Reversion",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.06,
        stop_loss=-0.06,
        holding_days=15,
    )
