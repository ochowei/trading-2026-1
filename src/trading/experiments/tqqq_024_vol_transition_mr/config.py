"""TQQQ Post-Capitulation Vol-Transition MR 配置 (TQQQ-024)

實驗動機（repo 首次「完全替代 framework」於 TQQQ）：
- TQQQ-018 Att3 為當前最佳（min(A,B) 0.80），其框架為「-15% drawdown extreme
  capitulation buy」，Part B 0.80 為 binding constraint
- TQQQ-019/020/021/022/023 共五次「在 TQQQ-018 上加 cross-asset macro filter」全部失敗：
  - implied vol（^VIX/^MOVE）三次與 capitulation 結構性共線
  - cross-asset divergence（QQQ-SPY）一次因 broad panic 同步而 reverse-selecting
  - yield curve slope velocity 一次因 leveraged tech ETF 為 rate-indirect 失敗
- TQQQ-023 AI_CONTEXT 明確指出剩餘未驗證假設：「完全替代 framework
  （vol-transition MR / BB Squeeze Breakout，跳脫 -15% extreme capitulation 結構）」

嘗試方向（repo 中 Vol-Transition MR 已於 EWJ-005、EWT-008、IWM-013、INDA-010、
EEM-014、VGK-008、SOXL-006、IBIT-009 等 8+ 資產驗證成功，但**尚未於 TQQQ 試驗**）：
**Post-Capitulation Vol-Transition Mean Reversion**。

核心假設：
- TQQQ -15% drawdown 過於極端，僅捕捉 2020 COVID + 2022 升息兩段 regime，
  Part B 訊號流稀疏（5-6 個訊號 vs Part A 16 個）
- 改用「BB 下軌觸及 + 中度回檔（8-25% from 10d high）+ WR(10) 深度超賣
  + 收盤強反轉 + ATR vol-transition + 2DD floor」的混合進場框架
- 預期可放寬進場至 ~15-20 訊號/Part 並改善 Part B 樣本數

與 lesson #5 的區分：
- 此為 BB lower band MR + 中度 pullback，不含趨勢方向過濾器
- ATR vol-transition 為「signal-day capitulation panic 確認」，非趨勢過濾

成交模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定，
slippage 0.1%（同 TQQQ-010/018 慣例）。

========================================================================
三次迭代記錄（2026-05-09，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1（基線）：2DD floor <= -3.0% + ATR(5)/ATR(20) > 1.10
  深度 capitulation 要求（2 日累計 >= 3% 跌幅）+ 標準 vol-transition 門檻

Att2：2DD floor <= -2.0% + ATR(5)/ATR(20) > 1.10（更寬鬆 capitulation）
  測試是否更寬的 2DD 門檻能引入更多 winners 而不犧牲品質

Att3：2DD floor <= -3.0% + ATR(5)/ATR(20) > 1.20（更嚴 vol-transition）
  測試是否更嚴的 ATR vol expansion 要求能精煉訊號品質
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQ024Config(ExperimentConfig):
    """TQQQ-024 Post-Capitulation Vol-Transition MR 參數"""

    # BB 下軌觸及（mean reversion 主訊號）
    bb_period: int = 20
    bb_std: float = 2.0

    # 10 日高點回檔範圍 [floor, cap]：要求中度 pullback（過淺無 MR 動能、過深為崩盤）
    pullback_lookback: int = 10
    pullback_floor: float = -0.08  # 至少 8% 回檔
    pullback_cap: float = -0.25  # 最多 25% 回檔（排除 -15% 以上的 extreme crash）

    # Williams %R 深度超賣
    wr_period: int = 10
    wr_threshold: float = -85.0

    # 收盤強反轉確認
    close_position_threshold: float = 0.35

    # ATR vol-transition gate（signal-day panic 確認）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10  # Att1/Att2 預設；Att3 改為 1.20

    # 2 日急跌 floor（require true 2-day capitulation depth）
    twoday_return_floor: float = -0.03  # Att1/Att3 預設；Att2 改為 -0.02

    # 冷卻期
    cooldown_days: int = 5

    # 成交模型
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ024Config:
    return TQQQ024Config(
        name="tqqq_024_vol_transition_mr",
        experiment_id="TQQQ-024",
        display_name="TQQQ Post-Capitulation Vol-Transition MR",
        tickers=["TQQQ"],
        data_start="2018-06-01",  # 暖機 BB(20) / ATR(20)
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.05,
        stop_loss=-0.05,
        holding_days=10,
    )
