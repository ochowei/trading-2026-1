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
- TLT-007 Att2 Part A 5 筆到期訊號的共同特徵：訊號日當日 2DD 偏淺
  （通常 0% ~ -1%），反映非急跌環境。2DD 濾波預期移除這 5 筆中的
  多數，提升 Part A Sharpe；Part B 6 筆訊號多為急跌反彈（2024-04、
  2024-05、2025-02、2025-03 等），預期保留主要訊號

與既有失敗方向的區分：
- TLT-006 Day-After Capitulation（Close > Prev High 強反轉 K 線）失敗：
  T-1 為極端急跌而 T 須強反彈，在 TLT 2024-2025 高利率高原期過嚴
- 本實驗 2DD 濾波僅要求 signal day 當下的 2 日報酬已深；signal day
  本身仍保留 ClosePos >= 40% 的 lenient 反轉條件，不要求 strong
  bullish reversal

設計理念（執行模型同 TLT-007）：
- 繼承 TLT-007 Att2 完整進場（pullback 3-7% + WR ≤ -80 + ClosePos ≥ 40%
  + BB(20,2) 寬度/Close < 0.05）
- 新增：2 日累積報酬 <= two_day_decline_threshold（Att1: -1.5%）
- 出場沿用 TLT-002/TLT-007：TP +2.5% / SL -3.5% / 20 天

迭代紀錄：
  Att1 (two_day_decline_threshold=-0.015, floor direction)：**FAILED**
    Part A 6/33.3% WR/Sharpe **-0.11** cum -1.61%（2 TP / 1 SL / 3 Expiry）
    Part B 3/100% WR/Sharpe 0.00 zero-var cum +7.69%（3 TP，過嚴移除 3 筆
    TLT-007 Part B 贏家）
    失敗分析：2DD floor 方向（2DD <= -1.5%）預期移除慢磨下跌的近零到期，
    實際上 TLT 贏家分布橫跨淺深 2DD。removed 3 TPs (2019-07-12/2021-08-11/
    2022-02-07) + 2 SLs but introduced cooldown-shift 2020-06-03 new SL
    （lesson #19）. Part B kept only 3/6 winners — 2DD floor 在 TLT 反向
    移除好訊號。**轉換方向至 Att2：2DD cap（exclude deep 2DD）**，理論為
    TLT 深 2DD 為「continuation wave」而非 capitulation（2020-05-26/
    2021-02-04 SLs 皆為深 2DD 訊號）

  Att2 (two_day_decline_threshold=-0.02, cap direction CIBR-012 風格)：**FAILED**
    Part A 9/55.6% WR/Sharpe **0.02** cum +0.28%（4 TP / 1 positive expiry /
    2 SL / 2 neg expiry + 1 cooldown shift SL 2020-12-04 -3.01%）
    Part B 5/80% WR/Sharpe 0.52 cum +6.41%（4 TP / 1 SL — 2024-04-08 SL 保留，
    但 2024-05-29 TP 因 2DD 過深被過濾）
    min(A,B) **0.02**（vs TLT-007 Att2 的 0.12，-83%）
    失敗分析：2DD cap 雖移除 3 個 Part A 近零負值到期（2020-08-12/
    2020-12-02/2021-01-06），但同時：(a) 移除 2020-11-09 TP（深 2DD
    贏家）、(b) 引入 cooldown shift 新 SL 2020-12-04 -3.01%（lesson
    #19）、(c) 移除 2024-05-29 Part B TP。驗證 TLT 2DD 分布無方向性
    選擇力，cap/floor 皆失敗。**轉換方向至 Att3：ATR(5)/ATR(20) 波動
    率擴張濾波**（repo 首次於 TLT 測試 ATR）

  Att3 (use_atr_expansion=True, atr_fast=5, atr_slow=20, atr_ratio_min=1.05)：
    停用 2DD 濾波。加上 ATR(5)/ATR(20) >= 1.05 要求近 5 日實現波動率
    相對 20 日正在擴張——即訊號觸發於「波動剛開始抬升」而非「平穩
    低波中的單點 pullback」。預期過濾掉 Part A 5 個近零到期（皆發生
    於盤中低波環境），保留 Part A/B 所有 TPs（典型反彈前均有波動
    抬升）。TLT 日波動 1.00% 在 ATR 有效邊界（≤ 2.25%）內，符合
    lesson #15 適用範圍。**Repo 首次 ATR 過濾測試於 TLT**
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT010Config(ExperimentConfig):
    """TLT-010 Capitulation-Confirmed Vol-Regime-Gated MR 參數

    迭代紀錄：
      Att1（two_day_decline_threshold=-0.015，其餘同 TLT-007 Att2）：
        2DD <= -1.5% 作為 capitulation-confirmation 濾波，預期移除
        TLT-007 Att2 Part A 的近零到期訊號（2020-08-12、2020-12-02、
        2023-05-16 等），同時保留 Part B 的急跌反彈訊號
    """

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

    # 2 日累積報酬濾波（Att1 floor/Att2 cap 皆失敗；Att3 停用）
    two_day_decline_lookback: int = 2
    two_day_decline_threshold: float = -0.02
    two_day_decline_as_cap: bool = True
    use_two_day_decline_filter: bool = False  # Att3 停用

    # Att3 新增：ATR 波動率擴張濾波（repo 首次於 TLT 測試）
    use_atr_expansion: bool = True
    atr_fast_period: int = 5
    atr_slow_period: int = 20
    atr_expansion_ratio_min: float = 1.05

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT010Config:
    return TLT010Config(
        name="tlt_010_capitulation_regime_mr",
        experiment_id="TLT-010",
        display_name="TLT Capitulation-Confirmed Vol-Regime MR",
        tickers=["TLT"],
        data_start="2018-01-01",  # 需要 BB(20)/SMA(100) 暖機
        profit_target=0.025,  # +2.5%（同 TLT-007）
        stop_loss=-0.035,  # -3.5%（同 TLT-007）
        holding_days=20,
    )
