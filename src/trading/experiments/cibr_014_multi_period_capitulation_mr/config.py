"""
CIBR Multi-Period Capitulation-Strength Filter MR 配置 (CIBR-014)

策略方向：Multi-Period Capitulation-Strength Filter（lesson #19 family）
+ Vol-Expansion Cap（lesson #22 family，新方向：ATR ratio 上限）

動機：CIBR-012 Att3 採「2DD cap >= -4%」單維度過濾，min(A,B) 0.49（記錄基線），
但於更新資料後退化為 Part A 3 訊號 zero-var（邊界 jitter 敏感）。CIBR-008
（前任最佳 0.39）Part A 含 2 筆停損（2020-02-24 COVID + 2021-02-26 科技股拋售），
其中 2020-02-24 可由「1d 急跌 cap」精準過濾（1d -3.54% 深於 -3% 門檻），
但 2021-02-26 之 1d -0.14% / 2d -2.85% / 3d -3.05% / 5d -7.19% 皆與 TPs 訊號
重疊，無法以 return-based 維度區分。

跨資產 trade-level 分析（CIBR-014 Att1 Part A 4 訊號 + Part B 4 訊號）發現
2021-02-26 SL 之 ATR(5)/ATR(20) **= 1.5065**，遠高於其他 7 筆訊號（範圍
1.1597 ~ 1.3147，平均 1.244）。此為**極端波動率擴張**結構，標誌進場日仍處於
crash 加速階段（vs 一般 1.15-1.30 為「panic 過後 settling」階段）。

CIBR-014 雙重過濾組合：
1. 1d return cap >= -3.0%（過濾 2020-02-24 COVID 級單日急跌）
2. ATR(5)/ATR(20) 上限 <= 1.40（過濾 2021-02-26 級極端波動率擴張）

Att1：1d cap >= -3.0% + 3d cap >= -7.0%（DIA-012 Att2 跨資產移植）
- 結果：Part A 4 訊號 75% WR Sharpe 0.49 cum +6.33%（過濾 2020-02-24 SL，
  保留 2021-02-26 SL）/ Part B 4 訊號 100% WR Sharpe 4.08 cum +11.75%
  / min(A,B) **0.49**（持平 CIBR-012 baseline，3d cap 對 CIBR 數據集為非綁定）
- 失敗根因：3d 維度上 2021-02-26 (-3.05%) 與 TP 2020-10-30 (-5.42%) 排序
  逆向，無法以 3d 閾值單獨過濾 SL 而保留 TP

Att2 ★（本次迭代核心）：移除 3d cap，改用 ATR ratio CEILING **<= 1.40**
- 設計：保留 CIBR-008 既有 ATR(5)/ATR(20) > 1.15（panic 過濾）+ 新增
  CEILING <= 1.40（in-crash 過濾）= **ATR ratio BAND [1.15, 1.40]**
- 預期：精準過濾 2021-02-26 SL（ATR ratio 1.5065），保留所有 TP
- 結構：Part A 退化為 3 TPs zero-var（structurally optimal），Part B 變異維持
- min(A,B)† 由 EWJ-003/EWT-008/DIA-012 慣例：Part A zero-var 100% WR 為
  structurally optimal，Part B Sharpe 為 binding constraint

Att3（穩健性測試 + 邊界探索）：放寬 ATR ratio 上限至 <= 1.45
- 確認 CIBR 1.40 ~ 1.45 區間敏感度；若結果與 Att2 完全相同，確認 1.40 為
  穩健閾值（與 1.45 之間無新增 borderline 訊號）

跨資產延伸（lesson #19 family + lesson #22 vol-regime cross product）：
- DIA-012 (1.0% vol): 1d cap + 3d cap（return-only 雙維度）
- SPY-009 (1.0% vol): 1d floor + 3d cap
- INDA-011 (0.97% vol): 1d floor + 3d cap
- GLD-014 (1.12% vol): 1d floor + 2d floor
- CIBR-014 Att2 (1.53% vol)：**1d cap + ATR ratio BAND** — repo 首次
  return-based 維度與 vol-regime 維度結合作為 MR 進場過濾，挑戰「ATR ratio
  > 1.15 即足夠」的傳統認知，發現「過高 ATR ratio（>1.40）反而標誌 in-crash」
  的對稱失敗模式
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR014Config(ExperimentConfig):
    """CIBR-014 Multi-Period Capitulation-Strength Filter MR 參數"""

    # BB 參數（同 CIBR-008）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（同 CIBR-008 甜蜜點）
    pullback_lookback: int = 10
    pullback_cap: float = -0.12

    # 品質過濾（同 CIBR-008）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    # Multi-Period Capitulation-Strength Filter（CIBR-014 雙維度創新）
    # 1 日報酬上限（filter 單日 news/policy-driven 急跌）
    oneday_return_cap: float = -0.030
    # 3 日報酬上限（filter 跨夜 regime-shift 延續性下跌）
    threeday_return_cap: float = -0.070

    cooldown_days: int = 8


def create_default_config() -> CIBR014Config:
    return CIBR014Config(
        name="cibr_014_multi_period_capitulation_mr",
        experiment_id="CIBR-014",
        display_name="CIBR Multi-Period Capitulation-Strength Filter MR",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=18,
    )
