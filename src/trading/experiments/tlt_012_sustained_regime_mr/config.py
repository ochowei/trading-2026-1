"""
TLT Sustained Low-Volatility Regime Mean Reversion 配置 (TLT-012)

實驗動機：
- TLT-007 Att2 當前最佳（Part A Sharpe 0.12、Part B Sharpe 0.65），使用單日 BB(20,2)
  寬度/Close < 5% 作為波動率 regime 閘門。Part A 12 筆訊號中 50% WR，仍保留部分
  升息轉換期的邊緣訊號。
- TLT-011（rolling percentile BB 寬度，252d/504d lookback + 50th/40th pctile）結構
  性失敗（min(A,B) -0.11/0.01/0.03），原因為 2022 升息期占視窗 50%+ 使百分位自我
  稀釋。
- TLT-010（signal-day 2DD/ATR 補充濾波疊加於 TLT-007 Att2）三次迭代全失敗
  （min(A,B) -0.11/0.02/-0.18），確認在已套用 regime-level gate 後 signal-day
  secondary filter 結構性失效。

嘗試方向（repo 首次試驗於任何資產）：**Trajectory-Based Regime Gate — 多日 BB 寬度
一致性/收縮性作為 regime 確認**。
核心思想（與 TLT-007 / TLT-011 的結構性差異）：
- TLT-007 Att2 只要「當日 BB 寬度 < 5%」即通過，屬單日 snapshot 靜態閾值 → 在升息
  期偶發性單日壓縮仍可通過（2021-12-20 當日 BB 寬度短暫低於 5%，但 rolling 結構仍
  屬擴張中）。
- TLT-011 百分位屬 **相對靜態** 閾值（參考窗口內統計），單一極端 regime 主導時
  self-dilute。
- TLT-012 本實驗：多日 BB 寬度一致性（all/mean）或當日 vs 過去 N 日比較（contracting），
  屬 trajectory-based（軌跡）regime 確認 —— 不是單一日點測，也不是相對百分位。

與 TLT-010 lesson（signal-day secondary filter 失效）的區分：
- TLT-010 在 TLT-007 Att2 已完整 regime gate 通過後，於訊號日增加 2DD/ATR 次級濾波
  （獨立於 regime 的另一維度特徵）。
- TLT-012 本實驗：**精煉 regime gate 本身**（將單日 BB 寬度換成多日軌跡），規則
  仍屬 regime-level classifier 範疇，不屬於 signal-day secondary filter。
- 此區分呼應 cross_asset lesson #6 TLT-010 新規則：「未來方向應為更精細的 regime-level
  classifier，非 signal-day filter」。

設計理念（執行模型同 TLT-007）：
- 保留 TLT-007 驗證有效的進場條件（pullback 3-7% + WR ≤ -80 + ClosePos ≥ 40%）
- 保留 TLT-007 Att2 的絕對閾值（BB 寬度 < 5%）作為 baseline 單日要求
- 疊加 **trajectory 規則**（mode="all"/"mean"/"contracting"）
- 出場沿用 TLT-007 的 TP +2.5% / SL -3.5% / 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT012Config(ExperimentConfig):
    """TLT-012 Sustained Low-Volatility Regime Mean Reversion 參數

    迭代紀錄（三次迭代，全部失敗於 TLT-007 Att2 min 0.12）：

      Att1（mode="all"，trajectory_lookback=3；過去 4 日 BB 寬度皆 < 5%）：
        Part A 11 訊號 / WR 45.5% / Sharpe **0.03** / 累計 +0.43%
        Part B **3 訊號** / WR 100% / Sharpe 0.00 zero-var / 累計 +7.69%
        min(A,B) **0.00**（相對 TLT-007 Att2 的 0.12 退化 -100%）
        失敗分析：嚴格 4 日一致性過濾移除了 TLT-007 Part B 6 筆贏家中 3 筆
        （Part B 訊號崩潰至 3），這 3 筆為「spike-to-calm transition」結構
        ——TLT 在短暫 vol 升高後迅速回落至 calm regime，trajectory-strict
        規則要求連續 4 日皆 < 5% 因此濾除這些高品質轉換訊號。Part A 訊號
        從 12 降至 11（移除 1 筆贏家），Sharpe 崩壞。

      Att2（mode="mean"，trajectory_lookback=3；過去 4 日 BB 寬度均值 < 5%）：
        Part A **17 訊號** / WR 47.1% / Sharpe **-0.09** / 累計 -4.22%
        Part B 3 訊號 / WR 100% / Sharpe 0.00 zero-var（同 Att1）
        min(A,B) **-0.09**（相對 TLT-007 Att2 退化嚴重）
        失敗分析：均值條件 loosens 過濾——允許「當日 BB 寬度 > 5% 但近期均值 < 5%」
        的案例通過，等於在 TLT-007 Att2 基礎上新增 5 筆 Part A 訊號（17 vs 12），
        但這 5 筆均為低品質升息期邊緣訊號（BB 當下偏高但剛從更高位回落）。
        Part B 仍過濾同樣 3 筆 transition 贏家（跟 Att1 相同）。**Mean 模式雙向
        失敗**：對 Part A 過度放寬（引入壞訊號），對 Part B 無改善。

      Att3（mode="contracting"，trajectory_lookback=10；當日 BB < 5% AND 當日 BB
             <= 10 日前 BB）：
        Part A 9 訊號 / WR 44.4% / Sharpe **-0.02** / 累計 -0.82%
        Part B **5 訊號** / WR 80% / Sharpe **0.52** / 累計 +6.41%
        min(A,B) **-0.02**（相對 TLT-007 Att2 的 0.12 退化 -117%）
        失敗分析：「不擴張」條件改善 Part B（Att1/2 的 3 → 5 筆，保留更多
        transition 贏家），但 Part A 從 12 縮至 9（移除 3 筆）且 WR 由 50%
        降至 44.4%——contracting 濾波在 Part A 「穩定低 vol 但略有起伏」期間
        （2020-2021）將訊號日的 BB 寬度與 10 日前比較，穩定震盪的日子難以
        滿足「今天 <= 10 日前」，導致好訊號流失多於壞訊號。Part B 5 筆但
        1 筆 SL 導致 Sharpe 僅 0.52（不及 TLT-007 Att2 的 0.65）。

    **結論（強化 cross_asset lesson #6 + TLT-011 lesson）**：
      trajectory-based 精煉（strict consistency / mean consistency / contracting
      direction）三種變體在 TLT 上**全面失效**，強化 TLT-007 Att2 固定絕對閾值
      + 單日 snapshot 為結構性最優。**新增 TLT-specific 子規則**：BB-width regime
      gate 的精煉方向（percentile / trajectory）在 TLT 上皆系統性結構失敗，
      確認 TLT min 0.12 為現有技術面框架結構性上限，除非引入 regime-prediction
      機制（forward-looking Fed 政策指標、30d-implied vol 等），否則應停止在
      regime-classifier 精煉方向嘗試。

    **最終配置**：Att3（mode="contracting", lookback=10），其 min(A,B)=-0.02
    為三次迭代中最接近 TLT-007 Att2 的（Att1=0.00 為 Part B zero-var 假象）。
    """

    # 回檔範圍進場（同 TLT-007）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-007）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-007）
    close_position_threshold: float = 0.4

    # 波動率 regime 閘門基本參數（同 TLT-007 Att2）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05  # 5% 絕對閾值（同 TLT-007 Att2）

    # Trajectory-based regime 參數
    # trajectory_mode 定義 trajectory 規則：
    #   "all":         過去 trajectory_lookback+1 日 BB 寬度皆 < max_bb_width_ratio（嚴格一致性）
    #   "mean":        過去 trajectory_lookback+1 日 BB 寬度均值 < max_bb_width_ratio（均值一致性）
    #   "contracting": 當日 BB 寬度 < max_bb_width_ratio AND 當日 BB 寬度 <= trajectory_lookback 日前 BB 寬度
    #                 （vol 不擴張條件；允許穩定低 vol + 收斂中 vol，阻擋擴張中 vol）
    trajectory_mode: str = "contracting"
    trajectory_lookback: int = 10

    # 冷卻期（同 TLT-007）
    cooldown_days: int = 7


def create_default_config() -> TLT012Config:
    return TLT012Config(
        name="tlt_012_sustained_regime_mr",
        experiment_id="TLT-012",
        display_name="TLT Sustained Low-Volatility Regime MR",
        tickers=["TLT"],
        data_start="2018-01-01",  # 需要 SMA/BB 的 200 日暖機
        profit_target=0.025,  # +2.5%（同 TLT-007）
        stop_loss=-0.035,  # -3.5%（同 TLT-007）
        holding_days=20,
    )
