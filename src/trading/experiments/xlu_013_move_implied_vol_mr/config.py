"""
XLU MOVE Implied-Volatility Forward-Looking Regime-Gated MR (XLU-013)

實驗動機：
- XLU-012 Att3 為當前全域最優（min(A,B) 0.75，Part A 0.75 / Part B 1.59）
- A/B 累計差 31.7%（略高於 30% 目標）+ A/B 訊號比 1.75:1（略高於 1.5:1）
- 殘留問題：Part A 1 筆 SL（2021-09-20 FOMC 鷹派衝擊 -4.10%，發生於 Fed 釋出 taper
  signal 前夕，bond market 隱含波動劇烈跳升期）
- TLT-013（2026-05-01）以 ^MOVE 隱含波動率 forward-looking regime gate 首次突破
  TLT 結構性 0.12 ceiling（+17% Sharpe），其 config 明確列為待驗證跨資產假設：
  「^MOVE level filter 可能適用其他 rate-driven 資產（XLU, REITs）」

跨資產背景（lesson #24 v2 候選）：
- ^MOVE = Merrill Lynch Option Volatility Estimate，債券選擇權市場對未來 30 日
  Treasury yield 波動率的隱含預期。**結構上 forward-looking**，與 ^TNX (rate level) /
  BB-width (realized vol) / TLT 60d ROC（XLU-006 Att3 失敗）等 backward-looking
  指標本質不同。
- 假設：當 bond market 預期未來 30 日利率波動高（^MOVE 高），XLU 短期均值回歸
  失敗率上升（rate-uncertainty regime 持續壓抑 utility yield bid）；當 ^MOVE 低
  或下降（rate vol 預期回歸正常），XLU MR 訊號落於 calm rate regime 容易回歸。

設計理念：
- 沿用 XLU-012 Att3 完整框架（pullback 3.5-7% + WR(10)<=-80 + ClosePos>=0.4
  + ATR(5)/ATR(20)>1.15 + TP+3.0%/SL-4.0%/20d/cd7）
- 疊加 ^MOVE 過濾器作為**獨立第六維度**：MOVE Close <= max_move_level
- 出場、冷卻、進場全部不變，僅新增 1 個過濾條件以隔離 ^MOVE 邊際貢獻

XLU-012 Att3 訊號日 ^MOVE 預估分布（待回測實測）：
  Part A：2019-11-08 / 2020-10-30 / 2021-03-03 / 2021-06-24 / 2021-09-20（SL）/
          2022-12-19 / 2023-09-06 — 含 2 段 MOVE 高峰（2022-Q4 加息頂、2023-09 高峰）
  Part B：2024-01-18 / 2024-06-14 / 2024-11-04 / 2025-03-05 — MOVE 普遍中等

**設計取捨**：
- 嚴格 MOVE <= 100 → 可能誤殺 2022-12-19 / 2023-09-06 winners（MOVE 高位但 calm
  region 內），失去 Part A 兩 winners 後 SL/TP 比惡化
- 寬鬆 MOVE <= 130（TLT-013 sweet spot）→ 可能僅過濾 1 訊號（2021-09-20 SL 正
  位於 MOVE 跳升日）
- 因此 Att1 採 TLT-013 直接移植 130 為起點，Att2/Att3 視結果調整

Cross-asset 比較：
- TLT-013 Att1 max_move_level=130：過濾 2023-05-16 SL（MOVE 130.3）
- XLU-013 Att1 採同 130：預期過濾 XLU 上對應 bond-vol shock SL 訊號
- 二者差別：TLT 直接受 rate level 影響；XLU 透過 yield-spread 機制間接受 rate
  vol 影響，敏感度可能弱於 TLT
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU013Config(ExperimentConfig):
    """XLU-013 MOVE Implied-Vol Regime-Gated MR 參數"""

    # 進場 — 回檔（同 XLU-011 / XLU-012）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035
    pullback_cap: float = -0.07

    # 進場 — Williams %R（同 XLU-011 / XLU-012）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（同 XLU-011 / XLU-012）
    close_position_threshold: float = 0.4

    # 進場 — ATR 自適應過濾（同 XLU-011 / XLU-012）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # ^MOVE forward-looking implied vol regime gate（XLU-013 核心新增）
    move_ticker: str = "^MOVE"
    # Att3 ablation：max_move_level=999.0 effectively disables LEVEL cap，
    # 隔離測試 DIRECTION filter 單獨效果（與 Att2 比較確認 cap 是否冗餘）
    max_move_level: float = 999.0
    # ^MOVE direction filter — N 日 absolute change <= max_move_change
    # （正向上限過濾「Fed 政策訊號日 bond vol 跳升」結構，e.g. 2021-09-20 SL：
    #  MOVE 3d change +5.65，恰於 +5 邊界外）
    use_move_direction_filter: bool = True
    move_direction_lookback: int = 3
    max_move_change: float = 5.0

    # 冷卻期（同 XLU-011 / XLU-012）
    cooldown_days: int = 7


def create_default_config() -> XLU013Config:
    return XLU013Config(
        name="xlu_013_move_implied_vol_mr",
        experiment_id="XLU-013",
        display_name="XLU MOVE Implied-Vol Regime-Gated MR",
        tickers=["XLU"],
        data_start="2010-01-01",
        # 沿用 XLU-012 Att3 出場（TP+3.0%/SL-4.0%/20d 為 ATR 動能濾波後突破型甜蜜點）
        profit_target=0.030,
        stop_loss=-0.040,
        holding_days=20,
    )
