"""TQQQ-028 TQQQ BB Squeeze Breakout 配置

策略方向：**突破 (Breakout) / 趨勢啟動**。
直接驗證 TQQQ-024 AI_CONTEXT 列出未驗證假設：
「BB Squeeze Breakout 於 TQQQ 本身（TQQQ-015 為 QQQ → trade TQQQ，方向不同）」。

實驗動機 (Problem statement)：
- TQQQ-015 為 **QQQ** BB Squeeze / 動量 → trade TQQQ（訊號源為 1x QQQ），
  3 次失敗。**從未於 TQQQ 自身計算 BB squeeze + 上軌突破**。
- 假設：TQQQ（3x NDX）波動率收縮（BB 寬度/Close 極低 = squeeze）後
  收盤突破 BB 上軌 = 趨勢啟動 ignition，順勢做多取 3x 放大趨勢段。

迭代計畫（最多三次）：
- Att1: BB(20,2) squeeze（前日 BB_Width/Close < 0.20）+ 當日 Close > BB_Upper
        ，TP+10%/SL-8%/15d
- Att2: 視 Att1 結果 tune squeeze 閾值 / TP / 持倉
- Att3: 替代維度 — 加量能放大確認 或 突破前 N 日高點

跨資產脈絡：
- 對比 TQQQ-015（QQQ BB squeeze，3 次失敗：QQQ 突破訊號在 TQQQ 幅度
  不足、TP+12% 過高）——TQQQ-028 改用 TQQQ 自身 BB（3x 已放大波動），
  測試 squeeze→breakout 於高波動 leveraged ETF 本身是否成立。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TQQQ028Config(ExperimentConfig):
    """TQQQ-028 TQQQ BB Squeeze Breakout 參數"""

    bb_period: int = 20
    bb_std: float = 2.0

    # Att1: squeeze=0.20, breakout, vol off → Part A 22/59.1%/Sharpe 0.29 /
    #   Part B 11/45.5%/Sharpe -0.03 cum -6.48% → min(A,B) -0.03 REJECT
    #   （breakout 在 3x TQQQ whipsaw 嚴重，Part B 45.5% WR）
    # Att2: squeeze=0.15 + 量能>1.5x → Part A 1/100%/+10%, Part B 0, Part C 0
    #   — squeeze 0.15 對 3x TQQQ 過嚴（TQQQ BB width/Close 罕 < 0.15），
    #   +量能後完全崩潰 REJECT（無訊號流）
    # Att3 ★ (saved as default): squeeze=0.20（回 Att1 有訊號流）+ 量能 off
    #   + 長期趨勢 bull regime filter（Close > SMA200，僅牛市取突破，針對
    #   Att1 Part B 2022/2025 非牛市假突破之根本修正）
    squeeze_max_bb_width: float = 0.20  # 前日 BB 寬度/Close < 此值 = 波動收縮
    require_breakout: bool = True  # 當日 Close > BB_Upper

    use_volume_filter: bool = False
    volume_multiplier: float = 1.5
    volume_sma_period: int = 20

    # Att3：長期趨勢 bull regime filter（breakout 順勢，非 MR，不違反 lesson #5）
    use_trend_filter: bool = True
    trend_sma_period: int = 200

    cooldown_days: int = 5
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ028Config:
    return TQQQ028Config(
        name="tqqq_028_bb_squeeze_breakout",
        experiment_id="TQQQ-028",
        display_name="TQQQ BB Squeeze Breakout (TQQQ-native)",
        tickers=["TQQQ"],
        data_start="2018-06-01",  # 暖機 BB(20)
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.10,
        stop_loss=-0.08,
        holding_days=15,
    )
