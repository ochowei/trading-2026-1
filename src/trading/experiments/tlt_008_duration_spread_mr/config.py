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
  形狀（steepness）驅動，是**機械性關係**而非跨類別相關性

核心假設：**TLT 相對 IEF 的短期過度跌落 + 成熟回檔結構 = MR 機會**。
- Att1 純 pair 訊號已證明失敗：duration spread <= -2% 單獨進場捕捉的是「TLT 啟動下跌」
  而非反轉機會（2020-05 至 2021-02 四筆全 SL/expiry）
- Att2 修正：將 spread 訊號降為**附加品質過濾**，疊加於 TLT-007 Att2 的成熟 MR 框架
  （pullback 3-7% + WR ≤ -80 + ClosePos ≥ 40% + BB 寬度 < 5%）之上
- 即：先確認 TLT 本身有深度回檔 + 超賣 + 日內反轉 + 非危機 regime，再加上
  「相對 IEF 的額外弱勢」作為識別「殖利率曲線陡峭化事件」的結構性訊號

進場條件（Att2 全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 >= 3%（同 TLT-007）
2. 10 日高點回檔 <= 7%
3. Williams %R(10) <= -80（超賣）
4. TLT 收盤位置 >= 40%（日內反轉）
5. BB(20, 2) 寬度 / Close < 5%（regime gate）
6. [新增] TLT 相對 IEF 過去 N 日報酬差 <= threshold（殖利率曲線陡峭化事件）
7. 冷卻期 N 天

出場條件（同 TLT-007）：
- TP +2.5% / SL -3.5% / 20 天最長持倉
- 成交模型：隔日開盤市價進場、限價賣單 Day、停損市價 GTC、到期隔日開盤
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT008Config(ExperimentConfig):
    """TLT-008 Duration-Spread Mean Reversion 參數

    迭代紀錄（三次迭代）：
      Att1（純 pair 訊號：lookback=10，threshold=-0.02，BB<5%，無 pullback/WR）：
        Part A 4/0%/Sharpe -5.92、累計 -12.49%；Part B 1/100%/Sharpe 0.00 (零方差)。
        min(A,B) -5.92 遠低於 TLT-007 Att2 的 0.12。
        失敗根因：spread <= -2% 單獨進場捕捉「TLT 長期熊市開端」而非 MR 機會。
        2020-05 至 2021-02 四筆訊號均為 TLT 緩跌 regime 啟動初期，BB<5% 對此類
        「低波動緩跌」無過濾效果。

      Att2（Att2 combined：TLT-007 Att2 完整框架 + 附加 pair 過濾 threshold=-0.015）：
        TLT 回檔 3-7% + WR(10)≤-80 + ClosePos≥40% + BB<5% + TLT-IEF 10d spread ≤ -1.5%。
        預期：過濾掉 TLT-007 Att2 中「一般 MR 訊號」，保留「殖利率曲線陡峭化事件」
        這類結構性機會（2022-10 Fed hawkish surprise、2023-08 bond auction shock 等）。

      Att3（z-score 統計標準化 pair 過濾）：
        反向方向中間測試（5d spread >= +0.3% + MR 主訊號）**所有 part 皆 0 訊號**——
        TLT 在 10d pullback 3-7% 期間相對 IEF 必然弱勢（duration 機械關係），短期
        反向 spread 與 MR 進場結構互斥。最終 Att3 配置：TLT/IEF 價格比率對其 100 日
        均值的 z-score <= -1.5σ（統計顯著的歷史性偏離）+ TLT-007 Att2 完整 MR 框架。
        結果：Part A 6/33.3% WR/Sharpe **-0.31** (2 TP/1 SL/3 expiry)、cum -4.64%；
        Part B 2/100%/零方差 Sharpe 0.00、cum +5.06%；min(A,B) **-0.31**。
        仍低於 TLT-007 Att2 的 0.12。z-score 過濾雖救回 2022-02-08 贏家，但仍無法
        補救 2020-12、2021-01 連續性虧損期訊號。

    實驗結論（三次迭代皆失敗）：TLT vs IEF duration spread pairs trading 於 TLT 上
    **結構性失敗**，擴展 cross_asset lesson #20 邊界：
    - 原規則：「跨資產類別相關性配對」在 regime change 時失效
    - TLT-008 發現：**同資產類別（同為美國公債）但不同 duration 的機械性 pair** 仍失敗
    - 根因：TLT 與 IEF 在 TLT pullback 期間的相對表現由「duration 敏感度比例」機械
      決定（TLT ≈ 18yr duration vs IEF ≈ 7.5yr duration，TLT 對利率敏感度 ~2.4x），
      而非「獨立個體間偏離後回歸」的經典 pairs MR 結構
    - 任何「TLT 輸 IEF」過濾都系統性保留「rate shock 起點」訊號（贏家被濾掉）；
      任何「TLT 贏 IEF」過濾在 MR 進場結構下無解（矛盾條件）；z-score 統計標準化
      無法克服此結構性限制

    最終配置：保留 Att3（z-score），作為最後一次驗證參考；實驗標記為**未超越 TLT-007 Att2**。
    """

    # 參考標的（配對對手：中期公債 ETF）
    reference_ticker: str = "IEF"

    # === 主訊號（Att2 啟用：TLT-007 Att2 完整框架）===
    # 回檔範圍
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置
    close_position_threshold: float = 0.4

    # 波動率 regime 閘門（沿用 TLT-007 Att2）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # === 配對過濾（TLT-008 核心創新）===
    # 啟用主訊號所有條件（Att1 為 False = 純 pair；Att2+ 為 True = hybrid）
    require_mr_framework: bool = True

    # Relative strength 過濾參數
    # Att1/Att2 (弱勢方向) + 反向測試 (強勢方向) 皆失敗
    # Att3：改用 TLT/IEF 價格比率 z-score（100d 視窗統計標準化），捕捉「歷史性
    # 極端偏離」而非短期絕對差距，作為最後一次嘗試的 pair 變體
    relative_lookback: int = 10
    relative_underperf_threshold: float = -0.015
    relative_direction_bullish: bool = False  # 恢復弱勢方向（與 z-score 一致）

    # 當日轉正確認（僅 Att1 純 pair 使用；Att2+ 已由 ClosePos + 主 MR 框架覆蓋）
    require_daily_up: bool = False

    # Att3 啟用：spread ratio z-score MR（100 日視窗，-1.5σ 門檻）
    use_spread_zscore: bool = True
    spread_zscore_window: int = 100
    spread_zscore_threshold: float = -1.5

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT008Config:
    return TLT008Config(
        name="tlt_008_duration_spread_mr",
        experiment_id="TLT-008",
        display_name="TLT Duration-Spread MR (vs IEF)",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,  # +2.5%（同 TLT-007）
        stop_loss=-0.035,  # -3.5%（同 TLT-007）
        holding_days=20,
    )
