"""SOXL Volatility-Regime-Gated Capitulation Buy 配置 (SOXL-012)

實驗動機（lesson #23 跨資產移植自 TQQQ-018 / TLT-007 Att2）：
- SOXL-006（精選超賣均值回歸）為當前 cum 報酬最佳但 min(A,B) 僅 0.47；
  SOXL-010 Att3（板塊 RS 動量）為 min(A,B) 全域最優 0.70（11 次實驗）
- TQQQ-018 證明在 3x 槓桿 ETF 上，BB(20,2) 寬度 / Close 為極端 vol regime 的有效切除器：
  TQQQ-010 Part A Sharpe 0.36 → TQQQ-018 Att3 Part A 0.80（+122%）
- TLT-007 與 TQQQ-018 共同驗證 lesson #23：BB-width regime gate 對「單一極端 vol regime
  episode」資產有效（TLT 2022 升息、TQQQ 2022 科技熊市）
- SOXL 同樣經歷 2022 全年半導體熊市（單一極端 vol episode），結構性適合此 framework

跨資產假設：
- SOXL 為 3x leveraged sector ETF（半導體），日波動 ~6%（高於 TQQQ ~5%）
- 2020-03 COVID（單週極端）+ 2022 全年熊市為兩段可被 BB 寬度切除的高 vol regime
- 切除後 Part A Sharpe 預期顯著提升，Part B（2024-2025 bull regime）幾乎不受影響

與 SOXL-009（純 BB Squeeze Breakout）的區別：
- SOXL-009 為突破策略（趨勢跟蹤），三次嘗試 Part B 均負（Sharpe -0.15~-0.51）
- SOXL-012 為均值回歸策略（買恐慌），BB-width 為「波動率 regime classifier」（過濾極端
  vol 環境），非「進場日方向過濾」，不違反 lesson #5

執行模型：next_open_market 進場、limit_order 止盈、stop_market 停損、悲觀認定、
滑價 0.1%、3x 槓桿適用標準成交模型。

迭代紀錄（最多三次）：
  Att1（max_bb_width_ratio=0.55）：
    SOXL 日波動 ~6% (vs TQQQ ~5%)，BB-width threshold 預期略高於 TQQQ 0.48。
    0.55 為初步甜蜜點預測。
"""

from dataclasses import dataclass

from trading.experiments.soxl_006_selective_oversold.config import (
    SOXLSelectiveOversoldConfig,
)


@dataclass
class SOXL012Config(SOXLSelectiveOversoldConfig):
    """SOXL-012 Volatility-Regime-Gated Capitulation Buy 參數"""

    # 沿用 SOXL-006 的進場與出場參數：
    # drawdown_lookback=20, drawdown_threshold=-0.25, drawdown_cap=-0.40,
    # rsi_period=5, rsi_threshold=20.0, drop_2d_threshold=-0.08,
    # cooldown_days=7, profit_target=0.18, stop_loss=-0.12, holding_days=25

    # 波動率 regime 閘門（新增）：BB(bb_period, bb_std) 寬度 / Close < max_bb_width_ratio
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.55

    # 「進場前已在回撤」過濾器
    # T-N 日的 Drawdown 必須 <= prior_drawdown_lookback_threshold
    # 設計目的：過濾「first-day-of-decline」pattern（如 2025-12-17 DD-5d 僅 -0.9%）
    enable_prior_drawdown_filter: bool = False
    prior_drawdown_lookback: int = 5
    prior_drawdown_threshold: float = -0.03


def create_default_config() -> SOXL012Config:
    return SOXL012Config(
        name="soxl_012_regime_vol_gate",
        experiment_id="SOXL-012",
        display_name="SOXL Volatility-Regime-Gated Capitulation Buy",
        tickers=["SOXL"],
        data_start="2018-06-01",  # 暖機 BB(20)
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.18,
        stop_loss=-0.12,
        holding_days=25,
    )
