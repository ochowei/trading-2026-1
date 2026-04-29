"""
TLT Dynamic BB-Width Percentile Regime MR 配置 (TLT-011)

實驗動機：
- TLT-007 Att2（BB 寬度/Close < 5% 固定閾值）為當前最佳（Part A Sharpe 0.12 / Part B 0.65 /
  min(A,B) **0.12**），但 A/B 累計報酬差 67.5%（>30% 目標），且固定閾值缺乏 cross-regime
  適應性——2022 升息期被「5%」這個 ad-hoc 數字一刀切除，未來若波動率結構改變則無法自適應。
- TLT-009、TLT-010 延續嘗試「外部 yield gate / signal-day secondary filter」均失敗，
  EXPERIMENTS_TLT.md 明示未來方向為「**BB 寬度 60 日分位數 dynamic regime 而非固定閾值**」。
- FXI-013 驗證固定 BB 寬度在多段中等 vol regime 失敗（min 0.09 vs FXI-005 的 0.38），
  但 TLT 2022 為**單一極端 vol regime episode**，符合 BB-width regime gate 成功前提。
  本實驗以 percentile-based dynamic threshold 替代固定 5%，預期能維持 TLT-007 Att2 的
  regime classification 能力，並可能進一步提升 Part A 訊號品質。

嘗試方向（repo 中未曾於任何資產試驗 percentile-based BB-width regime gate）：
**Dynamic BB-Width Percentile Regime Gate**。核心思想：
- BB(20,2) 寬度 / Close 計算後，再取其 252 日（或 504 日）rolling percentile rank
- 僅當 current BB-width percentile rank <= max_bb_width_pctile_rank 時放行訊號
- 2022 升息期 BB-width 全年處於歷史分位數 80-100th，percentile gate 天然過濾
- 2019-2021 降息期 + 2024-2025 高利率高原期 BB-width 常處於分位數 10-60th，訊號保留

與 lesson #5 的區分（同 TLT-007）：
- Percentile 仍是 regime classifier（crisis vs calm 波動率狀態），非單日方向濾波
- 不違反 MR + trend filter = disaster 原則

執行模型（同 TLT-007）：
- 訊號日收盤偵測 → 隔日開盤市價進場（含 0.1% 滑價）
- TP/SL：限價單 / 停損市價 GTC
- 悲觀認定：同根 K 線 TP + SL 同觸 → 假設 SL 先成交
- 到期：持倉滿 holding_days 後隔日開盤市價出場
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT011Config(ExperimentConfig):
    """TLT-011 Dynamic BB-Width Percentile Regime MR 參數

    迭代紀錄（三次迭代，全部失敗 vs TLT-007 Att2 的 min 0.12）：

      Att1（bb_width_pctile_lookback=252、max_bb_width_pctile_rank=0.50、
           enable_absolute_backup=False）：
        策略方向：252 日 rolling percentile rank <= 50%（中位數）作為 regime 閘門
        關鍵參數：lookback=252d、pctile<=50%、純動態無絕對閾值
        結果：Part A 24 訊號/50.0% WR/Sharpe **-0.11**/cum -7.76%
              Part B 11 訊號/81.8% WR/Sharpe 0.55/cum +14.72%
              min(A,B) **-0.11**（劣於 TLT-007 Att2 的 0.12 約 0.23 絕對值）
        失敗分析：50th percentile 閾值過寬，2022 升息期 trailing 252 日窗口累積大量
          高 vol 天數，導致中位數本身被拉高，「當日 <= 中位數」仍放行整片 2022 升息期
          訊號流。Part A 訊號反增至 24（vs TLT-007 Att2 12），A/B signal ratio 12/11
          = 1.1:1 雖佳但 Part A 品質崩潰。**rolling percentile 在單一極端 regime episode
          持續存在時會「自我稀釋」**——參考窗口被 regime 期間主導，percentile 失去
          cross-regime 區分力。

      Att2（bb_width_pctile_lookback=504、max_bb_width_pctile_rank=0.40）：
        策略方向：擴大 lookback 至 504 日（2 年）以跨越 2022 regime，收緊 pctile 至 40th
        關鍵參數：lookback=504d、pctile<=40%、純動態無絕對閾值、data_start=2016-01-01
        結果：Part A 13 訊號/53.8% WR/Sharpe **0.01**/cum +0.06%
              Part B 11 訊號/81.8% WR/Sharpe 0.55/cum +14.72%
              min(A,B) **0.01**（仍劣於 TLT-007 Att2 的 0.12）
        失敗分析：504 日窗口雖含 2021 calm period 但 2022 升息期仍佔據超過 50% 的窗口
          樣本，40th pctile 亦不足以完全切除 2022 訊號。Part A 訊號從 Att1 的 24 降至 13
          （接近 TLT-007 Att2 的 12），Sharpe 小幅回升至 0.01 但仍未轉正。Part B 維持 11
          訊號（比 TLT-007 Att2 的 6 訊號多 5 筆），WR 81.8% 顯示 Part B 有訊號放寬的潛力。
          **504 日視窗仍不夠長**——理論上需要 1000+ 日（4 年）才能稀釋 2022 影響，但如此
          長的視窗會過度平滑近期波動率變化，實用性受限。

      Att3（lookback=252、pctile<=40%、enable_absolute_backup=True，絕對 < 5%）：
        策略方向：Hybrid dual gate — 252 日 pctile <= 40th AND 絕對 BB 寬度 < 5%
          （希望絕對閾值提供 2022 regime 切除，pctile 作為補充過濾）
        關鍵參數：lookback=252d、pctile<=40%、absolute<=5%（雙重 AND）
        結果：Part A 10 訊號/50.0% WR/Sharpe **0.03**/cum +0.53%
              Part B 6 訊號/83.3% WR/Sharpe 0.65/cum +9.07%（Part B 與 TLT-007 Att2 完全相同）
              min(A,B) **0.03**（仍劣於 TLT-007 Att2 的 0.12）
        失敗分析：Part B 結果與 TLT-007 Att2 完全相同（6/83.3%/0.65/+9.07%）——表示 Part B
          的 6 筆訊號其 BB 寬度絕對值皆 < 5% 且 pctile rank 皆 <= 40th（calm regime 自洽）。
          但 Part A 訊號從 TLT-007 Att2 的 12 降至 10，Sharpe 從 0.12 降至 0.03——pctile
          多過濾了 2 筆 TLT-007 Att2 贏家（2022-02-07 或 2020-05/2021-02 區間內某些訊號，
          這些訊號 BB 寬度 < 5% 但相對於過去 252 日為高分位數）。**pctile gate 在 TLT 上
          系統性移除 calm period 末期 / regime 轉換初期的好訊號**。

    結論：**TLT 的 BB 寬度 regime 閘門以「固定絕對閾值 5%」為結構性最優**，percentile-based
    dynamic threshold 無論（1）純動態（Att1/Att2）或（2）與絕對閾值 AND 組合（Att3）皆
    系統性劣於 TLT-007 Att2。核心原因：
    1. TLT 2022 升息期為單一持續 12+ 個月的 regime episode，rolling percentile 在此期間
       自我稀釋（Att1、Att2），無法提供 cross-regime 區分力；
    2. 即使絕對閾值已切除大部分 2022 訊號，追加 pctile 過濾（Att3）會系統性移除 calm
       regime 末期 / regime 轉換初期的好訊號（pctile 以「相對近期歷史」為基準，2022 後
       calm period 初期 BB 寬度雖絕對值低但相對於 2022 為極低，隨時間推移 pctile 上升，
       反而過濾掉 2022 結束後的 good signals）。
    3. TLT-007 Att2 的「固定 5%」本質上是對 TLT 物理波動率的**結構性常數**（約 5σ 日波動
       等價於 BB 通道 2 × 2σ = 約 5% 價格範圍），不應被動態化。

    **跨資產規則擴展（lesson #20b）**：對於**單一極端 vol regime episode 持續時間長於
    percentile lookback 視窗 50%** 的資產，rolling percentile-based regime gate 結構性
    失效——固定絕對閾值為唯一有效解。此規則與 FXI-013 的「多段中等 vol regime 下固定和
    動態皆失敗」互補，共同精煉 BB-width regime gate 的適用邊界：
    - 資產有**單一極端且短於 lookback 50% 的 vol regime**：動態 percentile 可行
    - 資產有**單一極端且長於 lookback 50% 的 vol regime**（TLT 2022）：僅固定絕對閾值有效
    - 資產有**多段中等 vol regime**（FXI）：BB-width 所有型式皆失敗，應改用其他 regime
      classifier（如政策驅動資產的事件驅動濾波）

    最終配置：Att3（留作失敗紀錄配置，min(A,B) 0.03 雖劣於 TLT-007 Att2 的 0.12 但為
    三次迭代中最接近者）。TLT-007 Att2 仍為 TLT 全域最優（11 次實驗、32+ 次嘗試）。
    """

    # 回檔範圍進場（同 TLT-007 Att2）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-007 Att2）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-007 Att2）
    close_position_threshold: float = 0.4

    # 動態 BB 寬度分位數 regime 閘門（新增，取代固定 5% 閾值）
    bb_period: int = 20
    bb_std: float = 2.0
    bb_width_pctile_lookback: int = 252  # Att3：252 交易日 ≈ 1 年
    max_bb_width_pctile_rank: float = 0.40  # Att3：BB 寬度 <= 過去 252 日 40th pctile

    # 雙閘門（絕對 + 相對）— Att3 啟用：絕對 < 5% 且分位數 <= 40th 同時成立
    enable_absolute_backup: bool = True
    max_bb_width_ratio_absolute: float = 0.05  # 同 TLT-007 Att2 絕對閾值

    # 冷卻期（同 TLT-007 Att2）
    cooldown_days: int = 7


def create_default_config() -> TLT011Config:
    return TLT011Config(
        name="tlt_011_dynamic_regime_mr",
        experiment_id="TLT-011",
        display_name="TLT Dynamic BB-Width Percentile Regime MR",
        tickers=["TLT"],
        data_start="2017-01-01",  # 需要 252 日 percentile 暖機 + BB(20) 暖機
        profit_target=0.025,  # +2.5%（同 TLT-007）
        stop_loss=-0.035,  # -3.5%（同 TLT-007）
        holding_days=20,
    )
