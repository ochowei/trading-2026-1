"""
TLT Duration-Spread Mean Reversion 配置 (TLT-008)

實驗動機（repo 首次試驗「配對交易」方向於利率驅動資產）：
- TLT-007 Att2 為當前最佳（Part A Sharpe 0.12，Part B Sharpe 0.65，min(A,B) 0.12），
  但 Part A 受 2022 升息餘波影響仍僅 0.12
- repo 已探索：pullback+WR+reversal MR、BB squeeze breakout、Donchian breakout、
  ROC momentum、Day-After Capitulation、Vol-Regime Gate MR。唯一完全未試方向為
  「配對交易（pairs trading）」
- cross_asset lesson #20 警告：橫跨不同資產類別的配對交易在 regime change 時結構性
  失效（XLU-005、COPX-006 等）。但 TLT 與 IEF 同屬美國公債，**結構性差異僅在存續期
  （Duration）**：TLT = 20+ yr、IEF = 7-10 yr。兩者間的相對表現差異由殖利率曲線
  形狀（steepness）驅動，是**機械性關係**而非跨類別相關性，預期較 lesson #20 的
  風險類別穩定

核心假設：**TLT 相對 IEF 的短期過度跌落代表殖利率曲線異常陡峭化，tends to revert**。
- 當 TLT 短期收益 - IEF 短期收益 << 0（TLT 明顯輸 IEF），表示長端利率跳升過度
- 此類事件（如 2022-10 Fed 超鷹事件、2023-08 財政部發債意外）常伴隨 1-2 週回補
- 過濾器：限定在非危機 regime（BB 寬度 < 5%，沿用 TLT-007 驗證），避免 2022 升息
  連續期間的長尾虧損

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. TLT lookback 日報酬 - IEF lookback 日報酬 <= relative_underperf_threshold（如 -2%）
2. TLT 今日 Close 位置（收盤位置）>= close_position_threshold（日內反轉確認）
3. TLT 今日 Close > 昨日 Close（至少首日轉正）
4. TLT BB(20, 2) 寬度 / Close < max_bb_width_ratio（波動率 regime 閘門，沿用 TLT-007）
5. 冷卻期 N 天

出場條件（同 TLT-007）：
- TP +2.5% / SL -3.5% / 20 天最長持倉
- 成交模型：隔日開盤市價進場、限價賣單 Day、停損市價 GTC、到期隔日開盤

迭代計畫：
- Att1 baseline：lookback=10，threshold=-2.0%，regime_gate=5%
- Att2：若 Att1 訊號過稀或 Part A 過低，放寬 threshold 至 -1.5% 或拉長 lookback 至 15
- Att3：若前兩次失敗，改用 TLT/IEF 比率 vs 其 100 日 z-score 作為 MR 訊號
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT008Config(ExperimentConfig):
    """TLT-008 Duration-Spread Mean Reversion 參數

    迭代紀錄（三次迭代）：
      Att1（lookback=10，threshold=-0.02，bb_gate=0.05）：
        10 日 TLT-IEF 報酬差 <= -2% + ClosePos >= 40% + daily up + BB 寬度 < 5%。
        （執行後填入結果）

      Att2（lookback=15，threshold=-0.025，bb_gate=0.05）：
        延長 lookback 捕捉更成熟的 spread divergence，收緊 threshold 至 -2.5%
        以維持訊號品質。

      Att3（改用 spread ratio z-score）：
        若前兩次失敗，改用 TLT/IEF 價格比率 vs 100 日移動平均的 z-score < -2 作為
        MR 訊號（更穩健的統計度量）。
    """

    # 參考標的（配對對手：中期公債 ETF）
    reference_ticker: str = "IEF"

    # Relative strength 進場參數
    relative_lookback: int = 10  # 10 日 TLT-IEF 報酬差
    relative_underperf_threshold: float = -0.02  # TLT 輸 IEF >= 2pp

    # 收盤位置過濾（日內反轉確認）
    close_position_threshold: float = 0.4

    # 當日轉正確認（Close_today > Close_yesterday）
    require_daily_up: bool = True

    # 波動率 regime 閘門（沿用 TLT-007 Att2 驗證的 5%）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # Att3 備用：spread ratio z-score MR（預設不啟用）
    use_spread_zscore: bool = False
    spread_zscore_window: int = 100
    spread_zscore_threshold: float = -2.0

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT008Config:
    return TLT008Config(
        name="tlt_008_duration_spread_mr",
        experiment_id="TLT-008",
        display_name="TLT Duration-Spread MR (vs IEF)",
        tickers=["TLT"],
        data_start="2018-01-01",  # 足夠暖機 BB/SMA(100)/spread lookback
        profit_target=0.025,  # +2.5%（同 TLT-007）
        stop_loss=-0.035,  # -3.5%（同 TLT-007）
        holding_days=20,
    )
