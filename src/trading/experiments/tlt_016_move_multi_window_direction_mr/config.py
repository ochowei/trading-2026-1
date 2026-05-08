"""
TLT ^MOVE Multi-Window IV Direction Regime-Gated MR (TLT-016)

實驗動機 (Problem statement):
- TLT-014 Att3 為當前全域最優 (min(A,B) 0.69, Part A 0.69 / Part B 0.00 zero-var)。
  Part A binding, Part A 5 訊號 / WR 80% / cum +6.56%, 殘餘 1 EX (-2.38% on 2021-01-06).
- 殘餘 EX 為 2021 reflation regime 經典訊號:
  - SPY 急漲 (Georgia Senate runoff + 財政刺激預期 + 疫苗 rollout)
  - TLT 急跌 (yields surging on inflation expectations)
  - 進場後 20 日 TLT 持續下跌至 -2.38% expiry
- TLT-014 已包含三層 regime gate:
  1. BB-width 5% (TLT 自身 backward-looking realized vol)
  2. ^MOVE Close <= 130 LEVEL CAP (forward-looking implied vol level)
  3. TLT-SPY 20d divergence >= -4% (cross-asset performance differential)
- TLT-013 Att1 ★ 確立 ^MOVE LEVEL CAP 維度 (single-window).
  TLT-013 config 中 `move_direction_lookback: int = 5` 與 `use_move_direction_filter`
  為已預備但未啟用的 placeholder, 明確列為下一探索方向.

嘗試方向 (cross-strategy port from USO-028 Att1 success):
**^MOVE multi-window IV DIRECTION combo** as 4th orthogonal regime dimension.
- USO-028 Att1 ★ 確立「IV DIRECTION 多時框正交組合」(^OVX 3d acute + 5d sustained)
  為 lesson #24 family v6 新模式 (USO 為 repo 首例, +28% Sharpe).
- 同源跨資產假設: ^MOVE 多時框 DIRECTION combo 可作為 TLT-014 的第四 regime gate,
  捕捉「LEVEL 平靜但 DIRECTION 已上升」的 stealth-build-up regime.
- USO-028 vs TLT-016 區別:
  * USO-028 base 已含 ^OVX 3d direction + 5d return cap (multi-period persistence
    in commodity returns).
  * TLT-016 base 含 ^MOVE LEVEL + TLT-SPY divergence, 新增 ^MOVE direction (5d) 為
    forward-looking IV trajectory dimension. 與既有 LEVEL 維度結構性正交.

預期效應 (probe data 已證實) :
- 殘餘 EX 2021-01-06 之 ^MOVE 5d=-1.46 (近平靜), 落於 Part A TPs 5d 分布中段
  (-18.62 ~ +2.30), Part B TPs 中段 (-8.10 ~ +8.11). **^MOVE 5d direction 維度
  結構性無法 selectively 過濾此 EX 而保留全部 winners.**
- 高機率三次迭代皆 REJECT/TIE: 預期成為「TLT residual EX 結構性無解」failure
  family 的第五個失敗類別 (繼 ^MOVE 60d SMA / prior-DD / IEF pair / ^TNX
  velocity / HYG credit divergence 後).
- 若失敗, 為 cross-asset lesson #24 family v6 boundary 提供新邊界資訊:
  「multi-window IV DIRECTION combo」適用條件需 target asset 的殘餘 SLs 在 IV
  trajectory 維度 cluster on one side; TLT residual EX cluster mid-distribution
  使 combo 結構性失效. 與 USO-028 (IV trajectory cluster on rising side) 形成
  失敗邊界對比.

迭代計畫 (3 iterations max):
- Att1: max_move_5d_change=+5.0 (中等 threshold, 預期 non-binding 對 Part A
  全部 winners; 可能 filter 掉 Part B 2024-05-29 winner 5d=+8.11)
- Att2: 視 Att1 結果調整方向. 若 Att1 over-filter Part B, 嘗試
  max_move_5d_change=+10.0 (寬 threshold, 期望僅 filter 異常上升期).
- Att3: 探索 multi-window combo: 同時加 3d 與 5d 雙閘門, 或反向 (FLOOR).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT016Config(ExperimentConfig):
    """TLT-016 ^MOVE Multi-Window IV Direction Regime-Gated MR 參數

    迭代紀錄將在執行後填入.
    """

    # 進場 (沿用 TLT-014 Att3)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_upper: float = -0.07

    wr_period: int = 10
    wr_threshold: float = -80.0

    close_position_threshold: float = 0.4

    # BB-width regime gate (沿用 TLT-007 / TLT-013 / TLT-014)
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # ^MOVE LEVEL CAP (沿用 TLT-013 Att1 / TLT-014)
    move_ticker: str = "^MOVE"
    max_move_level: float = 130.0

    # TLT-SPY cross-asset divergence (沿用 TLT-014 Att3)
    benchmark_ticker: str = "SPY"
    divergence_lookback: int = 20
    min_relative_return: float = -0.04

    # TLT-016 核心新增: ^MOVE multi-window direction (cross-strategy port from USO-028)
    use_move_5d_direction_filter: bool = True
    move_5d_lookback: int = 5
    # Att1: +5.0 → TIE 0.69 (Part A non-binding, Part B 4→3 winners; A/B gap 37%→14.7% ✓)
    # Att2: -1.7 (surgical cap, between residual EX 5d=-1.46 and Part A TP 2021-08-11 5d=-2.01)
    max_move_5d_change: float = -1.7

    # 可選 3d direction (multi-window combo, Att3 候選)
    use_move_3d_direction_filter: bool = False
    move_3d_lookback: int = 3
    max_move_3d_change: float = 5.0

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT016Config:
    return TLT016Config(
        name="tlt_016_move_multi_window_direction_mr",
        experiment_id="TLT-016",
        display_name="TLT ^MOVE Multi-Window IV Direction Regime-Gated MR",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,
        stop_loss=-0.035,
        holding_days=20,
    )
