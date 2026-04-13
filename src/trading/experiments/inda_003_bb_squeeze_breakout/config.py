"""
INDA-003: BB Squeeze Breakout → 20日回檔+2日急跌均值回歸
(INDA BB Squeeze → 20-Day Pullback + 2-Day Decline Mean Reversion)

前 2 個實驗均為均值回歸策略（10日回檔+WR+ATR），最佳 min(A,B) Sharpe 僅 0.15。

Att1: BB(20,2.0) + 30th pct squeeze + SMA(50) + TP2.5%/SL2.5%/20天 + cd10
  → Part A 0.53 (13訊號, WR 76.9%), Part B -0.41 (8訊號, WR 37.5%)
  嚴重市場狀態依賴（WR 76.9% → 37.5%），突破在 2024-2025 失效

Att2: 放寬 TP 至 3.0% + SL 至 -3.5%
  → Part A 0.72 (WR 84.6%), Part B -0.48 (WR 37.5%)
  放寬 SL 反增虧損（失敗突破不反彈），確認 BB Squeeze 對 INDA 無效

Att3: 完全轉換策略 — 20日回檔+2日急跌均值回歸
  設計理據：
  - GLD（vol 1.12%）最佳使用 20日回看窗口（GLD-012 Att3 Sharpe 0.48）
  - INDA vol 0.97% 更低，20日窗口應捕捉更深、更有意義的回檔
  - 2日跌幅替代 ATR 過濾，直接衡量急性賣壓而非波動率比
  - 保留 WR(10)+ClosePos（INDA-002 已驗證有效）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA003Config(ExperimentConfig):
    """INDA-003 20日回檔+2日急跌均值回歸參數"""

    # 進場 — 回檔（20日回看）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.04  # 回檔 >= 4%（20日窗口需更深門檻）
    pullback_cap: float = -0.10  # 回檔 <= 10%（20日窗口的崩盤隔離）

    # 進場 — 2日急跌
    decline_days: int = 2
    decline_threshold: float = -0.015  # 2日跌幅 >= 1.5%

    # 進場 — Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾
    close_position_threshold: float = 0.4

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> INDA003Config:
    return INDA003Config(
        name="inda_003_bb_squeeze_breakout",
        experiment_id="INDA-003",
        display_name="INDA 20-Day Pullback + 2-Day Decline MR",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%（同 INDA-002 Att1 已驗證）
        stop_loss=-0.04,  # -4.0%（同 INDA-002 Att1 已驗證）
        holding_days=20,
    )
