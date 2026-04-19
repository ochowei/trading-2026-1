"""
CIBR Key Reversal Day 均值回歸配置 (CIBR-009)

動機：CIBR-008 Att2 已確認為 CIBR 全域最優（Part A Sharpe 0.39 / Part B Sharpe 4.38，
其中 Part B 為 100% WR 5 訊號零方差，min(A,B) 實質由 Part A 0.39 綁定）。CIBR-008
的 Part A 有 7 訊號含 2 停損（2020-02-24 COVID、2021-02-26 科技拋售），兩者均為
「BB 下軌觸及但隔日繼續深跌」。如能改用「washout + 日內反轉確認」的 price-action
結構，或許能過濾此類 false bottom 訊號。

策略：Key Reversal Day（關鍵反轉日）— 經典 price-action 反轉結構
- Day T-1：下跌收黑（bearish bar）
- Day T：Low < Prev Low（stop-run / washout，觸發停損連鎖）
- Day T：Close > Prev Close（反轉確認，站回前日收盤）
- Day T：Close > Open（當日收紅 bullish bar）
- Day T：ClosePos >= 40%（日內反攻）

為了避免與 XBI-012（ROC acceleration）及 URA-009（Close > Prev High reclaim）重疊：
- XBI-012 使用 ROC(3) 短期加速下跌 + 日內反攻 → XBI 失敗
- URA-009 使用「Close > Prev High」即站上前日最高 → URA 失敗
- CIBR-009 使用「Low < Prev Low + Close > Prev Close」即 stop-run 後反轉
  → 更嚴格的 washout 結構（不只是反彈，而是先破底再收復）

Pullback 上下限：
- 下限 ≥ -3% 過濾無效橫盤（確保 MR 語境）
- 上限 ≤ -12%（~7.8σ for 1.53% vol，同 CIBR-008 崩盤隔離邊界）

Att1: 標準參數（WR ≤ -80, pullback -3~-12%, 全部 price-action 過濾）
      → Part A -0.08 (8/50% WR) / Part B -0.44 (3/33.3% WR), min -0.44（失敗）
      失敗分析：stop-run+reclaim 本身不具選擇性，熊市續跌中破底反彈只是技術性反彈。
      2022 年 3 連 SL、2025 年 2 連 SL 均為「washout 後續跌」。
Att2: 加入 ATR(5)/ATR(20) > 1.15（波動率飆升確認真 capitulation）
Att3: 視 Att2 結果決定（調 WR/pullback/ATR 門檻或 TP/SL）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR009Config(ExperimentConfig):
    """CIBR-009 Key Reversal Day 參數"""

    # Pullback 範圍（MR context）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 下限：回檔至少 -3%
    pullback_cap: float = -0.12  # 上限：回檔不深於 -12%（崩盤隔離）

    # 超賣確認
    wr_period: int = 10
    wr_threshold: float = -80.0

    # Key Reversal 結構（布林條件，硬編碼於 signal_detector）
    close_pos_threshold: float = 0.40  # 日內反轉
    # 其他結構條件：
    # - Prev Close < Prev Open（前日收黑）
    # - Today Low < Prev Low（washout / stop-run）
    # - Today Close > Prev Close（站回前日收盤）
    # - Today Close > Today Open（當日收紅）

    # Att2 新增：ATR 波動率飆升確認
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    cooldown_days: int = 8


def create_default_config() -> CIBR009Config:
    return CIBR009Config(
        name="cibr_009_key_reversal_day_mr",
        experiment_id="CIBR-009",
        display_name="CIBR Key Reversal Day after Pullback",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%（CIBR 甜蜜點，沿用 CIBR-002/CIBR-008）
        stop_loss=-0.04,  # -4.0%（CIBR 停損甜蜜點）
        holding_days=18,
    )
