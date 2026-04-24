"""
TLT Capitulation-Confirmed Vol-Regime-Gated Mean Reversion 配置 (TLT-010)

實驗動機：
- TLT-007 Att2 為當前最佳（Part A Sharpe 0.12 / Part B 0.65 / min 0.12），
  但 Part A 12 訊號中 5 筆到期訊號（接近零報酬）主導 std 拖累 Sharpe。

嘗試方向（repo 中未曾嘗試於 TLT）：signal-day secondary filter 疊加於
TLT-007 Att2。本實驗 Att1 測試 2DD floor，Att2 測試 2DD cap（方向反向）。

迭代紀錄：
  Att1 (two_day_decline_threshold=-0.015, floor direction)：**FAILED**
    Part A 6/33.3% WR/Sharpe -0.11 cum -1.61%（2 TP / 1 SL / 3 Expiry）
    Part B 3/100% WR/Sharpe 0.00 zero-var cum +7.69%
    min(A,B) -0.11（vs TLT-007 Att2 的 0.12）
    失敗分析：2DD floor 移除 3 Part A TPs（2019-07-12/2021-08-11/
    2022-02-07 淺 2DD 贏家）+ 2 SLs；引入 cooldown-shift 新 SL
    2020-06-03（lesson #19）；Part B 移除 3/6 winners
    核心發現：TLT winners 分布橫跨淺深 2DD，floor 方向無結構性選擇力
    **轉換方向至 Att2：2DD cap（exclude deep 2DD）**，理論為 TLT 深 2DD
    為「continuation wave」而非 capitulation（2020-05-26、2021-02-04 SLs
    皆為深 2DD 訊號）

  Att2 (two_day_decline_threshold=-0.02, cap direction CIBR-012 風格)：測試中
    require TwoDayReturn >= -2.0%（排除加速崩盤訊號）。預期保留 TLT-007
    Att2 的淺 2DD 贏家（2019-07-12、2021-08-11 等）並移除深 2DD SLs
    （2020-05-26、2021-02-04）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT010Config(ExperimentConfig):
    """TLT-010 Capitulation-Confirmed Vol-Regime-Gated MR 參數"""

    # 回檔範圍進場（同 TLT-007）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_upper: float = -0.07

    # Williams %R（同 TLT-007）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-007）
    close_position_threshold: float = 0.4

    # 波動率 regime 閘門（同 TLT-007 Att2）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # 2 日累積報酬濾波（Att1 floor -1.5% 失敗，Att2 轉為 cap -2.0%）
    two_day_decline_lookback: int = 2
    two_day_decline_threshold: float = -0.02
    two_day_decline_as_cap: bool = True  # True = cap（>=），False = floor（<=）

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT010Config:
    return TLT010Config(
        name="tlt_010_capitulation_regime_mr",
        experiment_id="TLT-010",
        display_name="TLT Capitulation-Confirmed Vol-Regime MR",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,
        stop_loss=-0.035,
        holding_days=20,
    )
