"""
TLT Capitulation-Confirmed Vol-Regime-Gated Mean Reversion 配置 (TLT-010)

實驗動機：
- TLT-007 Att2 為當前最佳（Part A Sharpe 0.12 / Part B 0.65 / min 0.12），
  但 Part A 12 訊號中 5 筆到期訊號（接近零報酬）主導 std 拖累 Sharpe：
    2020-08-12 -0.40%、2020-12-02 -0.09%、2021-01-06 -2.38%、
    2021-09-27 +1.36%、2023-05-16 -0.56%。這些訊號屬於「慢磨下跌」
    結構（signal day 前後波動低、反彈動能不足），而非真正的急跌
    capitulation。
- TLT-007 Att2 的 BB 寬度 regime 閘門過濾了 2022 升息期高波動訊號，
  但無法區分低 BB 寬度期間的「慢磨下跌」vs「短促急跌」訊號。
- TLT-008（pair vs IEF）、TLT-009（外部 ^TNX yield velocity）皆結構
  性失敗（見 EXPERIMENTS_TLT.md），確認外部利率數據作為濾波器受限。

嘗試方向（repo 中未曾嘗試於 TLT）：**2-day decline floor 加深方向**
（cross-asset lesson #19 驗證於 EEM-014 Att2 / INDA-010 Att3 / USO-013
 成功）。核心思想：
- 在 TLT-007 Att2 的 vol-regime gate 之上額外要求「訊號日 2 日累積
  報酬 <= -1.5%」，確保訊號為急跌 capitulation 而非慢磨漂移
- 2DD 為「signal-day capitulation confirmation」濾波器，不屬於 lesson
  #5 警告的「進場日趨勢濾波」——其作用是要求近期已發生一段真實
  下跌，而非要求未下跌

設計理念（執行模型同 TLT-007）：
- 繼承 TLT-007 Att2 完整進場（pullback 3-7% + WR ≤ -80 + ClosePos ≥ 40%
  + BB(20,2) 寬度/Close < 0.05）
- 新增：2 日累積報酬 <= two_day_decline_threshold（Att1: -1.5%）
- 出場沿用 TLT-002/TLT-007：TP +2.5% / SL -3.5% / 20 天

迭代紀錄：
  Att1 (two_day_decline_threshold=-0.015, floor direction)：測試中
    2DD <= -1.5% 作為 capitulation-confirmation 濾波，預期移除
    TLT-007 Att2 Part A 的近零到期訊號，同時保留 Part B 的急跌反彈訊號
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT010Config(ExperimentConfig):
    """TLT-010 Capitulation-Confirmed Vol-Regime-Gated MR 參數"""

    # 回檔範圍進場（同 TLT-007）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R（同 TLT-007）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-007）
    close_position_threshold: float = 0.4

    # 波動率 regime 閘門（同 TLT-007 Att2）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # 新增：2 日累積報酬 capitulation 濾波（Att1: -1.5% floor）
    two_day_decline_lookback: int = 2
    two_day_decline_threshold: float = -0.015  # 2 日累積報酬 <= -1.5%

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT010Config:
    return TLT010Config(
        name="tlt_010_capitulation_regime_mr",
        experiment_id="TLT-010",
        display_name="TLT Capitulation-Confirmed Vol-Regime MR",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,  # +2.5%（同 TLT-007）
        stop_loss=-0.035,  # -3.5%（同 TLT-007）
        holding_days=20,
    )
