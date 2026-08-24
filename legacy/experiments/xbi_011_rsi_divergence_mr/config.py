"""
XBI RSI Bullish Divergence + Pullback+WR Mean Reversion 配置 (XBI-011)

基於 XBI-005（pullback 8-20% + WR(10) ≤ -80 + ClosePos ≥ 35%），加入 RSI(14) bullish
hook 過濾器（SIVR-015 驗證之 classical bullish divergence 簡化版）。

Hypothesis: XBI-005 Part B（OOS）Sharpe 0.65 遠優於 Part A 0.36，訊號數 6 vs 21
（A/B 訊號比 3.5:1）。Part A 的 5 個停損多發生於 2021-2022 生技熊市，部分訊號
可能是在 RSI 仍在下探中觸發（持續下跌結構）。RSI(14) bullish hook 過濾可選擇性
移除 Part A 的「持續下跌」訊號，改善 A/B 平衡與 min(A,B) Sharpe。

XBI 日波動 ~2.0% 與 SIVR 1.93% 相近，且 XBI-005 使用 10 日 pullback 回看窗口，
符合 lesson #20b 對該過濾器有效條件之要求（日波動 2-3% + pullback 回看 ≤10 日
+ 已驗證 pullback+WR 框架）。

Based on XBI-005 (pullback 8-20% + WR(10) ≤ -80 + ClosePos ≥ 35%), adds an
RSI(14) bullish hook filter validated by SIVR-015. XBI meets the lesson #20b
generalization criteria (daily vol 2.0% within 2-3% band, 10-day pullback
lookback, pullback+WR framework validated).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI011Config(ExperimentConfig):
    """XBI-011 RSI Bullish Divergence + Pullback+WR 均值回歸參數"""

    # 進場指標（同 XBI-005）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 ≥ 8%
    pullback_upper: float = -0.20  # 回檔 ≤ 20%
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.35

    # 新增：RSI(14) bullish hook 過濾
    # Att1 (5/3.0/35): 過嚴 3/2 訊號 Sharpe 零方差
    # Att2 (5/3.0/40): 7/2 訊號 A/B 不平衡，Part A Sharpe 0.27 < XBI-005 0.36
    # Att3 (5/2.0/35): 保持 SIVR oversold 門檻，放寬 delta 讓淺回升 hook 通過
    # 目的：恢復 Part B 訊號頻率，同時維持 Part A 的 oversold 品質
    rsi_period: int = 14
    rsi_hook_lookback: int = 5  # 觀察過去 N 日內 RSI 最低點
    rsi_hook_delta: float = 2.0  # RSI 需自近期低點回升 ≥ H 點
    rsi_hook_max_min: float = 35.0  # 近期 RSI 低點須曾 ≤ 此水位（oversold）

    cooldown_days: int = 10


def create_default_config() -> XBI011Config:
    return XBI011Config(
        name="xbi_011_rsi_divergence_mr",
        experiment_id="XBI-011",
        display_name="XBI RSI Bullish Divergence + Pullback+WR MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 XBI-005）
        stop_loss=-0.050,  # -5.0%（同 XBI-005）
        holding_days=15,  # 15 天（同 XBI-005）
    )
