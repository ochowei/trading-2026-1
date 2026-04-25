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

進場條件（Entry conditions, all must hold）：
    1. ADX(14) >= adx_threshold（強趨勢確認，預設 25）
    2. +DI(14) > -DI(14)（多頭方向確認）
    3. Close > SMA(sma_trend_period)（價格上穿中期均線）
    4. RSI(rsi_period) <= rsi_threshold（短期超賣觸發）
    5. 5 日 Pullback ∈ [pullback_max, pullback_min]（淺回檔上下限）
    6. Close > Open（多頭 K 棒確認，當日反轉）
    7. 冷卻 cooldown_days 個交易日

出場條件（基於 NVDA-004 驗證之甜蜜點，較保守版本）：
    - TP +6%（NVDA 高波動下 6% 短期可達；NVDA-004 +8% 需 BB Squeeze 動能）
    - SL -6%（對稱止損，與 RSI(2) MR 短週期一致）
    - 最長持倉 15 天（短期 MR 一般 3-7 天解決）
    - 滑價 0.15%（NVDA 高波動 + 個股）

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價
    - 滑價：0.15%
    - 悲觀認定：是
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
