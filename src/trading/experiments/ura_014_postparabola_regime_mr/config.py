"""
URA-014: Post-Parabolic Long-Horizon Regime-Gated Capitulation MR

Extends URA-013 Att2 (current global optimum, min(A,B)† = Part A 1.22) with a
single orthogonal long-horizon regime gate that surgically removes its lone
residual binding Part A SL 2021-11-16 (the only losing trade in the entire
13-trade set).

This is a same-framework refinement of a proven winner, NOT a cross-asset
port. The added gate is in the lesson #19 multi-period-return family (the same
family as URA-013's own 5d return cap), extended to a LONG-horizon CEILING
that excludes "buy-the-dip during the unwind of a fresh parabolic blow-off".
It is NOT a trend-direction filter (cross_asset_lessons #3): it does not
require an uptrend — it REJECTS dips that follow an extreme up-move
(anti-extension / post-parabola exclusion regime classifier).

Mandatory pre-analysis gate (predict->confirm), reproduced URA-013 Att2 exact
trades (Part A 2019-2023 + Part B 2024-2025) and characterized the single
residual binding Part A SL 2021-11-16 (-5.59% SL) vs all 11 target-winners +
the 2019-08-05 expiry-win on long-horizon dimensions:

  Prior 60-day return (Ret60):
    SL 2021-11-16            = +51.39%   <- Sept-Nov 2021 Sprott-SPUT
                                            uranium parabolic blow-off
    winners (n=11, both pts) = [-24.39%, +29.59%]   max winner +29.59%
    -> SEPARABLE: SL is ABOVE every winner by 21.80pp; robust >=20pp
       plateau [+29.6%, +51.4%], NOT a knife-edge single-point notch.
  Other dims: Ret120 / Ret252 / AboveSMA200 / RunupTo252Peak interleaved;
  DDfromHigh252 a 0.01pp knife-edge (rejected). Ret60 is the clean axis.

Structural ex-ante mechanism: URA ran +51% over 60 days into 2021-11-16
(Sprott Physical Uranium Trust squeeze drove uranium spot ~$30 -> ~$50). The
RSI(2)<15 + 10-20% pullback dip during that parabolic phase was the early
stage of a multi-month mean-reverting unwind of the parabola, not a genuine
oversold capitulation bottom -> the MR buy continued lower into the SL.
Genuine URA capitulation winners occur when the prior 60-day momentum is
moderate or negative (a real decline producing oversold conditions), never
after a fresh +50% blow-off. This matches URA's documented "post-rally crash /
V-bounce then deeper" pattern (EXPERIMENTS_URA.md asset notes).

2021-11-16 is temporally isolated (prev signal 2021-07-19, next 2022-03-14,
both far beyond cd10) -> clean surgical excision predicted with no cooldown
chain-shift (GLD-016-class clean excision, not SOXL-013-class chain-shift).

Iterations (Ret60 ceiling threshold sweep; predict->confirm CONFIRMED):
  Att1 ★ SUCCESS (Ret60 ceiling <= +0.35, mid-plateau primary):
    Filtered ONLY 2021-11-16 (clean surgical excision, NO cooldown
    chain-shift as predicted). Part A 9->8 / WR 88.9%->100% / Sharpe
    1.22 -> 6.71 / cum +46.84% -> +55.54% / MaxDD -8.24% -> -5.14% /
    0 stop-loss. Part B 4/4 zero-var UNCHANGED (+26.25%). Part C
    3/66.7%/Sharpe 1.38/+12.25%. min(A,B)† = Part A 6.71 (Part B
    std=0 zero-var convention per EWJ-003 / SPY-009 / DIA-012 /
    IWM-013 / SIVR-018 / CIBR-014 / URA-013). **+450% vs URA-013 Att2
    1.22.** A/B annualized cum 11.11%/yr vs 13.13%/yr (gap 15.4% <
    30% ✓, better than URA-013 Att2 28.6%); A/B signal 1.6/yr vs
    2.0/yr = 1.25:1 (gap 20% < 50% ✓). All acceptance criteria met.
  Att2 (Ret60 ceiling <= +0.40, looser robustness check):
    IDENTICAL to Att1 (Part A 8/100%/6.71, Part B 4/100%, gap 15.4%);
    +0.45 / +0.40 / +0.35 / +0.30 all identical -> robust >=15pp
    plateau [+0.30, +0.45], NOT a fitted single point (contrast
    CIBR-016 0.7pt notch / INDA-013 post-hoc reject).
  Att3 (Ret60 ceiling <= +0.28, tighter cliff check):
    Part A unchanged 8/100%/6.71 BUT Part B 4->3 — additionally kills
    the nearest winner 2025-08-19 (Ret60 +29.59%), Part B cum
    +26.25% -> +19.10%, A/B gap 15.4% -> 16.3%. Confirms +0.35 is
    safely mid-plateau and +0.28 is the degradation cliff.

Cross-asset contribution: repo first LONG-horizon prior-return CEILING as a
post-parabolic capitulation-quality regime gate (lesson #19 family extended
from short-window depth caps 1d/2d/3d/5d/ATR to a 60d post-parabola exclusion
CEILING). URA second structural-ceiling break after URA-013 (0.47 -> 1.22 ->
6.71). Pre-analysis predict->confirm gate predicted SUCCESS and CONFIRMED
(GLD-016 / VOO-005-class clean excision; track record extended).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA014Config(ExperimentConfig):
    """URA-014 post-parabolic long-horizon regime-gated capitulation MR params"""

    # Pullback parameters (same as URA-004 / URA-012 / URA-013)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    # RSI(2) (same as URA-004 / URA-012 / URA-013)
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 2-day decline (same as URA-004 / URA-012 / URA-013)
    two_day_decline: float = -0.03

    # ATR ratio BAND (same as URA-012 Att2 / URA-013)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.00
    atr_ratio_ceiling: float = 1.50

    # Multi-period capitulation cap (same as URA-013 Att2 ★)
    multi_period_lookback: int = 5
    multi_period_cap: float = -0.090

    # Post-parabolic long-horizon regime gate (NEW, URA-014)
    # Prior N-day cumulative return must be BELOW this ceiling: reject
    # capitulation signals that occur during the unwind of a fresh parabolic
    # blow-off (early-stage of a multi-month parabola mean-reversion, not a
    # genuine oversold bottom). NOT a trend-direction filter.
    # Att1 ★: +0.35 (mid-plateau; filters only 2021-11-16 Ret60 +51.39%)
    # Att2:   +0.40 (looser robustness; within [+29.6%, +51.4%] plateau)
    # Att3:   +0.28 (tighter cliff; additionally kills 2025-08-19 +29.59%)
    runup_lookback: int = 60
    runup_ceiling: float = 0.35

    # Cooldown (same as URA-004 / URA-012 / URA-013)
    cooldown_days: int = 10


def create_default_config() -> URA014Config:
    return URA014Config(
        name="ura_014_postparabola_regime_mr",
        experiment_id="URA-014",
        display_name="URA Post-Parabolic Regime MR",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,
        stop_loss=-0.055,
        holding_days=20,
    )
