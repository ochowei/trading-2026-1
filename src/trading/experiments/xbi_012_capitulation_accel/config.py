"""
XBI-012: 短期急跌 + 中點反攻均值回歸配置
(XBI Capitulation + Acceleration Reversal MR Configuration)

設計動機 (Design rationale):
XBI-005 (pullback 8-20% + WR(10) ≤ -80 + ClosePos ≥ 35%) min(A,B) 0.36 為當前最佳，
XBI-010 (BB 下軌 + 回檔上限混合) 與 XBI-011 (RSI hook divergence) 均失敗，
揭示 XBI 2.0% 日波動 + 事件驅動 (FDA/臨床) 使統計自適應與 RSI 轉折過濾失效。

本實驗嘗試以 **3 日急跌 ROC + 當日強反攻收盤** 作為 XBI-005 的結構替代：
- 3 日 ROC ≤ -4% 捕捉 1-2 日急跌型 FDA/臨床事件（而非 10 日回檔的慢磨下跌）
- Close > 前日 Close 且 ClosePos ≥ 50% 確認當日反攻（比 XBI-005 的 35% 嚴格）
- 搭配 WR(10) + 10 日回檔作為 macro pullback 環境濾波

核心差異 vs XBI-005：
- ROC(3) 針對單次事件拋售（1-2 日集中下跌），XBI-005 的 Pullback(10) 反映慢磨下跌
- 「Up day + ClosePos ≥ 50%」比 XBI-005 的「ClosePos ≥ 35%」嚴格，要求當日明確轉強
- 10 日 pullback 門檻降至 -6%（XBI-005 為 -8%）補償 ROC(3) 的 time window 變窄

核心差異 vs XBI-010 / XBI-011：
- 不使用統計自適應門檻（BB 下軌）— XBI 2.0% vol 已驗證混合模式失效
- 不使用 RSI(14) hook — XBI 事件驅動 RSI 多停在 35-45 區間未達深度 oversold
- 改用「單週短期急跌 + 當日強反攻」的 price-action 驅動進場

預期效果：捕捉生技板塊典型「FDA 利空拋售 → 低吸買盤反攻」結構，
該結構常集中在 2-4 日內完成拋售+反攻，與 RSI 飽和式慢跌反轉不同。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI012Config(ExperimentConfig):
    """XBI-012 Capitulation + Acceleration Reversal 參數"""

    # Pullback context（輕度環境濾波，不同於 XBI-005 的 -8%）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.06  # 近 10 日回檔 ≥ 6%
    pullback_upper: float = -0.20  # 回檔上限 20%（過濾極端崩盤）

    # 短期急跌：3 日 ROC（Close / Close[-3] - 1） ≤ threshold
    # Att1 (-4%): 3/3 訊號過稀疏 Sharpe 0.16
    # Att2 (-3%): 放寬以增加訊號頻率
    roc_lookback: int = 3
    roc_threshold: float = -0.03  # 3 日急跌 ≥ 3%（約 1.5σ for 2.0% vol）

    # 日內反攻：當日收盤強度 + 較前日上漲
    # Att1 (0.50): 過嚴；Att2 (0.40): 放寬以同步提升訊號頻率
    close_position_threshold: float = 0.40
    require_up_day: bool = True  # Close > 前日 Close

    # Williams %R 超賣濾波（標準）
    wr_period: int = 10
    wr_threshold: float = -80.0

    cooldown_days: int = 10


def create_default_config() -> XBI012Config:
    return XBI012Config(
        name="xbi_012_capitulation_accel",
        experiment_id="XBI-012",
        display_name="XBI Capitulation + Acceleration Reversal MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（XBI 硬上限，同 XBI-005）
        stop_loss=-0.050,  # -5.0%（XBI 硬下限，同 XBI-005）
        holding_days=15,  # 15 天
    )
