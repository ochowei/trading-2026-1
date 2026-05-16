"""TQQQ-029 TQQQ Donchian Channel Trend-Following 配置

策略方向：**趨勢跟蹤 (Trend Following)** — repo 中 TQQQ 未曾以純 Donchian
通道突破趨勢跟蹤框架測試（TQQQ-006 為動量崩潰做空型、TQQQ-015 為 QQQ
動量/突破、TQQQ-028 為 BB squeeze 突破；皆非 Turtle 式 N 日高點 Donchian
趨勢跟蹤）。

實驗動機 (Problem statement)：
- leveraged tech ETF 長期 secular uptrend（NDX 2019-2025 大牛），理論上
  Turtle 式「N 日新高 + 趨勢確認」順勢做多可吃 3x 趨勢段。
- TQQQ-028（BB squeeze breakout）已證明純突破在 3x whipsaw；TQQQ-029
  改以「Donchian N 日高點突破 + 長期趨勢 regime 過濾」測試是否能以
  趨勢確認壓制 whipsaw。

迭代計畫（最多三次）：
- Att1: Close > Donchian(20) 高點 + Close > SMA50，TP+12%/SL-8%/20d
- Att2: 視 Att1 結果 tune Donchian 週期 / 趨勢 SMA / 出場
- Att3: 替代維度 — 加 SMA200 bull regime 或拉長 Donchian 週期

跨資產脈絡：
- 對比 TQQQ-015（QQQ 動量）/ TQQQ-028（TQQQ BB 突破）皆失敗——
  TQQQ-029 測試 Donchian 趨勢跟蹤 + regime 過濾是否突破 leveraged ETF
  「僅 MR/capitulation 維度有效」之邊界（lesson #5）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQ029Config(ExperimentConfig):
    """TQQQ-029 TQQQ Donchian Channel Trend-Following 參數"""

    # Att1: donchian=20, trend_sma=50, bull off → Part A 50/56.0%/Sharpe
    #   0.28 / Part B 19/42.1%/Sharpe -0.01 cum -9.67% → min -0.01 REJECT
    #   （Donchian whipsaw 嚴重，Part B 42% WR 19 SL）
    # Att2: donchian=55 + trend_sma=100 + SMA200 bull → Part A 34/61.8%/
    #   Sharpe 0.42 / Part B 16/43.8%/Sharpe 0.01 cum -4.52% → min 0.01
    #   REJECT（whipsaw 減少但 Part B 仍 44% WR 負報酬）
    # Att3 ★ (saved as default): donchian=100 (ultra-long major-trend) +
    #   trend_sma=150 + SMA200 bull + 拉寬出場 TP+20%/SL-10%/30d（給
    #   3x 趨勢段空間，避免 -8% SL 在 uptrend 正常回檔被洗）
    donchian_period: int = 100  # 當日 Close > 前 N 日 High 之 rolling max
    trend_sma_period: int = 150  # 中期趨勢確認 Close > SMA(trend_sma_period)

    use_bull_filter: bool = True
    bull_sma_period: int = 200  # 長期 bull regime（Close > SMA200）

    cooldown_days: int = 10
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ029Config:
    return TQQQ029Config(
        name="tqqq_029_donchian_trend",
        experiment_id="TQQQ-029",
        display_name="TQQQ Donchian Channel Trend-Following (TQQQ-native)",
        tickers=["TQQQ"],
        data_start="2018-06-01",  # 暖機 Donchian / SMA
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.20,
        stop_loss=-0.10,
        holding_days=30,
    )
