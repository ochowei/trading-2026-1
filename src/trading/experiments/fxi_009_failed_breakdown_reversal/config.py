"""
FXI-009: Failed Breakdown Reversal (Turtle Soup Variant)

New strategy direction absent from repo: capture the "liquidity vacuum" that
follows a failed breakdown below the prior N-day low. FXI is policy-driven
and frequently exhibits sharp reversals after forced-selling flushes
(stimulus announcements, ADR tax news, stop-loss cascades on Hang Seng).

Logic:
1. On day T-1 (the flush day): Low_{T-1} < rolling 10-day min Low measured
   over days [T-11, T-2]. I.e., T-1 prints a new 10-day low.
2. On day T (the reclaim day): Close_T > that same 10-day min Low level
   (price has reclaimed the broken support) AND Close_T > Open_T (intraday
   accumulation / bullish bar).
3. WR(10) at day T <= -80 (still extreme oversold; avoid post-rally triggers)
4. 20-day high pullback at T is in [-12%, -3%] (depth/cap gate — reuse
   FXI-005's -12% crash isolation; -3% floor avoids trivial pullbacks near
   highs that are NOT real flushes)
5. Signal fires on day T; enter next-day open (execution model).
6. Cooldown 10 days.

Why this may work on FXI specifically:
- FXI suffers frequent news-driven gap-downs that break short-term support
  then reverse when the tape stabilises. Classic Connors "Turtle Soup" setup.
- Unlike pullback-depth entries, failed breakdown captures the *structure
  break + reclaim*, which tends to resolve directionally either way within
  a few days — reducing the Part A "continued grind down" losers that plague
  FXI-005 in 2019-2023.
- Part B (2024-2025 stimulus era) frequently has sharp V-bottoms (2024-01,
  2024-02, 2025-01) — exactly the failed-breakdown pattern. Should improve
  Part B signal density without hurting quality.

Att1: breakdown_lookback=10, 20d pullback floor -3%/cap -12%, WR(10)<=-80,
      bullish bar, TP+5.5%/SL-5%/20d/cd10.
      RESULT: Part A 8 sig 62.5% WR +6.27% Sharpe 0.18; Part B 1 sig 0% WR
      -5.10% Sharpe 0.00. min(A,B) 0.00. Too restrictive — 10-day breakdown
      is rare, Part B only caught the 2025-04-01 pre-tariff trade (stopped
      out). The -3% pullback floor also excludes shallow dips that could be
      genuine flushes in stimulus-rally periods.

Att2: breakdown_lookback=5, drop pullback floor, add ClosePos>=40%.
      RESULT: Part A 7 sig 42.9% WR -4.76% Sharpe -0.11; Part B 1 sig 0%
      WR -5.10% Sharpe 0.00. min(A,B) -0.11 (WORSE vs Att1). The shorter
      5-day breakdown pattern is too common in choppy markets and produces
      low-quality signals. ClosePos doesn't help because FXI's high
      volatility means many genuine reclaim days don't close near highs.

Att3: restore breakdown_lookback=10, require breakdown_depth_pct=0.01
      (Low_{T-1} at least 1% below prior 10-day min). Keep ClosePos,
      bullish bar, WR, cap.
      RESULT: Part A 0 signals; Part B 1 sig 0% WR -5.10% Sharpe 0.00.
      min(A,B) 0.00 (Part A dried up). 1% real-break depth is too strict
      — FXI's 10-day lows are usually only fractionally undercut before
      the reclaim. Signal count collapsed; no usable data.

Final conclusion: all three iterations fail to beat FXI-005 (0.38).
Failed-breakdown reversal does NOT work on FXI. Root cause: FXI's
policy/event-driven selling tends to extend beyond the initial flush
rather than V-reverse. Signals that "reclaim" the prior low often are
caught in multi-day cascades (2021-11, 2022-09, 2023-02, 2025-04 all
stopped out). This is the same structural issue that makes BB Squeeze
breakout (FXI-003) and BB Lower MR (FXI-006) fail on FXI: policy-driven
EM markets lack reliable intra-week reversal patterns.

Extends cross_asset_lesson #25 / #52 to Turtle Soup / failed-breakdown
reversal: in policy-driven single-country EM ETFs, short-horizon
reversal structures (BB Squeeze, BB Lower, Stoch crossover, failed
breakdown reclaim) all fail. FXI-005's PB+WR+ClosePos+ATR remains
global-optimum.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI009Config(ExperimentConfig):
    """FXI-009 Failed Breakdown Reversal parameters"""

    # Failed-breakdown parameters
    breakdown_lookback: int = 10  # prior N-day low reference (Att3: 5 -> 10)
    breakdown_depth_pct: float = 0.01  # Att3: require Low <= RefLow * (1 - this)
    bullish_close_required: bool = True  # require Close > Open on reclaim day

    # Pullback depth filter (crash isolation only; Att2 drops lower floor)
    pullback_lookback: int = 20
    pullback_threshold: float = 0.0  # Att2: no depth floor (was -0.03)
    pullback_cap: float = -0.12  # cap at -12% (crash isolation)

    # Williams %R oversold gate
    wr_period: int = 10
    wr_threshold: float = -80.0

    # Close position filter (Att2 addition: reversal-day quality)
    close_position_threshold: float = 0.4

    # Cooldown
    cooldown_days: int = 10


def create_default_config() -> FXI009Config:
    return FXI009Config(
        name="fxi_009_failed_breakdown_reversal",
        experiment_id="FXI-009",
        display_name="FXI Failed Breakdown Reversal (Turtle Soup)",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,  # +5.5% (reuse FXI-005 exit)
        stop_loss=-0.050,  # -5.0% (reuse FXI-005 exit)
        holding_days=20,
    )
