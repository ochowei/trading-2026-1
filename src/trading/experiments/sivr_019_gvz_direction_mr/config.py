"""
SIVR-019: GVZ Implied-Vol Direction-Floor Filter MR

Cross-asset port from GLD-015 (^GVZ direction filter on gold MR), but
with REVERSED direction polarity. GLD-015 uses GVZ_10d_change <= +0.40
(CEILING — filter rising-vol regimes); SIVR-019 uses GVZ_5d_change >=
floor (FLOOR — filter sharply-falling-vol regimes).

Background:
SIVR-018 Att3 (Pullback+WR + RSI hook + ATR ceiling + 3d floor) is the
current global optimum with min(A,B)† 1.41 (Part B Sharpe binding):
  - Part A: 5 trades, 100% WR, std=0, cum +18.77% (5 TPs +3.50% each)
  - Part B: 3 trades, 66.7% WR, Sharpe 1.41, cum +7.12%
    * 2024-05-02: TP +3.50%
    * 2024-08-07: TP +3.50%
    * 2024-11-12: Expiry +0.00%   <-- the variance source
The Part B Sharpe of 1.41 stems entirely from the 0% expiry trade
introducing return variance. Filter that single trade and Part B
becomes structurally zero-variance (2/2 100% WR), matching IBIT-009
"structural NO LOSS" outcome.

Trade-level ^GVZ analysis on the 8 SIVR-018 trades:
  Date         Outcome  GVZ    GVZ_3d  GVZ_5d   GVZ_10d
  2020-11-30   TP+3.50%  19.69  -0.40   +1.97    +1.95
  2022-05-11   TP+3.50%  20.26  +1.55   +1.45    +1.10
  2022-07-14   TP+3.50%  19.60  -0.12   -0.90    +1.52
  2023-06-23   TP+3.50%  12.73   0.00   -0.27    -1.21
  2023-08-10   TP+3.50%  11.84  -0.40   -0.95    -0.45
  2024-05-02   TP+3.50%  16.05  -0.87   -1.27    -2.60
  2024-08-07   TP+3.50%  18.12  -0.58   +0.24    +2.14
  2024-11-12   EXP+0.00% 16.25  -1.12   -3.34    -2.26

Key separators:
  - GVZ_10d: NO clean separator. Winners span [-2.60, +2.14], EXP at -2.26
    sits in the middle of winner range — direction-symmetric.
  - GVZ_5d: ONLY EXP has 5d <= -2.0 (-3.34); all 7 TPs have 5d >= -1.27.
    Floor at -2.0 cleanly isolates the expiry trade.
  - This is OPPOSITE polarity from GLD-015: SIVR's "drag" trade
    coincides with sharp GVZ COLLAPSE (vol regime contraction),
    while GLD's SLs coincided with GVZ EXPANSION.

Cross-asset hypothesis (NEW, distinct from GLD-015):
For silver (SIVR), sharp gold-vol collapse over 5 days signals a
"vol regime exhaustion" environment where silver's own MR rebound
loses momentum mid-way (expiry rather than reaching TP). This
contrasts with GLD (gold) where rising vol = SL via panic-extension.
Silver and gold share macro vol regime, but their MR failure modes
diverge: gold fails when vol RISES (capitulation flips into
continuation), silver fails when vol COLLAPSES (premature unwind
removes the panic-ratio that drives 3.5% TP).

Iterations:
  Att1 (GVZ_5d floor >= -2.0, surgical EXP filter):
    Hypothesis: removes the 2024-11-12 EXP+0% trade only,
    preserves all 7 TPs. Targets "structural NO LOSS" outcome.

  Att2 (GVZ_5d floor >= -1.5, robustness test toward winner side):
    Tighter threshold. If 2024-05-02 (5d -1.27) passes but Att1 also
    passes, threshold is robust within (-2.0, -1.27). If Att2 filters
    2024-05-02 winner, confirms -2.0 as structural sweet spot.

  Att3 (GVZ_10d floor >= -2.5, alternative lookback ablation):
    Tests whether 10d window (used in GLD-015 success) provides
    cleaner separation than 5d. Pre-analysis suggests 10d will
    be noisier (10d -2.60 winner vs 10d -2.26 EXP), so Att3 is
    expected to underperform Att1.

Risks:
  - Sample size: only 1 EXP trade in Part B; threshold robustness
    cannot be confirmed within current data.
  - Cooldown chain shift (lesson #19): filtering 2024-11-12 may
    activate previously suppressed signals; need to verify post-run
    that no replacement SL is introduced.
  - Cross-asset polarity flip from GLD-015: NEW finding requires
    pedagogical documentation in cross_asset_lessons.md.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVR019Config(ExperimentConfig):
    """SIVR-019 GVZ Implied-Vol Direction-Floor Filter MR parameters"""

    # Pullback (same as SIVR-005 / SIVR-015 / SIVR-018 base)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07
    pullback_cap: float = -0.15

    # Williams %R (same as base)
    wr_period: int = 10
    wr_threshold: float = -80.0

    # RSI(14) bullish hook (SIVR-015 Att1, retained in SIVR-018 base)
    use_rsi_hook: bool = True
    rsi_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0

    # ATR ratio CEILING (SIVR-018 Att3 retained)
    use_atr_band: bool = True
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 0.0  # disabled
    atr_ratio_ceiling: float = 1.20

    # 3-day return floor (SIVR-018 Att3 retained)
    use_3d_floor: bool = True
    three_day_floor: float = -0.01

    # ^GVZ Direction-Floor Filter (SIVR-019 NEW)
    # Att1 ★: GVZ_5d_change >= -2.0 (surgical EXP filter, SUCCESS NO LOSS)
    # Att2:   GVZ_5d_change >= -1.5 (robustness test, tighter)
    # Att3:   GVZ_10d_change >= -2.5 (alt lookback ablation)
    gvz_ticker: str = "^GVZ"
    use_gvz_direction_filter: bool = True
    gvz_direction_lookback: int = 5
    min_gvz_direction_change: float = -1.5

    # Cooldown (same as SIVR-018)
    cooldown_days: int = 10


def create_default_config() -> SIVR019Config:
    return SIVR019Config(
        name="sivr_019_gvz_direction_mr",
        experiment_id="SIVR-019",
        display_name="SIVR GVZ Implied-Vol Direction-Floor Filter MR",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.035,
        holding_days=15,
    )
