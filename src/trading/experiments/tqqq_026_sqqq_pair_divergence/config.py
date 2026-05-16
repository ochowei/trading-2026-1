"""TQQQ-026 TQQQ/SQQQ Inverse-Pair Capitulation Confirmation 配置

策略方向：**配對交易 (Pair Trading)** — repo 中 TQQQ 未曾嘗試之方向。
直接驗證 TQQQ-021/024 AI_CONTEXT 明確列出之未驗證假設：
「TQQQ vs SQQQ inverse pair（同一 underlying 槓桿配對，未試）」。

實驗動機 (Problem statement)：
- 當前全域最優 TQQQ-025 Att2（雙 Part std=0 全勝）建立於 TQQQ-018 Att3
  框架（DD≤-15% + RSI(5)<25 + Vol>1.5x + BB-width<0.48 + DD(T-5)≤-1%）。
- SQQQ 為 -3x QQQ inverse ETF，與 TQQQ 為「同一 underlying（NDX）的反向
  槓桿配對」。真正的 TQQQ capitulation 底部，理論上應同時對應 SQQQ 的
  極端超買 + 量能耗竭（panic exhaustion at the inverse-pair top）。
- 假設：以 SQQQ RSI(5) 極端超買作為「inverse-pair 恐慌確認」FLOOR，可
  過濾「TQQQ 緩跌 drift（SQQQ 並未進入恐慌極端）」的低品質訊號（如
  TQQQ-018 Att3 殘餘 Part A SL 2021-09-28 supply-chain slow drift）。

迭代計畫（最多三次）：
- Att1: SQQQ RSI(5) FLOOR >= 70（中度 inverse-pair 恐慌確認）
- Att2: 視 Att1 結果 tighten/loosen FLOOR（>= 80 或 >= 60）
- Att3: 替代維度 — SQQQ 量能放大確認（SQQQ Volume > 1.5x SMA20）

跨資產脈絡：
- Repo 首次「leveraged ETF inverse-pair（TQQQ/SQQQ，同一 underlying 反向
  槓桿）confirmation gate」於任何資產（既有 cross-asset divergence 皆為
  不同 underlying：QQQ-SPY TQQQ-022、EEM-EFA EEM-017）。
- 若 SUCCESS：擴展至其他 leveraged inverse pair（SOXL/SOXS、SPXL/SPXS）。
"""

from dataclasses import dataclass

from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config


@dataclass
class TQQQ026Config(TQQQ018Config):
    """TQQQ-026 TQQQ/SQQQ Inverse-Pair Confirmation 參數

    在 TQQQ-018 Att3 完整框架上疊加 SQQQ inverse-pair 恐慌確認 FLOOR。
    """

    sqqq_ticker: str = "SQQQ"

    # Att1: use_sqqq_rsi_filter=True, min_sqqq_rsi=70 (volume off)
    # Att2: tighten/loosen min_sqqq_rsi
    # Att3: use_sqqq_volume_filter=True (alternative dimension)
    use_sqqq_rsi_filter: bool = True
    sqqq_rsi_period: int = 5
    # 訊號日 SQQQ RSI(5) 必須 >= min_sqqq_rsi（inverse-pair 恐慌極端確認）
    # Att1: min_sqqq_rsi=70 → Part A/B 完全等於 baseline（完全非綁定，
    #   SQQQ RSI 與 capitulation 結構性共線，TQQQ -15% 崩跌必使 SQQQ RSI 飆升）
    #   min(A,B) 0.80 TIE baseline
    # Att2 ★ (saved as default): min_sqqq_rsi=80 → Part A 5W std=0 + Part B 5W
    #   std=0 雙 Part 全勝（surgical 過濾兩殘餘 SL：Part A 2021-09-28 +
    #   Part B 2025-03-06）但 Part A 重度衰減 10→5（移除 4 winners，reverse
    #   selection）→ A/B 年化 cum gap ~62% > 30% ❌ + signal gap 60% > 50% ❌
    #   → PARTIAL（structurally NO LOSS 但未達 acceptance criteria，未超越
    #   現任最佳 TQQQ-025 Att2）
    # Att3: min_sqqq_rsi=75 → Part A 10/1SL Sharpe 1.21（2021-09-28 SL 殘存，
    #   SQQQ RSI ∈ [75,80)）/ Part B 5W std=0（2025-03-06 SL 過濾）→
    #   min(A,B)† 1.21 PARTIAL（+51% vs baseline 0.80，等同 TQQQ-025 Att1
    #   pattern，但 Part A 仍 1 SL）
    min_sqqq_rsi: float = 80.0

    use_sqqq_volume_filter: bool = False
    sqqq_volume_multiplier: float = 1.5
    sqqq_volume_sma_period: int = 20

    # 成交模型參數（同 TQQQ-018）
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ026Config:
    return TQQQ026Config(
        name="tqqq_026_sqqq_pair_divergence",
        experiment_id="TQQQ-026",
        display_name=(
            "TQQQ/SQQQ Inverse-Pair Capitulation Confirmation on Vol-Regime-Gated Capitulation Buy"
        ),
        tickers=["TQQQ"],
        data_start="2018-06-01",  # 暖機 BB(20) + SQQQ RSI 對齊
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
