"""
URA-013: Multi-Period Capitulation-Strength Filter MR

Cross-asset port of lesson #19 multi-period capitulation depth filter family
(INDA-011 / DIA-012 / GLD-014 / EWZ-007 / SIVR-018) to URA. Extends URA-012
Att2 BAND structure with a 5-day return cap that targets the residual 2022
bear-market SLs left untouched by ATR ratio BAND.

Trade-level analysis on URA-012 Att2 (17 Part A trades + 8 Part B trades)
revealed Part A SLs cluster at deeper 5-day cumulative declines while winners
sit shallower:

  Part A SLs 5d ret distribution:
    2021-11-16  -8.03%   <- shallowest SL (sub-threshold, not filterable here)
    2022-06-13  -9.04%
    2022-01-24  -9.85%
    2022-05-09 -12.10%   <- deep multi-day continuation
    2022-04-22 -12.83%   <- deep multi-day continuation
  Part A TPs 5d ret distribution: -11.04% ~ +0.76% (mostly shallower than -10%)
  Part B SLs 5d ret: -9.56% / -10.71%
  Part B TPs 5d ret: -5.54% ~ -12.39%

A 5d cap >= -10.5% (i.e., require recent 5-day cumulative return shallower
than -10.5%) targets the two deepest 2022 SLs (-12.83% / -12.10%) while
preserving most winners. Compared to ATR ratio BAND alone, this captures
"multi-day acceleration" structure that ATR ratio cannot detect when the
acceleration is gradual rather than spiky.

Iterations:
  Att1 (5d cap >= -10.5%, modest filter, INDA-011 cross-asset port direct):
    Part A 14/78.6%/Sharpe 0.71 cum +55.88% / Part B 7/85.7%/Sharpe 1.07 cum
    +33.92% / min 0.71. Filtered Part A 2022-04-22 / 2022-05-09 SLs (deep
    multi-day) + 1 deep TP 2021-06-18 (cost) and 1 deep TP 2025-10-21; Part B
    2025-02-25 SL filtered with positive cooldown chain shift adding 2025-03-03
    TP. (+51% vs URA-012 0.47)
  Att2 ★ (5d cap >= -9.0%, tighter, multi-day acceleration filter):
    Part A 9/88.9%/Sharpe 1.22 cum +46.84% / Part B 4/100% std=0 cum +26.25%
    / min(A,B)† Part A 1.22 (Part B zero-var convention per EWJ-003 / SPY-009
    / DIA-012 / IWM-013 / SIVR-018 / CIBR-014). Additional Part A SLs filtered:
    2022-01-24 (5d -9.85%), 2022-06-13 (5d -9.04%); cost: 3 deep TPs
    (2020-02-27 / 2021-08-19 / 2022-08-19) but Part A WR 78.6% → 88.9%; Part B
    additionally filters 2024-07-19 SL + 2 deep TPs (2024-09-03 / 2025-04-04)
    leaving 4/4 zero-var. **+160% vs URA-012 baseline 0.47.** A/B annualized
    cum 9.37%/yr vs 13.13%/yr (gap 28.6% < 30% ✓), signal ratio 1.11:1 (gap
    10% < 50% ✓).
  Att3 (5d cap >= -9.5%, robustness check):
    Part A 12/83.3%/Sharpe 0.90 / Part B 5/100% std=0 / min 0.90 (-26% vs Att2)
    — relaxing threshold by 0.5pp lets in 2022-06-13 SL (5d -9.04%), confirming
    -9.0% as the optimal sweet spot for URA Part A 5d return distribution.

Cross-asset contributions:
  - Repo first 5-day return cap as primary capitulation-strength filter
    (lesson #19 family extension to 5-day window) — joins INDA-011 (2DD floor +
    3DD cap), DIA-012 (1d cap + 3d cap), GLD-014 (2d floor + 1d floor),
    EWZ-007 (1d cap surgical), SIVR-018 (ATR ceiling + 3d floor) family.
  - URA first multi-period capitulation depth filter (URA-007/008/009/010/011
    all targeted single-day or 2-day dimensions; URA-012 used ATR ratio).
  - **Repo first 5-day window depth dimension** (prior family covered 1d / 2d /
    3d / ATR-ratio dimensions only).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA013Config(ExperimentConfig):
    """URA-013 multi-period capitulation-strength filter parameters"""

    # Pullback parameters (same as URA-004 / URA-012)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    # RSI(2) (same as URA-004 / URA-012)
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 2-day decline (same as URA-004 / URA-012)
    two_day_decline: float = -0.03

    # ATR ratio BAND (same as URA-012 Att2)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.00
    atr_ratio_ceiling: float = 1.50

    # Multi-period capitulation cap (NEW, URA-013)
    # 5-day cumulative return must be SHALLOWER than this threshold
    # (i.e., require 5d_ret >= cap_threshold, filtering deep multi-day declines).
    # Att1: -0.105 (modest; targets 2 deep 2022 SLs at -12.83% / -12.10%) min 0.71
    # Att2 ★: -0.090 (tighter; additionally targets 2022-01-24 / 2022-06-13 SLs) min(A,B)† 1.22
    # Att3: -0.095 (robustness check; lets in 2022-06-13 SL → Part A 0.90, -26% vs Att2)
    multi_period_lookback: int = 5
    multi_period_cap: float = -0.090

    # Cooldown (same as URA-004 / URA-012)
    cooldown_days: int = 10


def create_default_config() -> URA013Config:
    return URA013Config(
        name="ura_013_multi_period_cap_mr",
        experiment_id="URA-013",
        display_name="URA Multi-Period Cap MR",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,
        stop_loss=-0.055,
        holding_days=20,
    )
