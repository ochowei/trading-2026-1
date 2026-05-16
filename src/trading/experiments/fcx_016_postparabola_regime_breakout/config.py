"""
FCX-016: Post-Parabolic Long-Horizon Regime-Gated VIX-FLOOR BB Squeeze Breakout

策略方向（Strategy Direction）：
    在 FCX-015 Att2（VIX>14 FLOOR on Multi-Period Direction-Filter Regime BB
    Squeeze Breakout，當前 FCX 全域最優 min(A,B)† = Part A Sharpe **1.43**）
    基礎上，**跨資產移植 URA-014 Att1 ★ SUCCESS 的「post-parabolic 長窗
    prior-Nd-return CEILING」regime gate**（lesson #19 family v3，long-horizon
    後拋物線排除），目標外科式移除其唯一殘餘 binding Part A SL 2021-11-11。

    這是 **URA-014 winning-playbook 的跨資產移植測試**（NOT same-framework
    refinement）：URA-014 在 URA（uranium，Sprott-SPUT 2021 擠壓）以「prior
    60d cumulative return CEILING」外科移除其唯一 post-parabolic blow-off
    SL（Ret60 +51.39%，高於全部 winners 21.80pp，>=20pp robust plateau），
    Sharpe 1.22→6.71。memory/URA-014 明列 **FCX / COPX / SOXL / SIVR** 為
    候選跨資產移植標的——「但僅當 binding residual SL 的 prior-Nd-return
    為相對 winners 的 separable plateau outlier（須先以 predict→confirm
    驗證；若 interleaved → documented-failure）」。

================================================================================
強制 predict→confirm 前置分析（pre-analysis gate，DECISIVE）
================================================================================
重現 FCX-015 Att2 的精確交易（Part A 2019-2023 10 筆 / WR 90% / 1 SL；
Part B 2024-2025 3 筆 / WR 100%）。唯一殘餘 binding Part A SL = **2021-11-11**
（-7.14% SL，10 筆 Part A 中唯一輸家，single characterizable residual SL）。

對 9 個 Part A winners 計算 signal-day prior-Nd cumulative return（FCX 自身
Close.pct_change(N)），檢驗 SL 是否為 separable post-parabolic outlier：

  prior-Nd cumulative return（SL 2021-11-11 vs 9 winners 區間 / 排序位置）
    Ret20 : SL +10.15% | winners [+3.8%, +19.4%] | SL 低於 max 9.25pp，
            mid-pack（5 低 / 4 高）→ INTERLEAVED
    Ret30 : SL +25.99% | winners [+2.4%, +43.3%] | SL 低於 max 17.26pp
            → INTERLEAVED
    Ret60 : SL +20.97% | winners [+3.4%, +62.6%] | **SL 低於 max winner
            41.59pp；9 winners 有 7 個 Ret60 高於 SL** → 方向 INVERTED，
            SL 並非 post-parabolic blow-off outlier（URA-014 之 SL 為
            全場 Ret60 最高 +51.39%，FCX 之 SL 反而偏低）
    Ret90 : SL +13.43% | winners [-18.5%, +125.3%] | 第 3 低 → INTERLEAVED
    Ret120: SL  -1.20% | winners [-19.1%, +126.4%] | mid-low → INTERLEAVED
    Ret252: SL +110.77%| winners [-0.3%, +361.5%]  | mid-pack → INTERLEAVED

  **每一條 prior-Nd-return 窗（20/30/60/90/120/252）SL 均與 winners
  完全 INTERLEAVED；無任何 separable plateau。** 在 URA-014 的關鍵維度
  Ret60，FCX 的 SL 為結構性 INVERSE：URA 之 SL 為單一最高（fresh
  parabolic blow-off），FCX 之 SL 反為 mid/low，而 FCX 的最大 prior-60d
  run-ups（+55%~+63%）全部是 winners（2020 COVID V-recovery breakouts）。

  結構性 ex-ante 機制：FCX/銅於 2021-05 已見頂（~$46），至 2021-10/11
  為盤整/下行；2021-11-11 的 prior-60d +20.97% 是對 2021-08/09 回檔的
  recovery bounce，**並非新鮮拋物線 blow-off**。FCX 的拋物線階段是
  2020 COVID V-recovery，而那些 breakout 全部獲利。對突破策略而言，
  「高 prior-Nd run-up」是 productive regime（動能延續），與 URA
  MR 框架「高 prior-Nd run-up = 抄底拋物線崩解陷阱」結構性相反。

  **predict→confirm 結論：DOCUMENTED-FAILURE（方向 INVERTED）。**
  Ret60 CEILING 要移除 SL（+20.97%）必須 ceiling <= +0.21，將同時殺死
  6 個高 Ret60 winners（+30.5/+40.8/+45.7/+55.6/+58.8/+62.6）→ Part A
  災難性 attrition；ceiling 放寬至 > +0.21 則 SL 通過不被過濾、僅誤殺
  高動能 winners（SIVR-019 / DIA-013-class 方向倒置）。無 separable
  plateau，與 URA-014 的 >=20pp robust plateau 形成對照。

================================================================================
迭代設計（Ret60 ceiling 掃描；predict→confirm 預測 documented-failure）
================================================================================
- Att1（runup_ceiling = +0.21，mid — 剛好低於 SL Ret60 +20.97% 的最緊值）：
  預測移除 SL 但同時殺死 6 個高 Ret60 winners → Part A 災難性 attrition，
  min(A,B) 大幅低於 1.43，方向 INVERTED。
- Att2（runup_ceiling = +0.45，looser robustness）：
  預測 SL Ret60 +20.97% <= +0.45 通過不被過濾（gate 對 SL non-binding），
  僅誤殺最大的 3 個 COVID-recovery winners → SL 保留、winners 流失，
  min(A,B) 退化，確認方向倒置非單點。
- Att3（runup_ceiling = +0.15，tighter cliff）：
  預測更深 attrition（移除 SL + 更多 winners），確認單調退化、無 plateau。

================================================================================
基準對照（FCX-015 Att2 ★ 2026-05-07，FCX 全域最優）
================================================================================
- Part A: 10 訊號, WR 90.0%, 累計 +85.63%, Sharpe **1.43**, MDD -7.47%
- Part B:  3 訊號, WR 100%, 累計 +25.97%, std=0, Sharpe 0.00
- min(A,B)† = Part A Sharpe **1.43**（Part B std=0 零方差慣例）
- A/B 年化 cum 13.18%/yr vs 12.24%/yr → gap 7.1% << 30% ✓
- A/B 訊號比 2.0/yr vs 1.5/yr → 1.33:1 (gap 25% < 50% ✓)

驗收目標：min(A,B) > 1.43 且 A/B gap 維持達標。
**predict→confirm 預測：三次迭代均 FAIL/REJECT（documented-failure），
記錄 lesson #19 family v3 long-horizon prior-return CEILING 不可移植至
copper-supercycle commodity miner 之新跨資產規則。**
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX016Config(ExperimentConfig):
    """FCX-016 post-parabolic long-horizon regime-gated VIX-FLOOR breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 FCX-015 Att2 / FCX-014）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime（lesson #22，同 FCX-015 Att2）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === 訊號日方向過濾（lesson #19 family，同 FCX-015 Att2）===
    max_signal_day_3d_return: float | None = 0.12

    # === ^VIX FLOOR regime gate（同 FCX-015 Att2 ★，lesson #24 family）===
    vix_ticker: str = "^VIX"
    vix_filter_mode: str = "floor"
    vix_low_threshold: float = 14.0
    vix_high_threshold: float = 22.0

    # === Post-parabolic 長窗 prior-return CEILING（FCX-016 核心新增，
    #     跨資產移植 URA-014 Att1 lesson #19 family v3）===
    # 訊號日 prior runup_lookback 日 cumulative return 須 <= runup_ceiling，
    # 排除「於新鮮拋物線 blow-off 解除過程中買進突破」。NOT 趨勢方向過濾。
    # predict→confirm 預測：FCX 之 SL 2021-11-11 Ret60 +20.97% 與 winners
    # 完全 interleaved（winners 高至 +62.56%），方向 INVERTED → documented-failure。
    # Att1: +0.21（mid，剛低於 SL +20.97%，最緊）
    # Att2: +0.45（looser，SL 通過不被過濾）
    # Att3: +0.15（tighter cliff）
    runup_lookback: int = 60
    runup_ceiling: float = 0.21


def create_default_config() -> FCX016Config:
    """建立預設配置（Att1：runup_ceiling +0.21）"""
    return FCX016Config(
        name="fcx_016_postparabola_regime_breakout",
        experiment_id="FCX-016",
        display_name="FCX Post-Parabolic Regime Breakout",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
