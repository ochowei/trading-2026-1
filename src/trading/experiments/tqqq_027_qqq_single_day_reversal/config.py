"""TQQQ-027 QQQ Single-Day Momentum-Reversal → Trade TQQQ 配置

策略方向：**均值回歸 / 單日動量反轉 (Single-Day Momentum Reversal MR)**。
直接驗證 TQQQ-019~024 AI_CONTEXT 多次明確列出之未驗證假設：
「underlying QQQ short-term momentum reversal（單日反轉模式，未試）」。

實驗動機 (Problem statement)：
- repo 中 TQQQ 既有 26 次實驗皆為 -15% extreme capitulation framework
  變體（TQQQ-001~014/018~026）或 QQQ 多日動量/突破（TQQQ-006/015）或
  TQQQ 自身 gap-down 反轉（TQQQ-016），**從未測試「QQQ 單日急跌 +
  日內反轉」這個更短週期、更高頻的純均值回歸維度**。
- 假設：QQQ（1x NDX，無 -3x decay 噪音）單日急跌（ROC(1) <= 閾值）但
  當日收於日內區間上半部（ClosePos 高 = 多方尾盤承接 = 日內反轉），
  隔日開盤買 TQQQ 取 3x 放大短線反彈。

迭代計畫（最多三次）：
- Att1: QQQ ROC(1) <= -2.5% + QQQ ClosePos >= 0.50（中度急跌 + 日內反轉）
- Att2: 視 Att1 結果 tune ROC 閾值 / ClosePos
- Att3: 替代維度 — 加 QQQ 量能放大確認 或 收緊 ClosePos

跨資產脈絡：
- 對比 TQQQ-016（TQQQ 自身 Gap-Down + 日內反轉，3 次失敗：QQQ 盤外
  流動性有限使日內反彈常為技術性反應而非真正底部）——TQQQ-027 改用
  QQQ（underlying，1x，較乾淨）單日 ROC + ClosePos，測試是否較 TQQQ
  自身 gap-down 維度乾淨。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQ027Config(ExperimentConfig):
    """TQQQ-027 QQQ Single-Day Momentum-Reversal 參數（訊號基於 QQQ，交易 TQQQ）"""

    qqq_ticker: str = "QQQ"

    # Att1: qqq_roc1_threshold=-2.5, qqq_min_closepos=0.50
    # Att2: tune ROC / ClosePos
    # Att3: + QQQ 量能確認 或 收緊 ClosePos
    # Att1: roc1=-2.5, closepos=0.50 → Part A 1 訊號(0% WR -8.09% SL) /
    #   Part B 3 訊號(100% WR +22.50%) — 過嚴過稀（4 訊號/7yr），Part A
    #   訊號流崩潰 → REJECT
    # Att2 ★ (saved as default — 最佳迭代): roc1=-2.0, closepos=0.40 →
    #   Part A 7/57.1%/Sharpe 0.07 / Part B 4/75%/0.49 → min(A,B) 0.07
    #   REJECT（單日反轉噪音大，Part A 3 SL/7，無深度 capitulation 脈絡使
    #   低品質技術性反彈混入）— 但為唯一有實質訊號流的迭代
    # Att1: roc1=-2.5, closepos=0.50 → Part A 1/0%/-8.09% SL + Part B
    #   3/100% — 過嚴過稀（4 訊號/7yr）Part A 訊號流崩潰 REJECT
    # Att3: + QQQ 量能 >1.3x + closepos 0.45 → Part A 1/0%/-8.09% SL +
    #   Part B 3/100% — 量能濾過度收斂，Part A 1 訊號全敗 REJECT
    qqq_roc1_threshold: float = -2.0  # QQQ 單日報酬 <= -2.0%
    qqq_min_closepos: float = 0.40  # (Close-Low)/(High-Low) >= 0.40（日內反轉）

    use_qqq_volume_filter: bool = False
    qqq_volume_multiplier: float = 1.3
    qqq_volume_sma_period: int = 20

    cooldown_days: int = 3
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ027Config:
    return TQQQ027Config(
        name="tqqq_027_qqq_single_day_reversal",
        experiment_id="TQQQ-027",
        display_name="TQQQ QQQ Single-Day Momentum-Reversal MR → Trade TQQQ",
        tickers=["TQQQ"],
        data_start="2018-06-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,
        stop_loss=-0.08,
        holding_days=10,
    )
