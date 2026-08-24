"""
TSM-012: Volume-Confirmed RS Momentum Pullback 配置
TSM Volume-Confirmed Relative Strength Momentum Pullback Configuration

策略方向：在 TSM-008 RS 動量回調框架上加入 signal-day volume ratio 過濾，
測試「成交量信號」作為 RS momentum pullback 訊號的補充維度。

研究動機：TSM-011 Att3 透過 5d return CEILING（rally exhaustion filter）
將 min(A,B) 從 0.79 提升至 0.83。本實驗測試 volume 維度是否提供
額外正交過濾（與 price-based ceiling 結構性正交）。

跨資產證據（lesson #6 邊界 + 反例 8 SIVR-017 結論）：
- volume-based filters（URA-011 Volume spike、SIVR-017 MFI 等）作為主訊號
  在 active MR regime 通常 supplementary 而非 substitutive：
  創造 A/B 對稱性但不突破品質天花板。
- 在 RS momentum 框架（非 MR）上 volume 維度尚未驗證，TSM-012 為首次嘗試。

兩種對立假設（across iterations 測試）：
- H1（capitulation buy）：訊號日 volume / 20日均量 >= K
  高量回調 = 機構集中拋售完成 = MR 進場品質高
- H2（orderly continuation）：訊號日 volume / 20日均量 <= K
  低量回調 = 健康 profit-taking = 趨勢延續品質高

進場條件（沿用 TSM-008，所有條件需同時滿足 + 新增 volume 維度）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. **新增 訊號日 Volume / SMA(Volume, 20) 在 [vol_ratio_min, vol_ratio_max] 區間**
5. 冷卻期 10 個交易日

三次迭代結果（全部 FAILED vs TSM-011 Att3 baseline min(A,B)=0.83）：
- Att1（vol_ratio_min >= 1.30，H1 capitulation buy）：FAILED
  Part A 5 訊號 / WR 80% / Sharpe **1.56** / cum +33.71% / 0 SLs
  Part B 4 訊號 / WR 75% / Sharpe **0.65** / cum +17.04% / 1 SL（2024-07-08）
  min(A,B) **0.65** (-22% vs TSM-011 Att3 0.83)
  分析：vol >= 1.30 過於嚴苛（12→5、10→4，-58%/-60% 訊號率），保留之 Part A
  訊號品質極佳（4/5 TP）但 Part B 2024-07-08 SL 仍存活於高 vol 過濾下，
  顯示「高 vol 確認」不能可靠區分 SL（2024 期間 SL 同時 vol 高）。

- Att2（vol_ratio_max <= 1.20，H2 orderly continuation）：FAILED
  Part A 9 訊號 / WR 66.7% / Sharpe **0.54** / cum +33.94% / 2 SLs
  Part B 7 訊號 / WR 71.4% / Sharpe **0.54** / cum +26.84% / 2 SLs
  min(A,B) **0.54** (-35% vs TSM-011 Att3 0.83)
  分析：低 vol 過濾保留更多訊號但品質下降——orderly continuation 假設失敗，
  低 vol 包含「無動量參與」的弱訊號。Part A 兩個原本被 TSM-008 baseline
  排除的低品質訊號（2022-11-21、2022-12-07）同時通過 vol <= 1.20 與 5d ceiling 缺失
  的雙重缺口，皆停損。

- Att3（vol_ratio_min >= 1.10，moderate floor）：FAILED
  Part A 6 訊號 / WR **83.3%** / Sharpe **1.76** / cum **+44.41%** / 0 SLs
  Part B 4 訊號 / WR 75% / Sharpe **0.65** / cum +17.04% / 1 SL（同 Att1）
  min(A,B) **0.65** (-22% vs TSM-011 Att3 0.83)
  A/B 累計差 **62%**（>> 30% 目標），A/B Sharpe 差 1.11（嚴重失衡）
  分析：放寬至 1.10 增加 1 個 Part A 訊號（2021-01-26 TP）但 Part B 完全相同
  （2024-07-08 SL 仍存活），結構性 A/B 失衡——Part A 高 vol 訊號天然密集於
  2020-2023 高波動期，Part B 2024-2025 較低波動期 vol 整體偏低，floor filter
  系統性傾向 Part A。

核心發現（cross-asset lesson 擴展）：
1. **TSM-012 三次迭代全部失敗**，volume 維度在 RS momentum pullback 框架不有效。
2. **Volume filter 在不同框架的失敗模式**：URA-011（MR 框架）失敗於「無法
   區分真假 capitulation」，SIVR-017（MFI MR 框架）失敗於「volume-weighted
   oscillator 早期 panic 而非尾聲」，TSM-012（RS momentum 框架）失敗於
   「H1 高 vol 確認 SL/TP 均存活、H2 低 vol 引入弱訊號」。
3. **新跨資產規則候選**：volume-based filters 作為 supplementary 而非 substitutive
   維度規則擴展至 RS momentum 框架（lesson #6 邊界擴展第三次：URA-011 MR、
   SIVR-017 MFI MR、TSM-012 RS momentum 三類框架皆驗證）。
4. **A/B 結構性偏差**：高波動期（2020-2023）vol >= K filter 通過率高於低波動期
   （2024-2025），導致 floor 過濾結構性 A/B 失衡。Volume filter 在多 regime 期間
   需考慮 vol normalization（rolling z-score 而非 ratio）以避免此偏差。

結論：TSM-008 / TSM-011 RS momentum 框架對 volume 過濾無響應。
TSM-011 Att3 仍為全域最優。**Volume 維度從 TSM 已驗證無效方向中剔除**。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMVolumeConfirmedConfig(ExperimentConfig):
    """TSM Volume-Confirmed RS Momentum Pullback 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # Volume ratio = signal-day Volume / SMA(Volume, volume_avg_window)
    volume_avg_window: int = 20
    # vol_ratio 下限（>=）：>= 0 視為停用（H1 capitulation buy hypothesis）
    vol_ratio_min: float = 0.0
    # vol_ratio 上限（<=）：>= 999 視為停用（H2 orderly continuation hypothesis）
    vol_ratio_max: float = 999.0


def create_default_config() -> TSMVolumeConfirmedConfig:
    return TSMVolumeConfirmedConfig(
        name="tsm_012_volume_confirmed_rs_pullback",
        experiment_id="TSM-012",
        display_name="TSM Volume-Confirmed RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
        # Att3 final（FAILED but highest WR Part A）：vol_ratio_min=1.10
        vol_ratio_min=1.10,
        vol_ratio_max=999.0,
    )
