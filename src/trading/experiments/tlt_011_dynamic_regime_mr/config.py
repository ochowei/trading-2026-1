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
    """TLT-011 Dynamic BB-Width Percentile Regime MR 參數 (Att1 baseline)

    Att1（bb_width_pctile_lookback=252、max_bb_width_pctile_rank=0.50、
         enable_absolute_backup=False）：
      策略方向：252 日 rolling percentile rank <= 50%（中位數）作為 regime 閘門
      關鍵參數：lookback=252d、pctile<=50%、純動態無絕對閾值
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
    bb_width_pctile_lookback: int = 252  # Att1：252 交易日 ≈ 1 年
    max_bb_width_pctile_rank: float = 0.50  # Att1：BB 寬度 <= 過去 252 日 50th pctile

    # 雙閘門（絕對 + 相對）— Att1 不啟用，純動態 percentile
    enable_absolute_backup: bool = False
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
