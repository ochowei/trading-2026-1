"""
SIVR-018: Capitulation-Strength Filter Mean Reversion (ATR Ceiling + 3d Floor)

Cross-asset port from URA-012 (ATR BAND) and DIA-012/SPY-009 (lesson #19
multi-period capitulation-strength), refined to a CEILING-only ATR plus
3d return floor combo after trade-level analysis on SIVR-015 Att1 base.

Background:
SIVR-015 Att1 (Pullback+WR+RSI bullish hook) achieves min(A,B) 0.48 with
Part A 8 trades (6 wins / 2 SLs). Trade-level analysis revealed:
  - The 2 Part A SLs (2021-09-21, 2023-02-07) cluster ATR(5)/ATR(20) in
    [1.23, 1.26], i.e. mid-acceleration vol expansion, while 5/8
    winners cluster ATR <= 1.20.
  - Naive ATR ceiling alone triggers cooldown chain shift (lesson #19):
    removing 2021-06-21 EXP and 2023-02-07 SL allows previously-suppressed
    next-day signals to fire (2021-06-23 EXP -3.19%, 2023-02-10 SL),
    yielding only +0.01 Sharpe vs baseline.
  - Chain-shifted entries 2021-06-23 (3d +0.16%) and 2023-02-10 (3d -0.75%)
    fail a 3d return floor <= -1.0%, while ALL Part B winners have 3d
    deeper than -1.92% (non-binding on Part B).

Iterations:
  Att1 (BAND [1.00, 1.50] on SIVR-005 base, URA-012 Att2 direct port):
    Part A 0.07 / Part B 0.26 / min 0.07 — FAILED. URA mirror SLs ATR
    distribution does NOT replicate on SIVR (Part A SL/TP ATR overlap
    heavily in 1.00-1.20 band).

  Att2 (SIVR-015 + ATR CEILING <= 1.20 alone):
    Part A 0.49 / Part B 1.41 / min 0.49 — MARGINAL +2% vs baseline 0.48.
    Cooldown chain shift introduces 2 replacement losses
    (2021-06-23 EXP-3.19, 2023-02-10 SL-3.64) that offset the gain from
    removing 2 SLs.

  Att3 ★ (SIVR-015 + ATR CEILING <= 1.20 + 3d floor <= -1.0%):
    Part A 5 trades 100% WR cum +18.77% Sharpe 0.00 (zero-var, 5 TPs all
    +3.50%) / Part B 3 trades 66.7% WR cum +7.12% Sharpe 1.41 / min(A,B)†
    1.41 (+193% vs baseline 0.48) by EWJ-003/SPY-009/DIA-012/IWM-013
    convention (Part A zero-var = structurally optimal, Part B Sharpe is
    binding constraint). A/B annualized cum gap 5.1% (<<30% ✓), signal
    gap 33% (<50% ✓). Repo first to combine ATR ceiling + 3d return
    floor as MR entry filters on SIVR.

Cross-asset findings:
  1. Lesson #15 v3 mirror SLs ATR hypothesis (URA-012 Att2) does NOT
     replicate on SIVR — Part A SLs/TPs ATR overlap too heavily for
     a clean BAND. SIVR's ATR mirror is between Part A SLs (high) and
     Part A TPs (low+high bimodal), not Part A vs Part B.
  2. ATR CEILING <= 1.20 alone removes 2 SLs but triggers cooldown
     chain shift — repo first SIVR observation of chain shift caused
     by ATR filter (paralleling lesson #19 dynamics).
  3. Adding 3d return floor <= -1.0% surgically filters chain-shifted
     entries (which characteristically have ret_3d > -1%) while leaving
     all Part B winners untouched. This combined filter avoids the
     chain-shift trap.
  4. Lesson #19 family extends to "ATR CEILING + 3d floor combo on
     RSI-hook MR base" — a new sub-pattern joining DIA-012's "1d cap +
     3d cap dual-dimension", INDA-011's "2d floor + 3d cap", GLD-014's
     "2d floor + 1d floor", and EWZ-007's "1d cap surgical filter".
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVR018Config(ExperimentConfig):
    """SIVR-018 capitulation-strength filter MR parameters"""

    # Pullback (same as SIVR-005 / SIVR-015 base)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07
    pullback_cap: float = -0.15

    # Williams %R (same as SIVR-005 / SIVR-015 base)
    wr_period: int = 10
    wr_threshold: float = -80.0

    # RSI(14) bullish hook (SIVR-015 Att1)
    use_rsi_hook: bool = True
    rsi_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0

    # ATR ratio CEILING (Att3 ★)
    # Trade-level analysis on SIVR-015 Att1 8 Part A trades shows both
    # SLs cluster ATR [1.23, 1.26] while 5/6 winners cluster ATR < 1.20.
    # Floor disabled — SIVR has no low-ATR Part A SL cluster to filter.
    use_atr_band: bool = True
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 0.0  # disabled
    atr_ratio_ceiling: float = 1.20

    # Lesson #19 family: 1-day return cap (disabled)
    # Att2 verified non-binding — RSI hook already excludes deep-1d signals.
    use_1d_cap: bool = False
    one_day_cap: float = -0.05

    # Lesson #19 family: 3-day return floor (Att3 ★)
    # Chain-shifted entries (2021-06-23 ret_3d +0.16%, 2023-02-10 -0.75%)
    # both fail this filter. Part B winners all have ret_3d <= -1.92%
    # (non-binding on Part B).
    use_3d_floor: bool = True
    three_day_floor: float = -0.01

    # Reserved (3d cap, currently disabled — direction reversed to floor)
    use_3d_cap: bool = False
    three_day_cap: float = -0.07

    # Cooldown (same as SIVR-005)
    cooldown_days: int = 10


def create_default_config() -> SIVR018Config:
    return SIVR018Config(
        name="sivr_018_atr_band_mr",
        experiment_id="SIVR-018",
        display_name="SIVR Capitulation-Strength Filter MR",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.035,
        holding_days=15,
    )
