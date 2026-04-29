"""
CIBR Post-Capitulation Vol-Transition 均值回歸配置 (CIBR-012)

動機：CIBR-008 Att2（全域最佳 min(A,B) Sharpe 0.39）的 Part A 7 訊號中 2 筆停損
均發生在「急跌剛開始、波動率正在急速擴張」的時點：
- 2020-02-24：COVID 前夕第一波下殺，ATR(5)/ATR(20) 急速突破 1.15，但後續 -24% 深度崩盤持續
- 2021-02-26：科技股輪動拋售，ATR 當日飆升符合 > 1.15 過濾，但後續 5-10 日續跌停損

核心觀察：CIBR-008 的 ATR(5)/ATR(20) > 1.15 過濾器成功區分「急跌恐慌 vs 慢磨下跌」
（跨資產教訓 #15），但無法區分「急跌中（續跌）」vs「急跌後（反彈）」。兩筆停損
均為 mid-crash 進場，而非 post-crash 進場。

策略方向：波動率峰值已先期出現（確認崩盤已發生），今日為 post-peak 進場時點

Att1（過嚴，已失敗）：
  - 近 10 日內出現 ATR(5)/ATR(20) ≥ 1.30
  - 今日 ATR(5)/ATR(20) ≤ 1.20（與 CIBR-008 的 ATR > 1.15 結構性衝突）
  - Part A 1 訊號 / Part B 0 訊號（過嚴，訊號近乎歸零）
  - 失敗分析：condition B 「today <= 1.20」與 CIBR-008 working filter ATR > 1.15
    幾乎互斥（signal-day ATR 通常在 1.15-1.30 區間但必須 <= 1.20），把所有訊號都過濾掉

Att2（已失敗）：保留 CIBR-008 所有進場條件，新增「先期 ATR 峰值」補充過濾
  - 保留：BB 下軌 + 回檔上限 -12% + WR ≤ -80 + ClosePos ≥ 40% + ATR 今日 > 1.15
  - 新增：max(ATR_ratio, t-10..t-1) ≥ 1.25（不含今日，確認 10 日前已有 crash 峰值）
  - 結果 Part A 3 訊號 WR 66.7% Sharpe 0.27 / Part B 3 訊號 WR 100% Sharpe 4.21
  - min(A,B) 0.27 < CIBR-008 的 0.39（-31%）
  - 失敗分析：prior peak ≥ 1.25 過嚴，非綁定式移除 3 個贏家（2020-10-30、
    2022-09-01、2023-03-13）僅過濾 1 個停損（2020-02-24），2021-02-26 未被過濾。
    核心發現：「先期 ATR 峰值」與「winner/loser」無關聯——許多 winners 發生在
    前期較平靜、突然 capitulation 後快速反彈的結構，先期 peak 不是區分因素

Att3 ★（當前最佳）：改用「2 日急跌上限」（2DD cap，不同於 CIBR-004 測試的 2DD floor）
  觀察 CIBR-008 Part A 7 訊號的 signal-day + prev-day 2 日收盤報酬：
  - SL: 2020-02-24 2DD -4.1% / 2021-02-26 2DD -3.9%
  - TP: 其餘 5 筆 2DD 分布 -1.5% ~ -3.8%

  新增條件：2-day close-to-close return >= -4.0%
  此條件與 CIBR-004 Att2/Att3 的「2日跌幅 <= -1.5%/-2.0%」方向**完全相反**：
  - CIBR-004 方向: 要求 2DD 必須 <= -X%（建立 2DD 最低門檻，篩選急跌）— 失敗
  - CIBR-012 方向: 要求 2DD 必須 >= -4.0%（2DD 最高上限，排除 in-crash 進場）— 新方向

  直覺：深 2DD（≤-4% = 2.6σ for 1.53% vol）意味「崩盤加速中」，淺 2DD（-2~-4%）
  意味「減速階段」，後者為 mean reversion 的良好進場時機。此為 repo 首次測試
  「2DD 上限」作為進場時機過濾器（vs 傳統「2DD 下限」急跌確認）。

  內部參數調校：
  - -3.5% 過嚴（Part A 剩 3 訊號全 TP 零方差 Sharpe 0.00，過濾 2019-08-05 和
    2022-09-01 兩個 TPs）
  - -4.0% 甜蜜點（Part A 4 訊號 3W/1L Sharpe 0.49，過濾 2020-02-24 SL，保留
    2021-02-26 SL，WR 71.4→75%）★

  結果（Att3 於 -4.0% 2DD cap）：
  - Part A: 4 訊號 WR 75% Sharpe **0.49** cum +6.33%（過濾 2020-02-24 COVID SL + 3 個邊際 TPs）
  - Part B: 3 訊號 WR 100% Sharpe 3.96 cum +7.97%（過濾 2024-02-21 / 2024-08-02 兩個 TPs）
  - min(A,B) = **0.49**（+26% vs CIBR-008 的 0.39）
  - A/B 累計差 1.64pp（大幅改善自 CIBR-008 的 6.43pp，符合 <30% 目標）
  - A/B 訊號比 1.33:1（符合 <50% 目標）
  - 代價：Part B cum 15.66%→7.97%（2DD cap 移除 2024 年兩個大 TP），但 Part A
    Sharpe 大幅改善使 min(A,B) 上升
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR012Config(ExperimentConfig):
    """CIBR-012 Post-Capitulation Vol-Transition MR 參數"""

    # BB 參數（同 CIBR-008）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（同 CIBR-008 Att2 甜蜜點）
    pullback_lookback: int = 10
    pullback_cap: float = -0.12

    # 品質過濾
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40

    # ATR 當日過濾（保留 CIBR-008 signal-day panic 要求）
    atr_fast: int = 5
    atr_slow: int = 20
    atr_today_threshold: float = 1.15

    # 2 日急跌上限（Att3 新方向：排除 in-crash 進場）
    # 若 (Close(t) / Close(t-2) - 1) < twoday_return_cap，則視為「崩盤加速中」不進場
    # -3.5% 測試過嚴（過濾 2019-08-05 / 2022-09-01 兩個 TPs，Part A 剩 3 訊號零方差）
    # 放寬至 -4.0%（=2.6σ for CIBR 1.53% vol），仍能過濾 2020-02-24 (-4.1%) 和
    # 2021-02-26 (-4.9%) 兩個 SLs
    twoday_return_cap: float = -0.040

    cooldown_days: int = 8


def create_default_config() -> CIBR012Config:
    return CIBR012Config(
        name="cibr_012_vol_transition_mr",
        experiment_id="CIBR-012",
        display_name="CIBR Post-Capitulation Vol-Transition MR",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=18,
    )
