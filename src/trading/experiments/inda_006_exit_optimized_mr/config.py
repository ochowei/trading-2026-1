"""
INDA-006: Exit-Optimized Mean Reversion
(INDA 出場優化均值回歸)

基於 INDA-005 Att3 框架，探索進場/出場參數優化：

Att1: TP +3.5% / SL -4.0% / 12天持倉
  → Part A 0.23 / Part B 0.21 → min 0.21（劣於 INDA-005 Att3 的 0.23）
  → 12天持倉將 Part B 近 TP 交易轉為到期（+1.95%, +2.79% 未達 +3.5%）
  → 結論：15天為持倉甜蜜點，12天過短

Att2: 移除 ClosePos 過濾 + TP +3.5% / SL -4.0% / 15天
  → Part A 0.08 / Part B 0.33 → min 0.08（嚴重劣化）
  → 移除 ClosePos 增加 Part A 7 個低品質訊號（含 3 SL），Sharpe 0.23→0.08
  → Part B 微改善 0.31→0.33（但 Part A 崩壞抵銷）
  → 結論：ClosePos 對 INDA 是有效過濾器

Att3: 深回檔 4-7% + ClosePos ≥40% + TP +3.5% / SL -4.0% / 15天
  → Part A 0.22 (10訊號, WR70%) / Part B 0.38 (4訊號, WR50%) → min 0.22
  → 4% 門檻改善 Part B 品質（0.31→0.38），但 Part A 微降（0.23→0.22）
  → Part B 僅 4 訊號太薄，A/B 比 2.5:1 偏高
  → 結論：INDA-005 Att3 的 3-7% 回檔為最優，增至 4% 反而過濾掉有效訊號

總結：3 次嘗試均未超越 INDA-005 Att3（min 0.23），確認 INDA 在
pullback+WR+ATR 框架下參數空間已飽和。關鍵發現：
  1. 持倉 15天為甜蜜點（12天過短、18/20天過長）
  2. ClosePos 對 INDA 為有效過濾器（移除致 Part A Sharpe 崩壞 0.23→0.08）
  3. 回檔 3% 為最優門檻（4% 減少訊號但 Part A 品質未提升）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA006Config(ExperimentConfig):
    """INDA-006 出場優化均值回歸參數"""

    # 進場 — 回檔（Att3：加深至 4%）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.04  # Att3: 回檔 >= 4%（vs INDA-005 的 3%）
    pullback_cap: float = -0.07  # 回檔 <= 7%（隔離極端崩盤）

    # 進場 — Williams %R（同 INDA-005）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（Att3：恢復，已驗證對 INDA 有效）
    close_position_threshold: float = 0.4  # Att3: 恢復 ClosePos（Att2 驗證有效）

    # 進場 — 波動率自適應過濾（同 INDA-005）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 進場 — 2日急跌過濾（同 INDA-005，已知非綁定但保留一致性）
    drop_2d_threshold: float = -0.01  # 2日報酬 <= -1.0%

    # 冷卻期（同 INDA-005）
    cooldown_days: int = 7


def create_default_config() -> INDA006Config:
    return INDA006Config(
        name="inda_006_exit_optimized_mr",
        experiment_id="INDA-006",
        display_name="INDA Exit-Optimized Mean Reversion",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=15,  # Att3：維持 15天甜蜜點
    )
