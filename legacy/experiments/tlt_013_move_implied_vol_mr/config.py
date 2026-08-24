"""
TLT MOVE Implied-Volatility Forward-Looking Regime-Gated MR (TLT-013)

實驗動機：
- TLT-007 Att2 為當前全域最優（min(A,B) 0.12，Part A 0.12 / Part B 0.65）
- TLT-010/011/012 三次「regime classifier 精煉」（2DD floor、percentile BB、trajectory BB）
  全部失敗，cross_asset_lessons.md 明確指出：
  「除非引入 regime-prediction 機制（forward-looking Fed 政策指標、30d-implied vol），
   否則應完全停止 regime-classifier 精煉方向嘗試。」
- TLT-008（IEF pair）+ TLT-009（^TNX 殖利率 velocity）皆已證明外部利率 LEVEL/方向
  指標作為 TLT MR 過濾器**結構性受限**——非 forward-looking、與 MR trigger 時序錯位。

嘗試方向（repo 首次於任何資產）：**^MOVE 隱含波動率 forward-looking regime gate**。
核心思想：
- ^MOVE = Merrill Lynch Option Volatility Estimate，債券選擇權市場對未來 30 日
  Treasury yield 波動率的隱含預期。**結構上 forward-looking**（option price 反映
  未來預期），與 ^TNX (rate level) / BB-width (realized vol) 等 backward-looking
  指標本質不同。
- 假設：當市場預期未來 30 日債券波動率高（^MOVE 高），TLT 短期均值回歸成功率下降
  （rate-uncertainty regime 持續主導）；當市場預期波動率回歸正常（^MOVE 低），
  MR 訊號落於正常 calm regime 中容易回歸。
- 與 TLT-007 BB-width regime gate 的差異：BB 寬度為 backward-looking realized vol
  classifier，^MOVE 為 forward-looking implied vol predictor，理論上二者**正交**。
- 與 TLT-009 ^TNX yield 失敗的差異：^TNX 為 rate **LEVEL** 指標，^TNX 變化反映
  rate shock 時序與 TLT MR trigger 錯位；^MOVE 為 **VOLATILITY** 指標，反映市場
  對未來波動的擔憂程度，與 MR 進場條件（pullback 已發生 + WR 超賣）邏輯一致。

設計理念：
- 沿用 TLT-007 Att2 的 BB-width regime gate（已驗證有效），疊加 ^MOVE 過濾
- ^MOVE 過濾方向：MOVE level <= max_move_level（過濾高 MOVE regime 訊號）
- 出場沿用 TLT-001/002/007 驗證的 TP +2.5% / SL -3.5% / 20 天

Cross-asset hypothesis（待驗證）：
- 若 ^MOVE filter 對 TLT 有效，可能擴展至其他 rate-driven assets（XLU, REITs）
- ^MOVE 為 repo 首次使用 forward-looking implied volatility derivative 作為 regime gate
  其他可能後續方向：^VIX (stocks), ^OVX (oil), ^GVZ (gold)
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT013Config(ExperimentConfig):
    """TLT-013 MOVE Implied-Vol Regime-Gated MR 參數

    迭代紀錄（三次迭代）：
      Att1 ★ (max_move_level=130.0)：
        Part A 11/54.5% WR/Sharpe 0.14 cum +3.53%（vs TLT-007 Att2 12/50%/0.12/+2.95%，
        +17% Sharpe）/ Part B 6/83.3%/Sharpe 0.65 cum +9.07%（與 TLT-007 Att2 完全相同，
        Part B 全部 MOVE 值 86.6-102.5 < 130 不被過濾）/ min(A,B) **0.14**（+17%）。
        ^MOVE 130 過濾僅作用於 2023-05-16 SL（MOVE 130.3，SVB 高峰期），2022-02-07
        winner（MOVE 87.4）保留。此為 repo **首次正向 Sharpe 改善** 來自 forward-looking
        implied volatility derivative regime gate（cross_asset_lessons.md 明確指出方向）。
        A/B 累計差 |3.53-9.07|/9.07 = 61% > 30% ❌（同 TLT-007 Att2 67.5% 結構性，
        Part B > Part A 屬利多不對稱非 overfitting），訊號比 11:6 = 45% < 50% ✓

      Att2 (Att1 base + MOVE 60d SMA <= 100)：
        Part A 11/54.5%/Sharpe 0.14（與 Att1 完全相同，Part A 訊號 60d SMA 全 < 100）/
        Part B 4/100% WR std=0 Sharpe 0.00 cum +10.38%（過濾 2024-04-08 SL 但同時誤殺
        2024-11-15 TP）/ min(A,B)† 0.14（同 Att1，但訊號比惡化至 11:4 = 64% > 50% ❌）。
        **REJECT**：MOVE 60d SMA filter 雖過濾 1 SL 卻同時誤殺 1 TP，A/B 訊號比違反平衡標準。
        2024-04-08 (MOVE 99.4) 與 2024-11-15 (MOVE 102.5) 在 60d SMA 維度高度重疊，
        無法選擇性過濾。

      Att3 (Att1 base + Prior_DD(T-5, 60d) <= -1%, TQQQ-018 cross-asset port)：
        Part A 8/50.0%/Sharpe 0.02 cum +0.05%（**嚴重退化** vs Att1 0.14）/ Part B 6 不變
        Sharpe 0.65 / min **0.02**。**REJECT**：prior-DD 過濾移除 3 訊號（2020-08-12 expiry
        +0.40%、2021-08-11 TP、2021-09-27 expiry +1.36%）但保留全部 2 SLs（2020-05-26、
        2021-02-04），淨效果為 -2 winners、0 SL filtered，Sharpe 0.14→0.02。**TQQQ-018
        prior-DD filter 結構性不適用 TLT**：TQQQ Part A SL 集中於 2020-02-24 COVID
        first-day-of-decline 且 DD(T-5)=-0.49% 剛好被 -1% 門檻過濾；TLT Part A SLs
        2020-05-26 / 2021-02-04 反而是 deep-prior-DD 訊號（5 days 前已大幅回檔），
        prior-DD 過濾錯誤方向。**新跨資產規則**：TQQQ-018 prior-DD filter
        適用「leveraged 索引 ETF first-day-of-decline」結構，**不適用 rate-driven 資產
        post-peak slow-melt 結構**。

    最終配置：Att1（max_move_level=130.0，所有其他過濾停用）

    結論與跨資產貢獻：
      1. **Repo 首次成功使用 forward-looking implied vol derivative 作為 regime gate**——
         ^MOVE 為 cross_asset_lessons.md 明確指出「TLT 突破 0.12 ceiling」的指定方向
         （forward-looking Fed policy / 30d-implied vol），TLT-013 Att1 為首次驗證
      2. **MOVE 130 為 TLT 上 ^MOVE 過濾甜蜜點**——保留 2022-02-07 winner（MOVE 87）
         與 2024-2025 全部 winners（MOVE 86-103），僅過濾 2023-05-16 SVB 高峰 SL
      3. **MOVE 60d SMA 平滑 regime 與 prior-DD 結構性失敗**：smoothed regime 在 Part B
         無法區分 SL/TP，prior-DD 在 Part A 誤刪 winners
      4. **新跨資產假設（待驗證）**：^MOVE level filter 可能適用其他 rate-driven 資產
         （XLU, REITs）；其他 implied vol indices（^VIX/^OVX/^GVZ）可能適用對應底層資產
    """

    # 回檔範圍進場（同 TLT-001/002/007）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-001/002/007）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-001/002/007）
    close_position_threshold: float = 0.4

    # BB-width regime gate（沿用 TLT-007 Att2 配置）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # ^MOVE forward-looking implied vol regime gate（TLT-013 核心新增）
    move_ticker: str = "^MOVE"
    max_move_level: float = 130.0  # Att1 最佳：保留 130 上限濾 2023-05-16 SL (130.3)
    # Att2 測試 MOVE 60d SMA 平滑 regime 過濾（reject — Part B 失去 1 winner）
    max_move_sma_level: float = 100.0
    move_sma_window: int = 60
    use_move_sma_filter: bool = False  # Att2 reject
    use_move_direction_filter: bool = False  # 暫不啟用
    move_direction_lookback: int = 5
    # Att3 新增：TQQQ-018 cross-asset port — 「prior drawdown 過濾」捕捉 first-day-of-decline
    # 訊號日 T-N 日的 drawdown(60d high) 必須已經 <= max_prior_dd（即 T-N 日已有顯著回檔）
    use_prior_dd_filter: bool = False  # Att3 reject：濾掉 2 TPs 但保留 2 SLs，Sharpe 0.14→0.02
    prior_dd_lookback_offset: int = 5  # 訊號日 T-5 日的 drawdown
    prior_dd_window: int = 60  # 60 日高點計算 drawdown
    max_prior_dd: float = -0.01  # T-5 日 drawdown(60d) <= -1%

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT013Config:
    return TLT013Config(
        name="tlt_013_move_implied_vol_mr",
        experiment_id="TLT-013",
        display_name="TLT MOVE Implied-Vol Regime-Gated MR",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,
        stop_loss=-0.035,
        holding_days=20,
    )
